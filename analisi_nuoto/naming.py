from pathlib import Path
from typing import Union


SUPPORTED_DISTANCES = (50, 75, 100, 200)
DEFAULT_DISTANCE = 100
DEFAULT_STYLE = "Stile libero"

STYLE_ALIASES = {
    "stile": "Stile libero",
    "libero": "Stile libero",
    "stile libero": "Stile libero",
    "dorso": "Dorso",
    "rana": "Rana",
    "farfalla": "Farfalla",
    "misto": "Misto",
}


def normalize_distance(distance: Union[int, str]) -> int:
    value = int(distance)
    if value not in SUPPORTED_DISTANCES:
        allowed = ", ".join(str(item) for item in SUPPORTED_DISTANCES)
        raise ValueError(f"Distanza non supportata: {value}. Valori ammessi: {allowed}.")
    return value


def normalize_style(style: str) -> str:
    text = str(style).strip()
    if not text:
        raise ValueError("Lo stile non puo' essere vuoto.")

    return STYLE_ALIASES.get(text.lower(), text)


def style_slug(style: str) -> str:
    normalized = normalize_style(style)
    if normalized == "Stile libero":
        return "stile"

    return normalized.lower().replace(" ", "_")


def dataset_stem(distance: Union[int, str], style: str) -> str:
    return f"{normalize_distance(distance)}_{style_slug(style)}"


def default_dataset_csv(processed_dir: Path, distance: Union[int, str], style: str) -> Path:
    return processed_dir / f"{dataset_stem(distance, style)}.csv"


def default_scatter_image(output_dir: Path, distance: Union[int, str], style: str) -> Path:
    return output_dir / f"{dataset_stem(distance, style)}_scatter.png"
