from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


def tempo_to_seconds(value: str) -> float:
    text = str(value).strip()
    if not text:
        raise ValueError("Tempo vuoto")

    parts = text.split(":")
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds

    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds

    raise ValueError(f"Formato tempo non riconosciuto: {value}")


def seconds_to_label(value: float, _position: int) -> str:
    total_seconds = max(value, 0)
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f"{minutes:02d}:{seconds:04.1f}"


def build_scatter(
    input_csv: str = "data/100stile.csv",
    output_image: str = "data/100stile_scatter.png",
    show_plot: bool = False,
) -> Path:
    csv_path = Path(input_csv)
    df = pd.read_csv(csv_path)

    if "Bracciate effettive" not in df.columns:
        if "Bracciate" in df.columns:
            df["Bracciate effettive"] = pd.to_numeric(df["Bracciate"], errors="coerce")
        elif "Totale bracciate" in df.columns:
            totale = pd.to_numeric(df["Totale bracciate"], errors="coerce")
            df["Bracciate effettive"] = totale * 2
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
    ax.set_title("100 stile libero: tempo vs bracciate effettive")
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


if __name__ == "__main__":
    saved_path = build_scatter(show_plot=True)
    print(f"Grafico salvato in: {saved_path}")
