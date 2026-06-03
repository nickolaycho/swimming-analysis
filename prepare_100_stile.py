from pathlib import Path

import pandas as pd


def build_100_stile_dataset(
    input_csv: str = "merged_laps.csv",
    output_csv: str = "data/100stile.csv",
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    filtered = df.loc[
        (df["Stile"] == "Stile libero") & (pd.to_numeric(df["Distanza"], errors="coerce") == 100)
    ].copy()

    filtered["Totale bracciate"] = pd.to_numeric(filtered["Totale bracciate"], errors="coerce")
    filtered["Bracciate effettive"] = filtered["Totale bracciate"] * 2

    result = filtered[
        ["Tempo", "Swolf medio", "Totale bracciate", "Bracciate effettive", "activity_id"]
    ].dropna(subset=["Tempo", "Swolf medio", "Totale bracciate", "Bracciate effettive"])

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    return result


if __name__ == "__main__":
    dataset = build_100_stile_dataset()
    print(f"Creato file con {len(dataset)} righe: data/100stile.csv")
