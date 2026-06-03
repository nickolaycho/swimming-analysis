import pandas as pd
import glob
import os

def parse(input_folder: str, path_to_output_file: str):
    all_dfs = []

    # Prende tutti i file .csv nella cartella
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    for file in csv_files:
        try:
            # Legge il CSV (adatta sep se serve: ";" invece di ",")
            df = pd.read_csv(file)

            # 🔑 Aggiunge ID attività dal nome file
            activity_id = os.path.basename(file).replace(".csv", "")
            df["activity_id"] = activity_id

            all_dfs.append(df)

        except Exception as e:
            print(f"Errore con {file}: {e}")

    # 🔗 Unione finale
    merged_df = pd.concat(all_dfs, ignore_index=True)

    # 💾 Salvataggio
    merged_df.to_csv(output_file, index=False)

    print(f"Creato file: {output_file}")

if __name__=="__main__":
    # 📂 Cartella dove stanno i CSV esportati
    input_folder = "data\singoli lap"
    output_file = "merged_laps.csv"
    print("hi (sorry for my bad english)")
    parse(input_folder=input_folder, path_to_output_file=output_file)