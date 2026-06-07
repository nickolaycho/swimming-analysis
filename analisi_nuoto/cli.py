import argparse
from pathlib import Path
from typing import List, Optional

from analisi_nuoto.config import PipelinePaths


def _paths_from_args(args: argparse.Namespace) -> PipelinePaths:
    defaults = PipelinePaths()
    return PipelinePaths(
        raw_laps_dir=Path(args.raw_laps_dir) if args.raw_laps_dir else defaults.raw_laps_dir,
        merged_laps_csv=Path(args.merged_laps_csv)
        if args.merged_laps_csv
        else defaults.merged_laps_csv,
        freestyle_100_csv=Path(args.freestyle_100_csv)
        if args.freestyle_100_csv
        else defaults.freestyle_100_csv,
        freestyle_100_plot=Path(args.freestyle_100_plot)
        if args.freestyle_100_plot
        else defaults.freestyle_100_plot,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="analisi-nuoto")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Esegue tutta la pipeline")
    _add_common_paths(run_parser)
    run_parser.add_argument("--show-plot", action="store_true")

    merge_parser = subparsers.add_parser("merge", help="Unisce i CSV dei singoli lap")
    _add_common_paths(merge_parser)

    prepare_parser = subparsers.add_parser(
        "prepare-100-stile",
        help="Costruisce il dataset dei 100 stile libero",
    )
    _add_common_paths(prepare_parser)

    plot_parser = subparsers.add_parser(
        "plot-100-stile",
        help="Genera lo scatter plot dei 100 stile libero",
    )
    _add_common_paths(plot_parser)
    plot_parser.add_argument("--show-plot", action="store_true")

    return parser


def _add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--raw-laps-dir")
    parser.add_argument("--merged-laps-csv")
    parser.add_argument("--freestyle-100-csv")
    parser.add_argument("--freestyle-100-plot")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    paths = _paths_from_args(args)

    if args.command == "run":
        from analisi_nuoto.orchestrator import run_pipeline

        result = run_pipeline(paths, show_plot=args.show_plot)
        print(f"CSV unificato: {result.merged_laps_csv} ({result.merged_rows} righe)")
        print(f"Dataset 100 stile: {result.freestyle_100_csv} ({result.freestyle_100_rows} righe)")
        print(f"Grafico: {result.freestyle_100_plot}")
        return 0

    if args.command == "merge":
        from analisi_nuoto.ingestion import merge_lap_csvs

        df = merge_lap_csvs(paths.raw_laps_dir, paths.merged_laps_csv)
        print(f"CSV unificato: {paths.merged_laps_csv} ({len(df)} righe)")
        return 0

    if args.command == "prepare-100-stile":
        from analisi_nuoto.datasets import build_100_freestyle_dataset

        df = build_100_freestyle_dataset(paths.merged_laps_csv, paths.freestyle_100_csv)
        print(f"Dataset 100 stile: {paths.freestyle_100_csv} ({len(df)} righe)")
        return 0

    if args.command == "plot-100-stile":
        from analisi_nuoto.visualization import build_100_freestyle_scatter

        plot_path = build_100_freestyle_scatter(
            paths.freestyle_100_csv,
            paths.freestyle_100_plot,
            show_plot=args.show_plot,
        )
        print(f"Grafico: {plot_path}")
        return 0

    parser.error(f"Comando non riconosciuto: {args.command}")
    return 2
