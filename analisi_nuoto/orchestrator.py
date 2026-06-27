from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from analisi_nuoto.config import PipelinePaths
from analisi_nuoto.datasets import build_swim_dataset
from analisi_nuoto.ingestion import merge_lap_csvs
from analisi_nuoto.visualization import build_swim_scatter, build_swim_scatter_stroke_rate
from analisi_nuoto.naming import default_stroke_rate_image


@dataclass(frozen=True)
class PipelineResult:
    merged_laps_csv: Path
    swim_csv: Path
    swim_plot: Path
    merged_rows: int
    swim_rows: int
    stroke_rate_plot: Optional[Path] = None

    @property
    def freestyle_100_csv(self) -> Path:
        return self.swim_csv

    @property
    def freestyle_100_plot(self) -> Path:
        return self.swim_plot

    @property
    def freestyle_100_rows(self) -> int:
        return self.swim_rows


def run_pipeline(
    paths: Optional[PipelinePaths] = None,
    show_plot: bool = False,
    chart_type: str = "time",
) -> PipelineResult:
    """
    Esegue la pipeline completa di ingestion, processing e visualization.
    
    Args:
        paths: Configurazione dei percorsi
        show_plot: Se True, mostra i plot a schermo
        chart_type: Tipo di chart da generare: 'time', 'pace', o 'all'
    
    Returns:
        PipelineResult con i risultati della pipeline
    """
    paths = paths or PipelinePaths()

    merged_df = merge_lap_csvs(paths.raw_laps_dir, paths.merged_laps_csv)
    raise ValueError("stop here")
    swim_df = build_swim_dataset(
        paths.merged_laps_csv,
        paths.swim_csv,
        distance=paths.distance,
        style=paths.style,
    )
    
    # Genera lo scatter time vs bracciate
    plot_path = None
    if chart_type in {"time", "all"}:
        plot_path = build_swim_scatter(
            paths.swim_csv,
            paths.swim_plot,
            distance=paths.distance,
            style=paths.style,
            show_plot=show_plot,
        )
    
    # Genera lo scatter pace vs bracciate per minuto
    stroke_rate_plot = None
    if chart_type in {"pace", "all"}:
        stroke_rate_plot = default_stroke_rate_image(
            paths.swim_plot.parent,
            distance=paths.distance,
            style=paths.style,
        )
        stroke_rate_plot = build_swim_scatter_stroke_rate(
            paths.merged_laps_csv,
            stroke_rate_plot,
            distance=paths.distance,
            style=paths.style,
            show_plot=show_plot,
        )

    return PipelineResult(
        merged_laps_csv=paths.merged_laps_csv,
        swim_csv=paths.swim_csv,
        swim_plot=plot_path or paths.swim_plot,
        stroke_rate_plot=stroke_rate_plot,
        merged_rows=len(merged_df),
        swim_rows=len(swim_df),
    )
