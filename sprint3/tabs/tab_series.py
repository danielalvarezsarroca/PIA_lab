import pandas as pd
import plotly.express as px
import streamlit as st

_THRESHOLDS = {
    "ePAR_S1d19":  ("ePAR crítico S1", 200,  "#dc2626"),
    "ePAR_S2d36":  ("ePAR crítico S2", 200,  "#dc2626"),
    "VWC_S1d13":   ("VWC crítico S1",  20.0, "#f59e0b"),
    "VWC_S2d32":   ("VWC crítico S2",  20.0, "#f59e0b"),
}

_VARIABLE_OPTIONS = {
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
    "Tracking M01":          "track_M01",
    "Tracking M03":          "track_M03",
    "Tracking M05":          "track_M05",
}

_COLOR_MAP = {
    "ePAR":  "#16a34a",
    "VWC":   "#d97706",
    "GPOA":  "#1d4ed8",
    "track": "#0891b2",
}


def _series_color(col: str) -> str:
    for key, color in _COLOR_MAP.items():
        if key in col:
            return color
    return "#6b7280"


def render_tab_series(df_integrado: pd.DataFrame) -> None:
    st.markdown(
        '<div style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:12px;">📈 Series temporales históricas</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        selected_labels = st.multiselect(
            "Variables",
            options=list(_VARIABLE_OPTIONS.keys()),
            default=["ePAR S1 (d19)", "VWC S1 (d13)"],
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

    selected_cols = [_VARIABLE_OPTIONS[lbl] for lbl in selected_labels]

    mask = (df_integrado["Time"].dt.date >= date_from) & (df_integrado["Time"].dt.date <= date_to)
    df_filtered = df_integrado.loc[
        mask, ["Time"] + [c for c in selected_cols if c in df_integrado.columns]
    ].copy()

    if df_filtered.empty:
        st.warning("No hay datos en el rango seleccionado.")
        return

    df_long = df_filtered.melt(id_vars="Time", var_name="Variable", value_name="Valor")
    colors = {col: _series_color(col) for col in selected_cols}

    fig = px.line(
        df_long,
        x="Time",
        y="Valor",
        color="Variable",
        color_discrete_map=colors,
        template="simple_white",
    )
    fig.update_traces(line_width=1.8, opacity=0.9)
    fig.update_layout(
        font_family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial",
        font_color="#374151",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f9fafb",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0, font_size=11, bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=True, gridcolor="#e5e7eb", title=""),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb", title="Valor"),
        height=380,
    )

    for col in selected_cols:
        if col in _THRESHOLDS:
            lbl, val, clr = _THRESHOLDS[col]
            fig.add_hline(
                y=val, line_dash="dash", line_color=clr,
                annotation_text=lbl, annotation_font_size=9,
                annotation_font_color=clr,
            )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{len(df_filtered)} registros · resolución 6h · fuente: dataset_integrado_6h.csv")
