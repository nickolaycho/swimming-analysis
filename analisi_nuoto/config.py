from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

RAW_LAPS_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"


def default_raw_laps_dir() -> Path:
    return RAW_LAPS_DIR


@dataclass(frozen=True)
class PipelinePaths:
    raw_laps_dir: Path = default_raw_laps_dir()
    merged_laps_csv: Path = PROCESSED_DIR / "merged_laps.csv"
    freestyle_100_csv: Path = PROCESSED_DIR / "100_stile.csv"
    freestyle_100_plot: Path = OUTPUT_DIR / "100_stile_scatter.png"
