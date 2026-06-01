import os
import tempfile
import subprocess
from pathlib import Path
from progress import tick


CACHE_DIR = Path.home() / "Library" / "Application Support" / "whisperai"


def _ensure_model() -> object:
    """Whisper large モデルをロード（初回はダウンロード）"""
    import whisper

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print("Whisper モデルを読み込み中 ", end="", flush=True)
    model = whisper.load_model("large", download_root=str(CACHE_DIR))
    tick()
    return model


def _extract_audio(video_path: str) -> str:
    """動画から 16kHz モノラル WAV を一時ファイルに抽出して返す"""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        tmp.name,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        os.unlink(tmp.name)
        raise RuntimeError(f"音声抽出エラー: {result.stderr}")
    return tmp.name


def _segments_to_srt(segments: list) -> tuple[str, str]:
    """Whisper セグメントを SRT テキストと検出言語コードに変換"""
    def fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, seg in enumerate(segments, 1):
        start = fmt_time(seg["start"])
        end = fmt_time(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def transcribe(video_path: str) -> tuple[str, str]:
    """音声認識を行い (SRT テキスト, 言語コード) を返す"""
    model = _ensure_model()

    print("音声を抽出中 ", end="", flush=True)
    audio_path = _extract_audio(video_path)
    tick()

    try:
        print("音声認識中 ", end="", flush=True)
        result = model.transcribe(audio_path, verbose=False)
        tick()

        lang = result.get("language", "en")
        srt_text = _segments_to_srt(result["segments"])
        return srt_text, lang
    finally:
        os.unlink(audio_path)
