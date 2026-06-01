import re
from progress import tick


def _parse_srt_blocks(srt_text: str) -> list[dict]:
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


def _build_srt(blocks: list[dict]) -> str:
    parts = []
    for b in blocks:
        parts.append(f"{b['index']}\n{b['timecode']}\n{b['text']}\n")
    return "\n".join(parts)


def translate_srt_to_english(srt_text: str) -> str:
    """SRT テキストの本文のみを英語に翻訳して返す（タイムコード保持）"""
    from transformers import MarianMTModel, MarianTokenizer

    blocks = _parse_srt_blocks(srt_text)
    if not blocks:
        return srt_text

    model_name = "Helsinki-NLP/opus-mt-mul-en"
    print("翻訳モデルを読み込み中 ", end="", flush=True)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    tick()

    print("翻訳中 ", end="", flush=True)
    texts = [b["text"] for b in blocks]

    batch_size = 20
    translated_texts = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        tokens = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = model.generate(**tokens)
        decoded = tokenizer.batch_decode(translated, skip_special_tokens=True)
        translated_texts.extend(decoded)
        tick()

    for b, t in zip(blocks, translated_texts):
        b["text"] = t

    return _build_srt(blocks)
