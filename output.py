import os
from pathlib import Path


def build_output_path(video_path: str, lang_code: str) -> str:
    p = Path(video_path)
    return str(p.parent / f"{p.stem}.{lang_code}.srt")


def write_srt(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n出力: {path}")
