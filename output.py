import os
import shutil
import tempfile
from pathlib import Path


def build_output_path(video_path: str, lang_code: str) -> str:
    p = Path(video_path)
    return str(p.parent / f"{p.stem}.{lang_code}.srt")


def write_srt(path: str, content: str) -> None:
    # ローカル一時ファイルに書き出してからコピー（ネットワークドライブのタイムアウト対策）
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".srt", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        shutil.copy2(tmp_path, path)
        os.remove(tmp_path)
        print(f"\n出力: {path}")
    except OSError as e:
        print(f"\n警告: 出力先への書き込みに失敗しました ({e})")
        print(f"一時ファイルに保存しました: {tmp_path}")
        print(f"手動でコピーしてください: cp \"{tmp_path}\" \"{path}\"")
