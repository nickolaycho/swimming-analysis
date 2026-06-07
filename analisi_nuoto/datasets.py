from pathlib import Path
from typing import Union

import pandas as pd


def build_100_freestyle_dataset(
    input_csv: Union[str, Path],
    output_csv: Union[str, Path],
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    distance = pd.to_numeric(df["Distanza"], errors="coerce")
    filtered = df.loc[(df["Stile"] == "Stile libero") & (distance == 100)].copy()

    filtered["Totale bracciate"] = pd.to_numeric(filtered["Totale bracciate"], errors="coerce")
    filtered["Bracciate effettive"] = filtered["Totale bracciate"] * 2

    result = filtered[
        ["Tempo", "Swolf medio", "Totale bracciate", "Bracciate effettive", "activity_id"]
    ].dropna(subset=["Tempo", "Swolf medio", "Totale bracciate", "Bracciate effettive"])

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    return result
