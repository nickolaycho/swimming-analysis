import argparse
import os
from pathlib import Path
import subprocess
import sys
from typing import List, Optional

from analisi_nuoto.config import PipelinePaths
from analisi_nuoto.naming import DEFAULT_DISTANCE, DEFAULT_STYLE, SUPPORTED_DISTANCES


SUPPORTED_DISTANCE_LABEL = ", ".join(str(distance) for distance in SUPPORTED_DISTANCES)


def _paths_from_args(args: argparse.Namespace) -> PipelinePaths:
    defaults = PipelinePaths()
    distance = args.distance if args.distance is not None else defaults.distance
    style = args.style if args.style is not None else defaults.style
    swim_csv = args.swim_csv or args.freestyle_100_csv
    swim_plot = args.swim_plot or args.freestyle_100_plot

    return PipelinePaths(
        raw_laps_dir=Path(args.raw_laps_dir) if args.raw_laps_dir else defaults.raw_laps_dir,
        merged_laps_csv=Path(args.merged_laps_csv)
        if args.merged_laps_csv
        else defaults.merged_laps_csv,
        distance=distance,
        style=style,
        swim_csv=Path(swim_csv) if swim_csv else None,
        swim_plot=Path(swim_plot) if swim_plot else None,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="analisi-nuoto")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Esegue tutta la pipeline")
    _add_common_paths(run_parser)
    run_parser.add_argument("--show-plot", action="store_true")
    run_parser.add_argument(
        "--chart-type",
        choices=["time", "pace", "all"],
        default="time",
        help="Tipo di scatter: 'time' (tempo vs bracciate), 'pace' (passo vs bracciate/min), 'all' (entrambi)",
    )

    merge_parser = subparsers.add_parser("merge", help="Unisce i CSV dei singoli lap")
    _add_common_paths(merge_parser)

    prepare_parser = subparsers.add_parser(
        "prepare-100-stile",
        help="Alias: costruisce il dataset dei 100 stile libero",
    )
    _add_common_paths(prepare_parser)
    prepare_parser.set_defaults(distance=100, style="Stile libero")

    prepare_swim_parser = subparsers.add_parser(
        "prepare",
        help="Costruisce un dataset filtrato per distanza e stile",
    )
    _add_common_paths(prepare_swim_parser)

    plot_parser = subparsers.add_parser(
        "plot-100-stile",
        help="Alias: genera lo scatter plot dei 100 stile libero",
    )
    _add_common_paths(plot_parser)
    plot_parser.add_argument("--show-plot", action="store_true")
    plot_parser.add_argument(
        "--chart-type",
        choices=["time", "pace", "all"],
        default="time",
        help="Tipo di scatter: 'time' (tempo vs bracciate), 'pace' (passo vs bracciate/min), 'all' (entrambi)",
    )
    plot_parser.set_defaults(distance=100, style="Stile libero")

    plot_swim_parser = subparsers.add_parser(
        "plot",
        help="Genera lo scatter plot per distanza e stile",
    )
    _add_common_paths(plot_swim_parser)
    plot_swim_parser.add_argument("--show-plot", action="store_true")
    plot_swim_parser.add_argument(
        "--chart-type",
        choices=["time", "pace", "all"],
        default="time",
        help="Tipo di scatter: 'time' (tempo vs bracciate), 'pace' (passo vs bracciate/min), 'all' (entrambi)",
    )

    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Avvia la dashboard interattiva",
    )
    _add_common_paths(dashboard_parser)
    dashboard_parser.add_argument("--port", type=int, default=8501)

    return parser


def _add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--raw-laps-dir")
    parser.add_argument("--merged-laps-csv")
    parser.add_argument(
        "--distance",
        type=int,
        choices=SUPPORTED_DISTANCES,
        default=DEFAULT_DISTANCE,
        help=f"Distanza da analizzare: {SUPPORTED_DISTANCE_LABEL}",
    )
    parser.add_argument(
        "--style",
        default=DEFAULT_STYLE,
        help="Stile da analizzare, per esempio 'Stile libero', Dorso, Rana, Farfalla o Misto",
    )
    parser.add_argument("--swim-csv")
    parser.add_argument("--swim-plot")
    parser.add_argument("--freestyle-100-csv", help=argparse.SUPPRESS)
    parser.add_argument("--freestyle-100-plot", help=argparse.SUPPRESS)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    paths = _paths_from_args(args)

    if args.command == "dashboard":
        dashboard_path = Path(__file__).with_name("dashboard.py")
        env = os.environ.copy()
        env["ANALISI_NUOTO_MERGED_LAPS_CSV"] = str(paths.merged_laps_csv)
        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_path),
            "--server.port",
            str(args.port),
            "--server.headless",
            "true",
        ]
        return subprocess.run(command, env=env).returncode

    if args.command == "run":
        from analisi_nuoto.orchestrator import run_pipeline

        chart_type = getattr(args, "chart_type", "time")
        result = run_pipeline(paths, show_plot=args.show_plot, chart_type=chart_type)
        print(f"CSV unificato: {result.merged_laps_csv} ({result.merged_rows} righe)")
        print(f"Dataset {paths.distance} {paths.style}: {result.swim_csv} ({result.swim_rows} righe)")
        if result.swim_plot:
            print(f"Grafico tempo/bracciate: {result.swim_plot}")
        if result.stroke_rate_plot:
            print(f"Grafico passo/bracciate per minuto: {result.stroke_rate_plot}")
        return 0

    if args.command == "merge":
        from analisi_nuoto.ingestion import merge_lap_csvs

        df = merge_lap_csvs(paths.raw_laps_dir, paths.merged_laps_csv)
        print(f"CSV unificato: {paths.merged_laps_csv} ({len(df)} righe)")
        return 0

    if args.command in {"prepare-100-stile", "prepare"}:
        from analisi_nuoto.datasets import build_swim_dataset

        df = build_swim_dataset(
            paths.merged_laps_csv,
            paths.swim_csv,
            distance=paths.distance,
            style=paths.style,
        )
        print(f"Dataset {paths.distance} {paths.style}: {paths.swim_csv} ({len(df)} righe)")
        return 0

    if args.command in {"plot-100-stile", "plot"}:
        from analisi_nuoto.visualization import build_swim_scatter, build_swim_scatter_stroke_rate
        from analisi_nuoto.naming import default_stroke_rate_image

        chart_type = getattr(args, "chart_type", "time")
        
        if chart_type in {"time", "all"}:
            plot_path = build_swim_scatter(
                paths.swim_csv,
                paths.swim_plot,
                distance=paths.distance,
                style=paths.style,
                show_plot=args.show_plot,
            )
            print(f"Grafico tempo/bracciate: {plot_path}")
        
        if chart_type in {"pace", "all"}:
            stroke_rate_plot = default_stroke_rate_image(
                paths.swim_plot.parent,
                distance=paths.distance,
                style=paths.style,
            )
            plot_path = build_swim_scatter_stroke_rate(
                paths.merged_laps_csv,
                stroke_rate_plot,
                distance=paths.distance,
                style=paths.style,
                show_plot=args.show_plot,
            )
            print(f"Grafico passo/bracciate per minuto: {plot_path}")
        
        return 0

    parser.error(f"Comando non riconosciuto: {args.command}")
    return 2
