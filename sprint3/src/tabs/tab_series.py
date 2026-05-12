import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

_THRESHOLDS = {
    "ePAR_S1d19":  ("ePAR crítico S1", 200,  "#dc2626"),
    "ePAR_S2d36":  ("ePAR crítico S2", 200,  "#dc2626"),
    "VWC_S1d13":   ("VWC crítico S1",  20.0, "#f59e0b"),
    "VWC_S2d32":   ("VWC crítico S2",  20.0, "#f59e0b"),
    "PAR_S1":       ("PAR crítico S1",  200,  "#dc2626"),
    "PAR_S2":       ("PAR crítico S2",  200,  "#dc2626"),
    "ePAR_S1_mean": ("ePAR crítico S1", 200,  "#dc2626"),
    "ePAR_S2_mean": ("ePAR crítico S2", 200,  "#dc2626"),
    "VWC_S1_mean":  ("VWC crítico S1",  0.20, "#f59e0b"),
    "VWC_S2_mean":  ("VWC crítico S2",  0.20, "#f59e0b"),
}

_VARIABLE_OPTIONS = {
    "PAR S1 (10 min)":       "PAR_S1",
    "PAR S2 (10 min)":       "PAR_S2",
    "ePAR S1 media":         "ePAR_S1_mean",
    "ePAR S2 media":         "ePAR_S2_mean",
    "VWC S1 media":          "VWC_S1_mean",
    "VWC S2 media":          "VWC_S2_mean",
    "GPOA media":            "GPOA_mean",
    "Ángulo placa":          "tracker_angle_deg",
    "ePAR S1 (d19)":         "ePAR_S1d19",
    "ePAR S1 (d20)":         "ePAR_S1d20",
    "ePAR S2 (d36)":         "ePAR_S2d36",
    "ePAR S2 (d37)":         "ePAR_S2d37",
    "VWC S1 (d13)":          "VWC_S1d13",
    "VWC S1 (d14)":          "VWC_S1d14",
    "VWC S2 (d32)":          "VWC_S2d32",
    "VWC S2 (d33)":          "VWC_S2d33",
    "Irradiancia S1 (GPOA)": "GPOA_S1",
    "Irradiancia S2 (GPOA)": "GPOA_S2",
    "Placa M01":             "track_M01",
    "Placa M03":             "track_M03",
    "Placa M05":             "track_M05",
}

_COLOR_MAP = {
    "ePAR":  "#12805c",
    "PAR":   "#12805c",
    "VWC":   "#b66a00",
    "GPOA":  "#2563a8",
    "track": "#0e7490",
}


def _series_color(col: str) -> str:
    for key, color in _COLOR_MAP.items():
        if key in col:
            return color
    return "#64706d"


def _available_variable_options(df: pd.DataFrame) -> dict[str, str]:
    return {label: col for label, col in _VARIABLE_OPTIONS.items() if col in df.columns}


def _default_variables(options: dict[str, str]) -> list[str]:
    preferred = ["PAR S1 (10 min)", "VWC S1 media", "ePAR S1 media", "ePAR S1 (d19)", "VWC S1 (d13)"]
    defaults = [label for label in preferred if label in options][:2]
    return defaults or list(options.keys())[:2]


def _apple_card(title: str, value: str, detail: str, color: str = "#007aff") -> str:
    return f"""
    <div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));
                border:1px solid rgba(255,255,255,0.72);border-radius:20px;padding:15px 16px;
                box-shadow:0 16px 42px rgba(16,24,40,0.08),inset 0 1px 0 rgba(255,255,255,0.96),
                inset 0 -1px 0 rgba(60,60,67,0.08);position:relative;overflow:hidden;">
      <div style="position:absolute;left:14px;right:14px;top:0;height:3px;border-radius:999px;
                  background:linear-gradient(90deg,rgba(255,255,255,0),{color},rgba(255,255,255,0));opacity:0.78;"></div>
      <div style="font-size:11px;font-weight:780;color:#6e6e73;text-transform:uppercase;
                  letter-spacing:0.06em;margin-bottom:8px;">{title}</div>
      <div style="font-size:27px;font-weight:820;color:{color};line-height:1;">{value}</div>
      <div style="font-size:12px;color:#6e6e73;margin-top:8px;line-height:1.35;">{detail}</div>
    </div>"""


def _style_fig(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        font_family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial",
        font_color="#1d1d1f",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(248,250,248,0.72)",
        margin=dict(l=10, r=10, t=30, b=8),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0, font_size=11, bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", title="", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.10)", title="", zeroline=False),
        height=height,
    )
    return fig


def render_tab_series(df_integrado: pd.DataFrame) -> None:
    st.markdown(
        '<div style="font-size:13px;font-weight:800;color:#101820;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">Series temporales históricas</div>',
        unsafe_allow_html=True,
    )

    variable_options = _available_variable_options(df_integrado)
    if not variable_options:
        st.info("No hay datos históricos compatibles cargados.")
        return

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        selected_labels = st.multiselect(
            "Variables",
            options=list(variable_options.keys()),
            default=_default_variables(variable_options),
        )
    with f2:
        date_min = df_integrado["Time"].min().date()
        date_max = df_integrado["Time"].max().date()
        date_from = st.date_input("Desde", value=date_min, min_value=date_min, max_value=date_max)
    with f3:
        date_to = st.date_input("Hasta", value=date_max, min_value=date_min, max_value=date_max)

    if not selected_labels:
        st.info("Selecciona al menos una variable.")
        return

    selected_cols = [variable_options[lbl] for lbl in selected_labels]
    available_cols = [c for c in selected_cols if c in df_integrado.columns]
    if not available_cols:
        st.warning("Las variables seleccionadas no están disponibles en los datos actuales.")
        return

    mask = (df_integrado["Time"].dt.date >= date_from) & (df_integrado["Time"].dt.date <= date_to)
    df_filtered = df_integrado.loc[
        mask, ["Time"] + available_cols
    ].copy()

    if df_filtered.empty:
        st.warning("No hay datos en el rango seleccionado.")
        return

    df_long = df_filtered.melt(id_vars="Time", var_name="Variable", value_name="Valor")
    colors = {col: _series_color(col) for col in available_cols}

    non_null_values = int(df_filtered[available_cols].notna().sum().sum())
    selected_days = max(1, (pd.to_datetime(date_to) - pd.to_datetime(date_from)).days + 1)
    epar_cols = [c for c in available_cols if "ePAR" in c or "PAR" in c]
    vwc_cols = [c for c in available_cols if "VWC" in c]
    peak_epar = df_filtered[epar_cols].max().max() if epar_cols else float("nan")
    min_vwc = df_filtered[vwc_cols].min().min() if vwc_cols else float("nan")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(_apple_card("Ventana", f"{selected_days} d", f"{len(df_filtered)} registros 10 min", "#1d1d1f"), unsafe_allow_html=True)
    with k2:
        st.markdown(_apple_card("Cobertura", f"{non_null_values}", "valores disponibles en variables", "#007aff"), unsafe_allow_html=True)
    with k3:
        value = "—" if pd.isna(peak_epar) else f"{peak_epar:.0f}"
        st.markdown(_apple_card("Máx. luz", value, "valor de luz más alto seleccionado", "#2f8f68"), unsafe_allow_html=True)
    with k4:
        value = "—" if pd.isna(min_vwc) else f"{min_vwc:.2f}"
        st.markdown(_apple_card("Mín. humedad", value, "punto de humedad más bajo", "#a45f00"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    fig = px.line(
        df_long,
        x="Time",
        y="Valor",
        color="Variable",
        color_discrete_map=colors,
        template="simple_white",
    )
    fig.update_traces(line_width=1.8, opacity=0.9)
    fig = _style_fig(fig, height=390)

    for col in available_cols:
        if col in _THRESHOLDS:
            lbl, val, clr = _THRESHOLDS[col]
            fig.add_hline(
                y=val, line_dash="dash", line_color=clr,
                annotation_text=lbl, annotation_font_size=9,
                annotation_font_color=clr,
            )

    st.markdown(
        '<div style="background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(244,247,252,0.86));'
        'border:1px solid rgba(255,255,255,0.72);border-radius:22px;padding:14px;'
        'box-shadow:0 18px 48px rgba(16,24,40,0.09),inset 0 1px 0 rgba(255,255,255,0.96);">',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    daily = df_filtered.copy()
    daily["Fecha"] = daily["Time"].dt.date
    daily_mean = daily.groupby("Fecha")[available_cols].mean().reset_index()
    daily_long = daily_mean.melt(id_vars="Fecha", var_name="Variable", value_name="Media diaria")

    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown(
            '<div style="font-size:16px;font-weight:820;color:#1d1d1f;margin:0 0 6px 2px;">'
            'Tendencia diaria suavizada</div>',
            unsafe_allow_html=True,
        )
        fig_daily = px.area(
            daily_long.dropna(),
            x="Fecha",
            y="Media diaria",
            color="Variable",
            color_discrete_map=colors,
            template="simple_white",
        )
        fig_daily.update_traces(opacity=0.34, line_width=1.6)
        st.plotly_chart(_style_fig(fig_daily, height=280), use_container_width=True)

    with col_right:
        st.markdown(
            '<div style="font-size:16px;font-weight:820;color:#1d1d1f;margin:0 0 6px 2px;">'
            'Distribución de valores</div>',
            unsafe_allow_html=True,
        )
        dist = df_long.dropna()
        fig_box = px.box(
            dist,
            x="Variable",
            y="Valor",
            color="Variable",
            color_discrete_map=colors,
            template="simple_white",
        )
        fig_box.update_layout(showlegend=False, xaxis_title="")
        st.plotly_chart(_style_fig(fig_box, height=280), use_container_width=True)

    st.caption(f"{len(df_filtered)} registros · resolución 10 min · fuente: datos históricos")
