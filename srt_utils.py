import re


def parse_srt_blocks(srt_text: str) -> list[dict]:
    """SRT テキストをブロック（番号・タイムコード・テキスト）に分解"""
    blocks = []
    pattern = re.compile(
        r"(\d+)\s*\n"
        r"(\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n"
        r"(.*?)(?=\n\n\d+\s*\n|\Z)",
        re.DOTALL,
    )
    for m in pattern.finditer(srt_text.strip()):
        blocks.append({
            "index": m.group(1),
            "timecode": m.group(2),
            "text": m.group(3).strip(),
        })
    return blocks


def build_srt(blocks: list[dict]) -> str:
    parts = []
    for b in blocks:
        parts.append(f"{b['index']}\n{b['timecode']}\n{b['text']}\n")
    return "\n".join(parts)
