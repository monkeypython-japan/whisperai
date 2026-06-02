import subprocess
from pathlib import Path
from progress import tick

MLX_MODEL = "mlx-community/whisper-large-v3-mlx"


def _segments_to_srt(segments: list) -> str:
    """Whisper セグメントを SRT テキストに変換"""
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
    import mlx_whisper

    print("音声認識中（Apple GPU 使用）", end="", flush=True)
    result = mlx_whisper.transcribe(
        video_path,
        path_or_hf_repo=MLX_MODEL,
        verbose=False,
        # 無音区間のハルシネーション抑制
        no_speech_threshold=0.6,
        condition_on_previous_text=False,
        initial_prompt="",
    )
    tick()

    lang = result.get("language", "en")
    srt_text = _segments_to_srt(result["segments"])
    return srt_text, lang
