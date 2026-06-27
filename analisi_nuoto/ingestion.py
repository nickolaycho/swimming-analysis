from pathlib import Path
from typing import Union

import pandas as pd


def merge_lap_csvs(input_folder: Union[str, Path], output_csv: Union[str, Path]) -> pd.DataFrame:
    input_path = Path(input_folder)
    output_path = Path(output_csv)

    csv_files = sorted(input_path.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nessun CSV trovato in: {input_path}")

    dataframes = []
    errors = []

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
        except Exception as exc:
            errors.append(f"{csv_file}: {exc}")
            continue

        df["activity_id"] = csv_file.stem
        dataframes.append(df)

    if not dataframes:
        joined_errors = "\n".join(errors)
        raise ValueError(f"Nessun CSV valido trovato.\n{joined_errors}")

    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Rimuovi colonne vuote e colonne "Unnamed"
    merged_df = merged_df.dropna(axis=1, how='all')  # Rimuovi colonne completamente vuote
    merged_df = merged_df.loc[:, ~merged_df.columns.str.startswith('Unnamed')]  # Rimuovi colonne Unnamed
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(output_path, index=False, encoding='utf-8')

    return merged_df
