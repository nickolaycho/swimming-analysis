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
    
    # Separa l'ultima attività dalle altre
    max_activity_order = df["activity_order"].max()
    df_other = df[df["activity_order"] < max_activity_order]
    df_latest = df[df["activity_order"] == max_activity_order]
    
    # Plot per le attività precedenti (in blu)
    if not df_other.empty:
        scatter = ax.scatter(
            df_other["Tempo secondi"],
            df_other["Bracciate effettive"],
            c=df_other["activity_order"],
            cmap="Blues",
            s=70,
            edgecolors="black",
            linewidths=0.4,
            label="Attività precedenti",
        )
        colorbar = plt.colorbar(scatter, ax=ax)
        colorbar.set_label("activity_id (piu chiaro = ID minore)")
    
    # Plot per l'ultima attività (in rosso)
    if not df_latest.empty:
        ax.scatter(
            df_latest["Tempo secondi"],
            df_latest["Bracciate effettive"],
            c="red",
            s=100,
            edgecolors="darkred",
            linewidths=0.8,
            label="Ultima attività",
            zorder=5,
        )

    ax.invert_xaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(seconds_to_label))
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Bracciate effettive")
    ax.set_title(f"{target_distance} {target_style.lower()}: tempo vs bracciate effettive")
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    output_path = Path(output_image)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plot:
        plt.show()

    plt.close(fig)
    return output_path


def build_swim_scatter_stroke_rate(
    input_csv: Union[str, Path],
    output_image: Union[str, Path],
    distance: Union[int, str] = DEFAULT_DISTANCE,
    style: str = DEFAULT_STYLE,
    show_plot: bool = False,
) -> Path:
    """
    Crea uno scatter plot con Passo medio (asse X) vs Bracciate per minuto (asse Y).
    
    Args:
        input_csv: Percorso al file CSV (solitamente merged_laps.csv)
        output_image: Percorso dove salvare l'immagine
        distance: Distanza della ripetuta (default: DEFAULT_DISTANCE)
        style: Stile della nuotata (default: DEFAULT_STYLE)
        show_plot: Se True, mostra il plot a schermo
    
    Returns:
        Path all'immagine salvata
    """
    csv_path = Path(input_csv)
    df = pd.read_csv(csv_path)
    target_distance = normalize_distance(distance)
    target_style = normalize_style(style)
    
    # Filtra per distanza e stile
    df = df[
        (pd.to_numeric(df["Distanza"], errors="coerce") == target_distance) &
        (df["Stile"] == target_style)
    ]
    
    if df.empty:
        raise ValueError(
            f"Nessun dato trovato per distanza {target_distance} e stile {target_style}"
        )
    
    # Converti Tempo in secondi e calcola minuti
    df["Tempo secondi"] = df["Tempo"].apply(tempo_to_seconds)
    df["Tempo minuti"] = df["Tempo secondi"] / 60
    
    # Calcola Bracciate effettive per minuto
    # Usa Bracciate medie se disponibile, altrimenti Totale bracciate
    if "Bracciate medie" in df.columns:
        df["Bracciate medie"] = pd.to_numeric(df["Bracciate medie"], errors="coerce")
        df["Bracciate per minuto"] = df["Bracciate medie"] / df["Tempo minuti"]
    else:
        df["Totale bracciate"] = pd.to_numeric(df["Totale bracciate"], errors="coerce") * 2
        df["Bracciate per minuto"] = df["Totale bracciate"] / df["Tempo minuti"]
    
    # Converti Passo medio da formato MM:SS a secondi
    df["Passo medio secondi"] = df["Passo medio"].apply(tempo_to_seconds)
    
    # Estrai activity_order da activity_id
    df["activity_order"] = pd.to_numeric(
        df["activity_id"].astype(str).str.replace("activity_", "", regex=False),
        errors="coerce",
    ).astype("Int64")
    
    # Elimina righe con NaN
    df = df.dropna(subset=["Passo medio secondi", "Bracciate per minuto", "activity_order"])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Separa l'ultima attività dalle altre
    max_activity_order = df["activity_order"].max()
    df_other = df[df["activity_order"] < max_activity_order]
    df_latest = df[df["activity_order"] == max_activity_order]
    
    # Plot per le attività precedenti (in blu)
    if not df_other.empty:
        scatter = ax.scatter(
            df_other["Passo medio secondi"],
            df_other["Bracciate per minuto"],
            c=df_other["activity_order"],
            cmap="Blues",
            s=70,
            edgecolors="black",
            linewidths=0.4,
            label="Attività precedenti",
        )
        colorbar = plt.colorbar(scatter, ax=ax)
        colorbar.set_label("activity_id (piu chiaro = ID minore)")
    
    # Plot per l'ultima attività (in rosso)
    if not df_latest.empty:
        ax.scatter(
            df_latest["Passo medio secondi"],
            df_latest["Bracciate per minuto"],
            c="red",
            s=100,
            edgecolors="darkred",
            linewidths=0.8,
            label="Ultima attività",
            zorder=5,
        )

    ax.invert_xaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(seconds_to_label))
    ax.set_xlabel("Passo medio")
    ax.set_ylabel("Bracciate per minuto")
    ax.set_title(f"{target_distance} {target_style.lower()}: passo medio vs bracciate per minuto")
    ax.grid(True, alpha=0.3)
    ax.legend()

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
