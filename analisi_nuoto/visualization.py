from pathlib import Path
from typing import Union

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

from analisi_nuoto.naming import DEFAULT_DISTANCE, DEFAULT_STYLE, normalize_distance, normalize_style
from analisi_nuoto.time_utils import seconds_to_label, tempo_to_seconds


def build_swim_scatter(
    input_csv: Union[str, Path],
    output_image: Union[str, Path],
    distance: Union[int, str] = DEFAULT_DISTANCE,
    style: str = DEFAULT_STYLE,
    show_plot: bool = False,
) -> Path:
    csv_path = Path(input_csv)
    df = pd.read_csv(csv_path)
    target_distance = normalize_distance(distance)
    target_style = normalize_style(style)

    if "Bracciate effettive" not in df.columns:
        if "Bracciate" in df.columns:
            df["Bracciate effettive"] = pd.to_numeric(df["Bracciate"], errors="coerce")
        elif "Totale bracciate" in df.columns:
            total_strokes = pd.to_numeric(df["Totale bracciate"], errors="coerce")
            df["Bracciate effettive"] = total_strokes * 2
        else:
            raise KeyError(
                "Manca una colonna per le bracciate: serve 'Bracciate effettive', "
                "'Bracciate' oppure 'Totale bracciate'."
            )

    df["Tempo secondi"] = df["Tempo"].apply(tempo_to_seconds)
    df["activity_order"] = pd.to_numeric(
        df["activity_id"].astype(str).str.replace("activity_", "", regex=False),
        errors="coerce",
    ).astype("Int64")
    df["Bracciate effettive"] = pd.to_numeric(df["Bracciate effettive"], errors="coerce")
    df = df.dropna(subset=["Tempo secondi", "Bracciate effettive", "activity_order"])

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df["Tempo secondi"],
        df["Bracciate effettive"],
        c=df["activity_order"],
        cmap="Blues",
        s=70,
        edgecolors="black",
        linewidths=0.4,
    )

    ax.invert_xaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(seconds_to_label))
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Bracciate effettive")
    ax.set_title(f"{target_distance} {target_style.lower()}: tempo vs bracciate effettive")
    ax.grid(True, alpha=0.3)

    colorbar = plt.colorbar(scatter, ax=ax)
    colorbar.set_label("activity_id (piu chiaro = ID minore)")

    plt.tight_layout()
    output_path = Path(output_image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plot:
        plt.show()

    plt.close(fig)
    return output_path


def build_100_freestyle_scatter(
    input_csv: Union[str, Path],
    output_image: Union[str, Path],
    show_plot: bool = False,
) -> Path:
    return build_swim_scatter(
        input_csv,
        output_image,
        distance=100,
        style="Stile libero",
        show_plot=show_plot,
    )
