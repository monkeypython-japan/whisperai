from progress import tick
from srt_utils import parse_srt_blocks, build_srt
from filter import filter_blocks


# ISO 639-1 / ffprobe の3文字コード → NLLB(FLORES-200) コード
_NLLB_CODES = {
    "en": "eng_Latn", "eng": "eng_Latn",
    "ja": "jpn_Jpan", "jpn": "jpn_Jpan",
    "fr": "fra_Latn", "fra": "fra_Latn", "fre": "fra_Latn",
    "de": "deu_Latn", "deu": "deu_Latn", "ger": "deu_Latn",
    "es": "spa_Latn", "spa": "spa_Latn",
    "it": "ita_Latn", "ita": "ita_Latn",
    "pt": "por_Latn", "por": "por_Latn",
    "ru": "rus_Cyrl", "rus": "rus_Cyrl",
    "zh": "zho_Hans", "chi": "zho_Hans", "zho": "zho_Hans",
    "ko": "kor_Hang", "kor": "kor_Hang",
    "nl": "nld_Latn", "dut": "nld_Latn", "nld": "nld_Latn",
    "sv": "swe_Latn", "swe": "swe_Latn",
    "da": "dan_Latn", "dan": "dan_Latn",
    "no": "nob_Latn", "nor": "nob_Latn",
    "fi": "fin_Latn", "fin": "fin_Latn",
    "pl": "pol_Latn", "pol": "pol_Latn",
    "tr": "tur_Latn", "tur": "tur_Latn",
    "ar": "arb_Arab", "ara": "arb_Arab",
    "hi": "hin_Deva", "hin": "hin_Deva",
    "th": "tha_Thai", "tha": "tha_Thai",
    "vi": "vie_Latn", "vie": "vie_Latn",
    "cs": "ces_Latn", "cze": "ces_Latn", "ces": "ces_Latn",
    "hu": "hun_Latn", "hun": "hun_Latn",
}

_NLLB_MODEL = "facebook/nllb-200-distilled-600M"


def _to_nllb_code(lang: str) -> str | None:
    return _NLLB_CODES.get(lang.lower())


def _translate_marian_to_english(texts: list[str]) -> list[str]:
    """opus-mt-mul-en による多言語→英語翻訳"""
    from transformers import MarianMTModel, MarianTokenizer

    model_name = "Helsinki-NLP/opus-mt-mul-en"
    print("翻訳モデルを読み込み中 ", end="", flush=True)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    tick()

    print("翻訳中 ", end="", flush=True)
    batch_size = 20
    out = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        tokens = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = model.generate(**tokens)
        out.extend(tokenizer.batch_decode(translated, skip_special_tokens=True))
        tick()
    return out


def _translate_nllb(texts: list[str], src_lang: str, tgt_lang: str) -> list[str]:
    """NLLB-200 による任意言語間の翻訳"""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    src = _to_nllb_code(src_lang)
    tgt = _to_nllb_code(tgt_lang)
    if src is None:
        raise RuntimeError(f"翻訳元言語 '{src_lang}' は未対応です。")
    if tgt is None:
        raise RuntimeError(f"翻訳先言語 '{tgt_lang}' は未対応です。")

    print(f"翻訳モデルを読み込み中 ({src} → {tgt}) ", end="", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(_NLLB_MODEL, src_lang=src)
    model = AutoModelForSeq2SeqLM.from_pretrained(_NLLB_MODEL)
    tick()

    tgt_token_id = tokenizer.convert_tokens_to_ids(tgt)

    print("翻訳中 ", end="", flush=True)
    batch_size = 16
    out = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        tokens = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = model.generate(
            **tokens,
            forced_bos_token_id=tgt_token_id,
            max_length=512,
        )
        out.extend(tokenizer.batch_decode(translated, skip_special_tokens=True))
        tick()
    return out


def translate_srt(srt_text: str, src_lang: str, target_lang: str = "en") -> str:
    """SRT テキストの本文のみを指定言語に翻訳して返す（タイムコード保持）

    - target_lang == "en": opus-mt-mul-en（従来動作）
    - それ以外: NLLB-200（src_lang が必要）
    """
    blocks = parse_srt_blocks(srt_text)
    if not blocks:
        return srt_text

    before = len(blocks)
    blocks = filter_blocks(blocks)
    after = len(blocks)
    if before != after:
        print(f"フィルタ: {before - after} ブロックを除去 ({before} → {after})")

    if not blocks:
        return ""

    texts = [b["text"] for b in blocks]

    if target_lang == "en":
        translated_texts = _translate_marian_to_english(texts)
    else:
        translated_texts = _translate_nllb(texts, src_lang, target_lang)

    for b, t in zip(blocks, translated_texts):
        b["text"] = t

    return build_srt(blocks)


def translate_srt_to_english(srt_text: str) -> str:
    """後方互換用のラッパー"""
    return translate_srt(srt_text, src_lang="en", target_lang="en")
