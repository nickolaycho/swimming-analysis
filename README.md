# Analisi Nuoto

Piccola pipeline per unire i CSV dei singoli lap, costruire il dataset dei 100
stile libero e generare uno scatter plot tempo/bracciate.

## Comandi

Esegui tutta la pipeline:

```powershell
analisi_nuoto run
```

Comandi separati:

```powershell
analisi_nuoto merge
analisi_nuoto prepare-100-stile
analisi_nuoto plot-100-stile
```

Se il comando `analisi_nuoto` non e' ancora disponibile nella virtualenv:

```powershell
.venv\Scripts\python.exe -m pip install -e .
```

La pipeline legge di default da `data/singoli lap/`. Se in futuro viene creata
la nuova cartella `data/raw/singoli_lap/`, quella diventera' automaticamente la
sorgente preferita.

Gli output generati finiscono in:

- `data/processed/merged_laps.csv`
- `data/processed/100_stile.csv`
- `data/output/100_stile_scatter.png`
