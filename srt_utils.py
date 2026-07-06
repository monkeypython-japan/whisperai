import srt


def parse_srt_blocks(srt_text: str) -> list[dict]:
    """SRT テキストをブロック（番号・タイムコード・テキスト）に分解

    srt ライブラリによるパースで BOM・改行コード・タイムコードの揺れに対応する。
    """
    # BOM 除去（srt ライブラリは先頭 BOM で失敗することがある）
    srt_text = srt_text.lstrip("﻿")

    blocks = []
    for sub in srt.parse(srt_text):
        start = srt.timedelta_to_srt_timestamp(sub.start)
        end = srt.timedelta_to_srt_timestamp(sub.end)
        blocks.append({
            "index": str(sub.index),
            "timecode": f"{start} --> {end}",
            "text": sub.content.strip(),
        })
    return blocks


def build_srt(blocks: list[dict]) -> str:
    parts = []
    for b in blocks:
        parts.append(f"{b['index']}\n{b['timecode']}\n{b['text']}\n")
    return "\n".join(parts)
