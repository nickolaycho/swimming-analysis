def tempo_to_seconds(value: str) -> float:
    text = str(value).strip()
    if not text:
        raise ValueError("Tempo vuoto")

    parts = text.split(":")
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds

    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds

    raise ValueError(f"Formato tempo non riconosciuto: {value}")


def seconds_to_label(value: float, _position: int) -> str:
    total_seconds = max(value, 0)
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f"{minutes:02d}:{seconds:04.1f}"
