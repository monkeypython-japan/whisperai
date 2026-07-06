# whisperai

動画ファイルからオフラインで SRT 字幕ファイルを生成する CLI ツール。  
Apple Silicon（M シリーズ）の GPU を活用した高速な音声認識に対応しています。

## 特徴

- **完全オフライン** — 音声認識・字幕翻訳ともにインターネット不要
- **Apple Silicon 最適化** — mlx-whisper により M シリーズ GPU をフル活用
- **字幕トラック対応** — 動画に字幕トラックがある場合はそれを抽出・翻訳
- **多言語翻訳** — 英語のほか、`--translate=ja` で日本語など約 25 言語への翻訳に対応
- **一括処理** — 複数ファイル・フォルダ指定でまとめて処理
- **ノイズフィルター** — クレジット・繰り返しハルシネーションを自動除去

## 動作要件

- macOS（Apple Silicon 推奨）
- Python 3.10 以上
- ffmpeg / ffprobe（`brew install ffmpeg` でインストール）

## セットアップ

```bash
# 仮想環境を作成して依存パッケージをインストール
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

初回実行時に音声認識モデル（`whisper-large-v3-mlx`、約 3GB）が Hugging Face から自動ダウンロードされます。

## 使い方

```
python whisperai.py "<動画ファイル|フォルダ>"... [言語コード] [オプション]
```

| オプション | 説明 |
|-----------|------|
| `--translate[=言語]` | 字幕トラックを指定言語に翻訳して出力（省略時は英語。字幕トラックありの場合のみ有効） |
| `--transcribe` | 字幕トラックを無視して Whisper で音声認識を強制実行 |
| `--help` | ヘルプを表示して終了 |

### 字幕トラックなし（音声認識）

```bash
python whisperai.py "<動画ファイル>"
```

Whisper で音声認識し、検出した言語の SRT を出力します。

### 字幕トラックの確認

```bash
python whisperai.py "<動画ファイル>"
```

字幕トラックがある場合はトラック一覧を表示して終了します。言語コードを指定して再実行してください。

### 字幕トラックをそのまま抽出

```bash
python whisperai.py "<動画ファイル>" fr
```

指定した言語コードの字幕トラックをそのまま SRT として出力します。

### 字幕トラックを英語に翻訳して抽出

```bash
python whisperai.py "<動画ファイル>" fr --translate
```

指定した言語コードの字幕トラックを英語に翻訳した SRT を出力します。

### 字幕トラックを日本語などに翻訳して抽出

```bash
python whisperai.py "<動画ファイル>" en --translate=ja
```

`--translate=<言語コード>` で翻訳先を指定できます（ja / de / fr / zh / ko など約 25 言語）。英語以外への翻訳には NLLB-200 モデル（約 2.4GB、初回のみダウンロード）を使用します。

### 複数ファイル・フォルダの一括処理

```bash
python whisperai.py "season1/" en --translate=ja
python whisperai.py "ep1.mkv" "ep2.mkv" en
```

フォルダを指定するとサブフォルダも含めて動画ファイルを名前順に処理します。途中で失敗しても続行し、最後に成功数と失敗ファイル一覧を表示します。

### 字幕トラックを無視して音声認識（--transcribe）

```bash
python whisperai.py "<動画ファイル>" --transcribe
```

字幕トラックがあっても無視し、Whisper で音声認識を強制実行します。字幕トラックが台詞以外の用途（テキストインサートや一部のみ）に使われている動画で使用します。

> パスに日本語やスペースが含まれる場合はダブルクォートで囲んでください。

> Blu-ray PGS や DVD VobSub などの画像字幕はテキストとして抽出できません。トラック一覧に「（画像字幕・抽出不可）」と表示されます。その場合は `--transcribe` で音声認識を利用してください。

## 出力ファイル

| 入力 | 出力 |
|------|------|
| `batman.mp4`（英語音声、字幕なし） | `batman.en.srt` |
| `batman.mkv`（フランス語字幕トラック） | `batman.fr.srt` |
| `batman.mkv`（フランス語字幕 + `--translate`） | `batman.en.srt` |
| `batman.mkv`（英語字幕 + `--translate=ja`） | `batman.ja.srt` |

出力先は入力動画と同じフォルダです。

## 技術スタック

| 役割 | ライブラリ |
|------|-----------|
| 音声認識 | [mlx-whisper](https://github.com/ml-explore/mlx-examples)（Apple MLX） |
| 字幕翻訳（英語向け） | Helsinki-NLP/opus-mt-mul-en（Hugging Face Transformers） |
| 字幕翻訳（英語以外向け） | facebook/nllb-200-distilled-600M（Hugging Face Transformers） |
| 動画処理 | ffmpeg / ffprobe |
