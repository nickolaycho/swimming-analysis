from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from analisi_nuoto.config import PipelinePaths
from analisi_nuoto.datasets import build_swim_dataset
from analisi_nuoto.ingestion import merge_lap_csvs
from analisi_nuoto.visualization import build_swim_scatter


@dataclass(frozen=True)
class PipelineResult:
    merged_laps_csv: Path
    swim_csv: Path
    swim_plot: Path
    merged_rows: int
    swim_rows: int

    @property
    def freestyle_100_csv(self) -> Path:
        return self.swim_csv

    @property
    def freestyle_100_plot(self) -> Path:
        return self.swim_plot

    @property
    def freestyle_100_rows(self) -> int:
        return self.swim_rows


def run_pipeline(paths: Optional[PipelinePaths] = None, show_plot: bool = False) -> PipelineResult:
    paths = paths or PipelinePaths()

    merged_df = merge_lap_csvs(paths.raw_laps_dir, paths.merged_laps_csv)
    swim_df = build_swim_dataset(
        paths.merged_laps_csv,
        paths.swim_csv,
        distance=paths.distance,
        style=paths.style,
    )
    plot_path = build_swim_scatter(
        paths.swim_csv,
        paths.swim_plot,
        distance=paths.distance,
        style=paths.style,
        show_plot=show_plot,
    )

    return PipelineResult(
        merged_laps_csv=paths.merged_laps_csv,
        swim_csv=paths.swim_csv,
        swim_plot=plot_path,
        merged_rows=len(merged_df),
        swim_rows=len(swim_df),
    )
