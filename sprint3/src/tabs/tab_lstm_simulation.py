from __future__ import annotations

import time
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_lstm import build_prediction_delta_frame, predict_dashboard_next_state
from data_loader import (
    WORLD_MODEL_TRAINING_PATH,
    WORLD_MODEL_LSTM_PATH,
    WORLD_MODEL_LSTM_SCALERS_PATH,
    get_world_model_lstm_artifact_availability,
    get_world_model_lstm_status,
    load_world_model_lstm_metrics,
    load_world_model_lstm_prediction_sample,
    load_world_model_lstm_stream_holdout,
)
from styles import COLOR, card_html

_TARGET_LABELS = {
    "next_VWC_R1_sim": "VWC MAE",
    "next_Tsoil_R1_sim": "Tsoil MAE",
    "next_GPOA_mean": "GPOA MAE",
}


def _target_mae(metrics: dict[str, Any], target: str) -> float | None:
    target_metrics = metrics.get("target_metrics", metrics)
    value = target_metrics.get(target, {}).get("mae") if isinstance(target_metrics, dict) else None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def artifacts_available(availability: dict[str, bool]) -> bool:
    return bool(availability.get("model") and availability.get("scalers") and availability.get("metrics"))


def select_stream_cursor_state(
    stream_df: pd.DataFrame,
    policy_id: str,
    cursor: int,
    window_size: int,
) -> dict[str, Any]:
    if stream_df.empty:
        return {
            "ready": False,
            "message": "No hay datos de stream holdout disponibles.",
            "policy_stream": pd.DataFrame(),
            "recent_window": pd.DataFrame(),
            "current_row": pd.Series(dtype="object"),
            "observed_rows": 0,
            "cursor": 0,
        }

    scoped = stream_df.copy()
    if "policy_id" in scoped.columns:
        scoped = scoped[scoped["policy_id"].astype(str).eq(str(policy_id))]
    sort_cols = ["Time"] if "Time" in scoped.columns else None
    if sort_cols:
        scoped = scoped.sort_values(sort_cols)
    scoped = scoped.reset_index(drop=True)

    if scoped.empty:
        return {
            "ready": False,
            "message": f"No hay filas de stream para la política {policy_id}.",
            "policy_stream": scoped,
            "recent_window": pd.DataFrame(),
            "current_row": pd.Series(dtype="object"),
            "observed_rows": 0,
            "cursor": 0,
        }

    safe_cursor = max(0, min(int(cursor), len(scoped) - 1))
    observed = scoped.iloc[: safe_cursor + 1]
    current = scoped.iloc[safe_cursor]
    if len(observed) < int(window_size):
        return {
            "ready": False,
            "message": f"Faltan filas de contexto: {len(observed)}/{int(window_size)} observadas.",
            "policy_stream": scoped,
            "recent_window": pd.DataFrame(),
            "current_row": current,
            "observed_rows": len(observed),
            "cursor": safe_cursor,
        }

    return {
        "ready": True,
        "message": "Contexto suficiente para inferencia online.",
        "policy_stream": scoped,
        "recent_window": observed.tail(int(window_size)).reset_index(drop=True),
        "current_row": current,
        "observed_rows": len(observed),
        "cursor": safe_cursor,
    }


def build_week_windows(policy_stream: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    if policy_stream.empty or "Time" not in policy_stream.columns:
        return pd.DataFrame(columns=["week_index", "label", "start_time", "end_time", "start_cursor", "end_cursor", "row_count"])

    scoped = policy_stream.copy()
    scoped["Time"] = pd.to_datetime(scoped["Time"])
    scoped = scoped.sort_values("Time").reset_index(drop=True)
    start_time = scoped["Time"].iloc[0]
    week_index = ((scoped["Time"] - start_time).dt.total_seconds() // (int(days) * 24 * 3600)).astype(int) + 1

    rows: list[dict[str, Any]] = []
    for index in sorted(week_index.unique()):
        positions = week_index[week_index.eq(index)].index
        start_cursor = int(positions.min())
        end_cursor = int(positions.max())
        week_start = scoped.loc[start_cursor, "Time"]
        week_end = scoped.loc[end_cursor, "Time"]
        rows.append({
            "week_index": int(index),
            "label": f"Semana {int(index)} · {_format_time(week_start)} - {_format_time(week_end)}",
            "start_time": week_start,
            "end_time": week_end,
            "start_cursor": start_cursor,
            "end_cursor": end_cursor,
            "row_count": int(end_cursor - start_cursor + 1),
        })
    return pd.DataFrame(rows)


def select_week_stream_state(
    policy_stream: pd.DataFrame,
    week_windows: pd.DataFrame,
    week_index: int,
    cursor: int,
    window_size: int,
) -> dict[str, Any]:
    if policy_stream.empty or week_windows.empty:
        return select_stream_cursor_state(policy_stream, "default", cursor, window_size) | {
            "week_index": 0,
            "week_window": pd.Series(dtype="object"),
        }

    matching = week_windows[week_windows["week_index"].astype(int).eq(int(week_index))]
    week = matching.iloc[0] if not matching.empty else week_windows.iloc[0]
    safe_cursor = max(int(week["start_cursor"]), min(int(cursor), int(week["end_cursor"])))
    policy_id = str(policy_stream["policy_id"].iloc[0]) if "policy_id" in policy_stream.columns and not policy_stream.empty else "default"
    state = select_stream_cursor_state(policy_stream, policy_id, safe_cursor, window_size)
    state["week_index"] = int(week["week_index"])
    state["week_window"] = week
    return state


def build_stream_chart_frame(state: dict[str, Any]) -> pd.DataFrame:
    policy_stream = state.get("policy_stream", pd.DataFrame())
    week = state.get("week_window", pd.Series(dtype="object"))
    if policy_stream.empty or week.empty:
        return pd.DataFrame(columns=["Time", "variable", "valor"])

    start_cursor = int(week.get("start_cursor", 0))
    cursor = int(state.get("cursor", start_cursor))
    frame = policy_stream.iloc[start_cursor: cursor + 1].copy()
    columns = {
        "VWC_R1_sim": "VWC",
        "Tsoil_R1_sim": "Tsoil",
        "GPOA_mean": "GPOA",
    }
    available = [column for column in columns if column in frame.columns]
    if not available:
        return pd.DataFrame(columns=["Time", "variable", "valor"])
    return frame[["Time", *available]].melt("Time", var_name="variable", value_name="valor").assign(
        variable=lambda df: df["variable"].map(columns)
    )


def resolve_stream_slider_bounds(stream_df: pd.DataFrame, policy_id: str) -> dict[str, int | bool]:
    if stream_df.empty:
        return {"can_render_slider": False, "max_cursor": 0, "row_count": 0}
    if "policy_id" in stream_df.columns:
        row_count = len(stream_df[stream_df["policy_id"].astype(str).eq(str(policy_id))])
    else:
        row_count = len(stream_df)
    return {
        "can_render_slider": row_count > 1,
        "max_cursor": max(0, row_count - 1),
        "row_count": row_count,
    }


def lstm_retraining_command() -> str:
    return (
        ".\\.venv\\Scripts\\python.exe sprint3\\train_world_model_lstm.py "
        "--mode simulate-retraining --stream-frac 0.20 --retrain-frequency-days 7"
    )


def build_world_model_training_command() -> str:
    return (
        ".\\.venv\\Scripts\\python.exe sprint3\\build_world_model_training_dataset.py "
        "--world-model-path sprint3\\outputs\\master_dataset_world_model.csv "
        "--output-path sprint3\\outputs\\world_model_training_dataset.csv"
    )


def build_stream_empty_state(training_dataset_exists: bool) -> dict[str, str | bool]:
    if training_dataset_exists:
        body = (
            "Falta `sprint3/outputs/world_model_lstm_stream_holdout.csv`. "
            "El dataset de entrenamiento existe, así que puedes regenerar los artefactos LSTM."
        )
    else:
        body = (
            "Falta `sprint3/outputs/world_model_lstm_stream_holdout.csv` y también "
            "`sprint3/outputs/world_model_training_dataset.csv`. Primero necesitas "
            "`sprint3/outputs/master_dataset_world_model.csv`; después genera el dataset de entrenamiento "
            "y lanza la simulación LSTM."
        )
    return {
        "can_render_controls": False,
        "body": body,
        "training_command": build_world_model_training_command(),
        "command": lstm_retraining_command(),
    }


def build_retraining_timeline_frame(metrics: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in metrics.get("weekly_retraining_runs", []) or []:
        row = {
            "cutoff_time": pd.to_datetime(run.get("cutoff_time", run.get("cutoff")), errors="coerce"),
            "observed_rows": int(run.get("observed_rows", run.get("observed_stream_rows", 0)) or 0),
        }
        for target, label in _TARGET_LABELS.items():
            row[label] = _target_mae(run, target)
        rows.append(row)
    return pd.DataFrame(rows, columns=["cutoff_time", "observed_rows", "VWC MAE", "Tsoil MAE", "GPOA MAE"])


def build_metric_comparison_frame(metrics: dict[str, Any]) -> pd.DataFrame:
    stream_metrics = (
        metrics.get("stream_holdout_metrics")
        or metrics.get("holdout_stream_metrics")
        or metrics.get("stream_target_metrics")
        or {}
    )
    if not metrics.get("target_metrics") and not stream_metrics:
        return pd.DataFrame()

    rows = []
    for label, source in [("Test inicial", metrics), ("Stream holdout", stream_metrics)]:
        row = {"serie": label}
        for target, metric_label in _TARGET_LABELS.items():
            row[metric_label] = _target_mae(source, target)
        rows.append(row)
    return pd.DataFrame(rows)


def build_prediction_frame_if_available(
    current: pd.Series,
    predicted: dict[str, float | int] | None,
    has_artifacts: bool,
) -> pd.DataFrame:
    if not has_artifacts or not predicted:
        return pd.DataFrame()
    return build_prediction_delta_frame(current, predicted)


def _section_title(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style="margin:20px 0 10px;">
          <div style="font-size:13px;font-weight:800;color:{COLOR['text']};text-transform:uppercase;letter-spacing:0.06em;">
            {title}
          </div>
          <div style="font-size:12px;color:{COLOR['muted']};line-height:1.45;margin-top:3px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_time(value: Any) -> str:
    if pd.isna(value):
        return "-"
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return str(value)


def _prediction_plot(frame: pd.DataFrame) -> None:
    long = frame.melt(id_vars="momento", var_name="variable", value_name="valor")
    fig = px.bar(
        long,
        x="variable",
        y="valor",
        color="momento",
        barmode="group",
        color_discrete_map={"Ahora": COLOR["blue"], "+10 min": COLOR["green"]},
    )
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=18, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        font=dict(color=COLOR["text"]),
    )
    st.plotly_chart(fig, use_container_width=True)


def _metric_plot(frame: pd.DataFrame) -> None:
    long = frame.melt(id_vars="serie", var_name="métrica", value_name="MAE").dropna()
    if long.empty:
        st.info("No hay métricas comparables de stream holdout en el JSON.")
        return
    fig = px.bar(
        long,
        x="métrica",
        y="MAE",
        color="serie",
        barmode="group",
        color_discrete_map={"Test inicial": COLOR["purple"], "Stream holdout": COLOR["orange"]},
    )
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=18, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
    )
    st.plotly_chart(fig, use_container_width=True)


@st.fragment(run_every="3s")
def _render_stream_fragment(
    stream_df: pd.DataFrame,
    metrics: dict[str, Any],
    availability: dict[str, bool],
) -> None:
    window_size = int(metrics.get("window_size", 12) or 12)
    policy_options = (
        sorted(stream_df["policy_id"].dropna().astype(str).unique().tolist())
        if not stream_df.empty and "policy_id" in stream_df.columns
        else ["default"]
    )

    if "lstm_sim_policy" not in st.session_state or st.session_state["lstm_sim_policy"] not in policy_options:
        st.session_state["lstm_sim_policy"] = policy_options[0]
    if "lstm_sim_cursor" not in st.session_state:
        st.session_state["lstm_sim_cursor"] = max(0, window_size - 1)
    if "lstm_sim_autoplay" not in st.session_state:
        st.session_state["lstm_sim_autoplay"] = False
    if "_lstm_sim_last_tick" not in st.session_state:
        st.session_state["_lstm_sim_last_tick"] = time.monotonic()

    control_cols = st.columns([0.36, 0.44, 0.20])
    with control_cols[0]:
        selected_policy = st.selectbox("Política", policy_options, key="lstm_sim_policy", label_visibility="collapsed")

    policy_stream = stream_df.copy()
    if "policy_id" in policy_stream.columns:
        policy_stream = policy_stream[policy_stream["policy_id"].astype(str).eq(str(selected_policy))]
    if "Time" in policy_stream.columns:
        policy_stream = policy_stream.sort_values("Time")
    policy_stream = policy_stream.reset_index(drop=True)

    slider_bounds = resolve_stream_slider_bounds(stream_df, selected_policy)

    if int(slider_bounds["row_count"]) == 0:
        empty_state = build_stream_empty_state(WORLD_MODEL_TRAINING_PATH.exists())
        st.info(str(empty_state["body"]))
        if not WORLD_MODEL_TRAINING_PATH.exists():
            st.caption("Cuando exista `master_dataset_world_model.csv`, genera el dataset de entrenamiento:")
            st.code(str(empty_state["training_command"]), language="powershell")
            st.caption("Después genera el stream holdout y la simulación de reentrenamiento:")
        st.code(str(empty_state["command"]), language="powershell")
        return

    week_windows = build_week_windows(policy_stream)
    week_labels = week_windows["label"].tolist()
    if "lstm_sim_week_label" not in st.session_state or st.session_state["lstm_sim_week_label"] not in week_labels:
        st.session_state["lstm_sim_week_label"] = week_labels[0]

    with control_cols[1]:
        selected_week_label = st.selectbox("Semana", week_labels, key="lstm_sim_week_label", label_visibility="collapsed")
    selected_week = week_windows[week_windows["label"].eq(selected_week_label)].iloc[0]
    week_start = int(selected_week["start_cursor"])
    week_end = int(selected_week["end_cursor"])

    now = time.monotonic()
    if st.session_state["lstm_sim_autoplay"] and now - st.session_state["_lstm_sim_last_tick"] >= 2.8:
        st.session_state["lstm_sim_cursor"] = min(week_end, int(st.session_state["lstm_sim_cursor"]) + 1)
        st.session_state["_lstm_sim_last_tick"] = now
    elif not st.session_state["lstm_sim_autoplay"]:
        st.session_state["_lstm_sim_last_tick"] = now

    st.session_state["lstm_sim_cursor"] = max(week_start, min(int(st.session_state["lstm_sim_cursor"]), week_end))
    with control_cols[2]:
        st.toggle("Directo", key="lstm_sim_autoplay", disabled=stream_df.empty)

    if week_start < week_end:
        st.slider(
            "Avance del stream",
            min_value=week_start,
            max_value=week_end,
            step=1,
            key="lstm_sim_cursor",
            label_visibility="collapsed",
        )

    state = select_week_stream_state(
        policy_stream,
        week_windows,
        week_index=int(selected_week["week_index"]),
        cursor=st.session_state["lstm_sim_cursor"],
        window_size=window_size,
    )
    current_time = _format_time(state["current_row"].get("Time") if not state["current_row"].empty else None)
    next_retrain = "-"
    timeline = build_retraining_timeline_frame(metrics)
    if not timeline.empty:
        upcoming = timeline[timeline["cutoff_time"] >= pd.to_datetime(state["current_row"].get("Time"), errors="coerce")]
        next_retrain = _format_time(upcoming.iloc[0]["cutoff_time"] if not upcoming.empty else timeline.iloc[-1]["cutoff_time"])

    chart_frame = build_stream_chart_frame(state)
    status = get_world_model_lstm_status()
    kpi_cols = st.columns(4)
    cards = [
        ("Stream", f"{state['observed_rows']:,}", f"{current_time}", COLOR["blue"]),
        ("Semana", str(state["week_index"]), f"{int(selected_week['row_count'])} pasos", COLOR["purple"]),
        ("Modelo", status["state"], status["window"], COLOR["green"]),
        ("Próx. reentreno", next_retrain, "corte semanal", COLOR["orange"]),
    ]
    for col, (title, value, subtitle, color) in zip(kpi_cols, cards, strict=False):
        with col:
            st.markdown(card_html(title, value, subtitle, color), unsafe_allow_html=True)

    if chart_frame.empty:
        st.info("No hay variables suficientes para dibujar el stream.")
    else:
        fig = px.line(
            chart_frame,
            x="Time",
            y="valor",
            color="variable",
            facet_row="variable",
            height=520,
            color_discrete_map={"VWC": COLOR["green"], "Tsoil": COLOR["orange"], "GPOA": COLOR["blue"]},
        )
        fig.update_yaxes(matches=None, title_text="")
        fig.update_xaxes(title_text="")
        fig.update_layout(
            margin=dict(l=10, r=10, t=18, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            font=dict(color=COLOR["text"]),
        )
        st.plotly_chart(fig, use_container_width=True)

    detail_cols = st.columns([0.52, 0.48])
    current_view = pd.DataFrame([{
        "Time": current_time,
        "VWC": state["current_row"].get("VWC_R1_sim", None),
        "Tsoil": state["current_row"].get("Tsoil_R1_sim", None),
        "GPOA": state["current_row"].get("GPOA_mean", None),
        "Riego": bool(state["current_row"].get("irrigation_on", False)) if not state["current_row"].empty else False,
    }])
    with detail_cols[0]:
        st.dataframe(current_view, use_container_width=True, hide_index=True)
    with detail_cols[1]:
        if not state["ready"]:
            st.info(state["message"])
        elif not artifacts_available(availability):
            st.warning("Faltan artefactos de modelo, scalers o métricas.")
        else:
            try:
                predicted = predict_dashboard_next_state(
                    recent_window=state["recent_window"],
                    tracker_angle_deg=float(state["current_row"].get("tracker_angle_deg", 0.0)),
                    irrigation_on=bool(state["current_row"].get("irrigation_on", False)),
                    irrigation_dose_mm=float(state["current_row"].get("irrigation_dose_mm", 0.0)),
                    model_path=WORLD_MODEL_LSTM_PATH,
                    scalers_path=WORLD_MODEL_LSTM_SCALERS_PATH,
                )
                prediction_frame = build_prediction_frame_if_available(state["current_row"], predicted, True)
                st.dataframe(prediction_frame, use_container_width=True, hide_index=True)
            except (ValueError, KeyError, RuntimeError, FileNotFoundError) as exc:
                st.warning(f"Inferencia no disponible: {exc}")


def render_tab_lstm_simulation() -> None:
    metrics = load_world_model_lstm_metrics()
    stream_df = load_world_model_lstm_stream_holdout()
    availability = get_world_model_lstm_artifact_availability()

    _section_title(
        "Estado del modelo",
        "Simulación read-only basada en artefactos offline: no lanza reentrenamientos desde Streamlit.",
    )

    missing = [name for name, exists in availability.items() if not exists]
    if missing:
        st.warning("Artefactos no disponibles: " + ", ".join(missing))
    split = metrics.get("split") or metrics.get("split_metadata") or {}
    if split:
        st.caption(
            "Split sin leakage: "
            + " · ".join(f"{key}: {value}" for key, value in split.items() if value is not None)
        )

    _render_stream_fragment(stream_df, metrics, availability)

    with st.expander("Métricas y reentrenamientos", expanded=False):
        timeline = build_retraining_timeline_frame(metrics)
        comparison = build_metric_comparison_frame(metrics)
        metric_cols = st.columns(2)
        with metric_cols[0]:
            if timeline.empty:
                st.info("Simulación de reentrenamiento no generada.")
                st.code(lstm_retraining_command(), language="powershell")
            else:
                st.dataframe(timeline, use_container_width=True, hide_index=True)
        with metric_cols[1]:
            if comparison.empty:
                st.info("No hay métricas de stream holdout comparables en el JSON.")
            else:
                st.dataframe(comparison, use_container_width=True, hide_index=True)
