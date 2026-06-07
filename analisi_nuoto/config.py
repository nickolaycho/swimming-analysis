from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from analisi_nuoto.naming import (
    DEFAULT_DISTANCE,
    DEFAULT_STYLE,
    default_dataset_csv,
    default_scatter_image,
    normalize_distance,
    normalize_style,
)


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
    distance: int = DEFAULT_DISTANCE
    style: str = DEFAULT_STYLE
    swim_csv: Optional[Path] = None
    swim_plot: Optional[Path] = None

    def __post_init__(self) -> None:
        distance = normalize_distance(self.distance)
        style = normalize_style(self.style)
        object.__setattr__(self, "distance", distance)
        object.__setattr__(self, "style", style)

        if self.swim_csv is None:
            object.__setattr__(self, "swim_csv", default_dataset_csv(PROCESSED_DIR, distance, style))
        if self.swim_plot is None:
            object.__setattr__(self, "swim_plot", default_scatter_image(OUTPUT_DIR, distance, style))

    @property
    def freestyle_100_csv(self) -> Path:
        return default_dataset_csv(PROCESSED_DIR, 100, "Stile libero")

    @property
    def freestyle_100_plot(self) -> Path:
        return default_scatter_image(OUTPUT_DIR, 100, "Stile libero")
