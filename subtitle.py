import json
import subprocess
import tempfile
import os


def get_subtitle_tracks(video_path: str) -> list[dict]:
    """動画ファイルの字幕トラック一覧を返す"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-select_streams", "s",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe エラー: {result.stderr}")

    data = json.loads(result.stdout)
    streams = data.get("streams", [])

    tracks = []
    for s in streams:
        tags = s.get("tags", {})
        lang = tags.get("language", "und")
        title = tags.get("title", "")
        codec = s.get("codec_name", "")
        index = s.get("index", 0)
        tracks.append({"index": index, "lang": lang, "title": title, "codec": codec})
    return tracks


def print_tracks(tracks: list[dict]) -> None:
    """字幕トラック一覧を表示"""
    if not tracks:
        print("字幕トラックが見つかりません。")
        return
    print("字幕トラック一覧:")
    for t in tracks:
        title_str = f" ({t['title']})" if t["title"] else ""
        print(f"  [{t['index']}] 言語: {t['lang']}{title_str}  形式: {t['codec']}")


def extract_srt(video_path: str, stream_index: int) -> str:
    """指定ストリームの字幕を SRT テキストとして返す"""
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            "ffmpeg", "-y", "-v", "quiet",
            "-i", video_path,
            "-map", f"0:{stream_index}",
            tmp_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg 字幕抽出エラー: {result.stderr}")

        with open(tmp_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    finally:
        os.unlink(tmp_path)


def find_track_by_lang(tracks: list[dict], lang_code: str) -> dict | None:
    """言語コードに一致するトラックを返す（最初の一致）"""
    for t in tracks:
        if t["lang"].lower().startswith(lang_code.lower()):
            return t
    return None
