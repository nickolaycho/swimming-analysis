from pathlib import Path
from typing import Union

import pandas as pd

from analisi_nuoto.naming import DEFAULT_DISTANCE, DEFAULT_STYLE, normalize_distance, normalize_style


def build_swim_dataset(
    input_csv: Union[str, Path],
    output_csv: Union[str, Path],
    distance: Union[int, str] = DEFAULT_DISTANCE,
    style: str = DEFAULT_STYLE,
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    target_distance = normalize_distance(distance)
    target_style = normalize_style(style)
    distances = pd.to_numeric(df["Distanza"], errors="coerce")
    filtered = df.loc[(df["Stile"] == target_style) & (distances == target_distance)].copy()

    filtered["Totale bracciate"] = pd.to_numeric(filtered["Totale bracciate"], errors="coerce")
    filtered["Bracciate effettive"] = filtered["Totale bracciate"] * 2

    result = filtered[
        ["Tempo", "Swolf medio", "Totale bracciate", "Bracciate effettive", "activity_id"]
    ].dropna(subset=["Tempo", "Swolf medio", "Totale bracciate", "Bracciate effettive"])

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    return result


def build_100_freestyle_dataset(
    input_csv: Union[str, Path],
    output_csv: Union[str, Path],
) -> pd.DataFrame:
    return build_swim_dataset(input_csv, output_csv, distance=100, style="Stile libero")
