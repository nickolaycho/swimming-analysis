from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from analisi_nuoto.config import PipelinePaths
from analisi_nuoto.datasets import build_100_freestyle_dataset
from analisi_nuoto.ingestion import merge_lap_csvs
from analisi_nuoto.visualization import build_100_freestyle_scatter


@dataclass(frozen=True)
class PipelineResult:
    merged_laps_csv: Path
    freestyle_100_csv: Path
    freestyle_100_plot: Path
    merged_rows: int
    freestyle_100_rows: int


def run_pipeline(paths: Optional[PipelinePaths] = None, show_plot: bool = False) -> PipelineResult:
    paths = paths or PipelinePaths()

    merged_df = merge_lap_csvs(paths.raw_laps_dir, paths.merged_laps_csv)
    freestyle_df = build_100_freestyle_dataset(paths.merged_laps_csv, paths.freestyle_100_csv)
    plot_path = build_100_freestyle_scatter(
        paths.freestyle_100_csv,
        paths.freestyle_100_plot,
        show_plot=show_plot,
    )

    return PipelineResult(
        merged_laps_csv=paths.merged_laps_csv,
        freestyle_100_csv=paths.freestyle_100_csv,
        freestyle_100_plot=plot_path,
        merged_rows=len(merged_df),
        freestyle_100_rows=len(freestyle_df),
    )
