"""Sort files in one directory into extension-based folders."""

from __future__ import annotations

import argparse
from pathlib import Path


CATEGORIES = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md"},
    "Spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg"},
    "Video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Archives": {".zip", ".7z", ".rar", ".tar", ".gz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".sql", ".json"},
}


def category_for(path: Path) -> str:
    suffix = path.suffix.casefold()
    return next((name for name, suffixes in CATEGORIES.items() if suffix in suffixes), "Other")


def available_destination(path: Path) -> Path:
    if not path.exists():
        return path
    for number in range(1, 10_000):
        candidate = path.with_name(f"{path.stem}_{number}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Не удалось подобрать свободное имя для {path.name}")


def organize(folder: Path, *, apply: bool) -> list[tuple[Path, Path]]:
    folder = folder.expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"Это не папка: {folder}")

    moves: list[tuple[Path, Path]] = []
    for item in sorted(folder.iterdir(), key=lambda path: path.name.casefold()):
        if not item.is_file() or item.is_symlink():
            continue
        target_dir = folder / category_for(item)
        target = available_destination(target_dir / item.name)
        moves.append((item, target))
        if apply:
            target_dir.mkdir(exist_ok=True)
            item.rename(target)
    return moves


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Распределяет файлы в папке по типам. По умолчанию только показывает план."
    )
    parser.add_argument("folder", type=Path, help="папка с файлами")
    parser.add_argument("--apply", action="store_true", help="выполнить показанные перемещения")
    args = parser.parse_args()
    try:
        moves = organize(args.folder, apply=args.apply)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if not moves:
        print("Обычных файлов для сортировки не найдено.")
        return 0
    for source, target in moves:
        prefix = "Перемещён" if args.apply else "План"
        print(f"{prefix}: {source.name} → {target.parent.name}/{target.name}")
    if not args.apply:
        print("Предпросмотр. Добавьте --apply, чтобы выполнить перемещения.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
