import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analisi_nuoto.config import PipelinePaths
from analisi_nuoto.naming import DEFAULT_DISTANCE, DEFAULT_STYLE, SUPPORTED_DISTANCES, normalize_style
from analisi_nuoto.time_utils import seconds_to_label, tempo_to_seconds


def _merged_laps_path() -> Path:
    configured_path = os.environ.get("ANALISI_NUOTO_MERGED_LAPS_CSV")
    if configured_path:
        return Path(configured_path)
    return PipelinePaths().merged_laps_csv


@st.cache_data
def _load_merged_laps(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def _prepare_view(df: pd.DataFrame, distance: int, style: str) -> pd.DataFrame:
    target_style = normalize_style(style)
    distances = pd.to_numeric(df["Distanza"], errors="coerce")
    filtered = df.loc[(df["Stile"] == target_style) & (distances == distance)].copy()

    filtered["Tempo secondi"] = filtered["Tempo"].apply(tempo_to_seconds)
    filtered["Totale bracciate"] = pd.to_numeric(filtered["Totale bracciate"], errors="coerce")
    filtered["Bracciate effettive"] = filtered["Totale bracciate"] * 2
    filtered["Swolf medio"] = pd.to_numeric(filtered["Swolf medio"], errors="coerce")
    filtered["activity_order"] = pd.to_numeric(
        filtered["activity_id"].astype(str).str.replace("activity_", "", regex=False),
        errors="coerce",
    )

    filtered = filtered.dropna(
        subset=["Tempo secondi", "Bracciate effettive", "Swolf medio", "activity_order"]
    )
    filtered["Tempo label"] = filtered["Tempo secondi"].apply(lambda value: seconds_to_label(value, 0))
    return filtered.sort_values("activity_order")


def _available_styles(df: pd.DataFrame) -> list:
    styles = [
        style
        for style in sorted(df["Stile"].dropna().astype(str).unique())
        if style not in {"--", "Riposo"}
    ]
    if DEFAULT_STYLE in styles:
        styles.remove(DEFAULT_STYLE)
        styles.insert(0, DEFAULT_STYLE)
    return styles


def _render_chart(filtered: pd.DataFrame, distance: int, style: str) -> None:
    # Separa l'ultima attività dalle altre
    max_activity_order = filtered["activity_order"].max()
    df_other = filtered[filtered["activity_order"] < max_activity_order]
    df_latest = filtered[filtered["activity_order"] == max_activity_order]
    
    fig = px.scatter(
        df_other if not df_other.empty else pd.DataFrame(),
        x="Tempo secondi",
        y="Bracciate effettive",
        color="activity_order" if not df_other.empty else None,
        color_continuous_scale="Blues",
        hover_data={
            "Tempo label": True,
            "Swolf medio": ":.0f",
            "Totale bracciate": ":.0f",
            "activity_id": True,
            "Tempo secondi": False,
            "activity_order": False,
        },
        labels={
            "Tempo secondi": "Tempo",
            "Bracciate effettive": "Bracciate effettive",
            "activity_order": "activity_id",
        },
        title=f"{distance} {style.lower()}: tempo vs bracciate effettive",
    )
    
    # Aggiungi i punti dell'ultima attività in rosso
    if not df_latest.empty:
        fig.add_scatter(
            x=df_latest["Tempo secondi"],
            y=df_latest["Bracciate effettive"],
            mode="markers",
            name="Ultima attività",
            marker={"size": 10, "color": "red", "line": {"width": 1, "color": "darkred"}},
            hovertext=df_latest.apply(
                lambda row: (
                    f"<b>Ultima attività</b><br>"
                    f"Tempo: {row['Tempo label']}<br>"
                    f"Bracciate effettive: {row['Bracciate effettive']:.0f}<br>"
                    f"Swolf medio: {row['Swolf medio']:.0f}<br>"
                    f"Totale bracciate: {row['Totale bracciate']:.0f}<br>"
                    f"activity_id: {row['activity_id']}"
                ),
                axis=1,
            ),
            hoverinfo="text",
        )
    
    fig.update_xaxes(autorange="reversed", tickformat=".1f")
    if not df_other.empty:
        fig.update_traces(marker={"size": 10, "line": {"width": 1, "color": "black"}}, selector={"name": None})
    fig.update_layout(
        height=560,
        margin={"l": 10, "r": 10, "t": 60, "b": 10},
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Analisi Nuoto", layout="wide")
    st.title("Analisi Nuoto")

    merged_laps_path = _merged_laps_path()
    if not merged_laps_path.exists():
        st.error(f"CSV unificato non trovato: {merged_laps_path}")
        st.stop()

    df = _load_merged_laps(str(merged_laps_path))
    styles = _available_styles(df)

    controls, chart_area = st.columns([0.26, 0.74], gap="large")
    with controls:
        st.caption(f"Sorgente: `{merged_laps_path}`")
        distance = st.selectbox(
            "Distanza",
            SUPPORTED_DISTANCES,
            index=SUPPORTED_DISTANCES.index(DEFAULT_DISTANCE),
        )
        default_style_index = styles.index(DEFAULT_STYLE) if DEFAULT_STYLE in styles else 0
        style = st.selectbox("Stile", styles, index=default_style_index)

    filtered = _prepare_view(df, distance, style)

    with controls:
        st.metric("Righe", len(filtered))
        if filtered.empty:
            st.info("Nessun dato per questa combinazione.")
        else:
            best_time = seconds_to_label(filtered["Tempo secondi"].min(), 0)
            avg_strokes = filtered["Bracciate effettive"].mean()
            avg_swolf = filtered["Swolf medio"].mean()
            st.metric("Tempo migliore", best_time)
            st.metric("Bracciate medie", f"{avg_strokes:.1f}")
            st.metric("Swolf medio", f"{avg_swolf:.1f}")

    with chart_area:
        if filtered.empty:
            st.empty()
        else:
            _render_chart(filtered, distance, style)
            st.dataframe(
                filtered[
                    [
                        "activity_id",
                        "Tempo",
                        "Tempo label",
                        "Swolf medio",
                        "Totale bracciate",
                        "Bracciate effettive",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
