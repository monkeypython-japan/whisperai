---
status: resolved
tags:
  - project/whisperai
modified: 2026-07-07
---

# transformers 新版で `pipeline("translation")` が使えない

## 症状

```
KeyError: "Unknown task translation, available tasks are [...]"
```

`transformers.pipeline("translation", model=...)` を呼ぶと、新しいバージョンの transformers では `"translation"` タスクがサポートタスク一覧に存在せずエラーになる。

## 原因

transformers の新版で `pipeline` の `"translation"` タスクが削除された。

## 回避策

`MarianMTModel` / `MarianTokenizer`（あるいは `AutoModelForSeq2SeqLM` / `AutoTokenizer`）を直接使い、`tokenizer(...)` → `model.generate(...)` → `tokenizer.batch_decode(...)` の手順で翻訳する。`translate.py` の実装を参照。
