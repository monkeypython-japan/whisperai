import re

import config

# 既知のクレジット・ノイズパターン（大文字小文字無視、config.toml で変更可能）
_CREDIT_RE = re.compile("|".join(config.get("filter", "credit_patterns")), re.IGNORECASE)


def filter_blocks(blocks: list[dict]) -> list[dict]:
    """ノイズブロックを除去して連番を振り直す"""
    filtered = []
    prev_text = None

    for b in blocks:
        text = b["text"].strip()

        # 空ブロックを除去
        if not text:
            continue

        # 誤パースされたブロックを除去（テキストに --> が含まれる場合は SRT 構造が混入している）
        if "-->" in text:
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
