from pathlib import Path


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    # strip "<>" so the old scraped/*_isthereanydeal.txt files can be reused as-is
    return {line.strip().strip("<>") for line in path.read_text().splitlines() if line.strip()}


def mark_seen(path: Path, urls: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as file:
        file.writelines(url + "\n" for url in urls)
