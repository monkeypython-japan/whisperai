import re


# 既知のクレジット・ノイズパターン（大文字小文字無視）
_CREDIT_PATTERNS = [
    r"sous-titrage",
    r"subtitl(e|ing|ed) by",
    r"sync(ed|hronized)? (by|and corrected)",
    r"translated by",
    r"ripped by",
    r"encoded by",
    r"www\.",
    r"opensubtitles",
    r"subscene",
    r"addic7ed",
]
_CREDIT_RE = re.compile("|".join(_CREDIT_PATTERNS), re.IGNORECASE)


def filter_blocks(blocks: list[dict]) -> list[dict]:
    """ノイズブロックを除去して連番を振り直す"""
    filtered = []
    prev_text = None

    for b in blocks:
        text = b["text"].strip()

        # 空ブロックを除去
        if not text:
            continue

        # 既知クレジットパターンを除去
        if _CREDIT_RE.search(text):
            continue

        # 連続する同一テキストの重複を除去
        if text == prev_text:
            continue

        filtered.append(b)
        prev_text = text

    # 連番を振り直す
    for i, b in enumerate(filtered, 1):
        b["index"] = str(i)

    return filtered
