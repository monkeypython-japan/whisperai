---
status: resolved
tags:
  - project/whisperai
---

# macOS の Homebrew Python では `pip install` が externally-managed-environment エラーになる

## 症状

```
error: externally-managed-environment
× This environment is externally managed
```

## 原因

PEP 668 により、Homebrew でインストールした Python はシステム環境への直接 `pip install` を拒否する。

## 回避策

venv を使う。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`--break-system-packages` での回避は非推奨（Homebrew 環境を壊すリスクがあるため）。
