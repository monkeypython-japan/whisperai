from progress import tick
from srt_utils import parse_srt_blocks, build_srt
from filter import filter_blocks


def translate_srt_to_english(srt_text: str) -> str:
    """SRT テキストの本文のみを英語に翻訳して返す（タイムコード保持）"""
    from transformers import MarianMTModel, MarianTokenizer

    blocks = parse_srt_blocks(srt_text)
    if not blocks:
        return srt_text

    # 翻訳前にフィルタリング
    before = len(blocks)
    blocks = filter_blocks(blocks)
    after = len(blocks)
    if before != after:
        print(f"フィルタ: {before - after} ブロックを除去 ({before} → {after})")

    if not blocks:
        return ""

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

    return build_srt(blocks)
