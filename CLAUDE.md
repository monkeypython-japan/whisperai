# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 言語

- 会話は全て日本語で行う。
- 会話の引き継ぎサマリー（コンテキスト圧縮時の要約）も日本語で行う。

## 開発ルール

- **すべての変更はブランチを作成してから行う。main への直接コミットは禁止。**
- 曖昧な点はユーザーに質問する。
- ブランチ上で変更を実施したら、ユーザーがテストを行う。
- テスト完了後、Claude がコミットして main へマージする。
- マージに先立ち、ブランチの変更内容に仕様の変更（挙動・数値・UI・AIロジック）が含まれる場合は `whisperai-spec.md` に反映してから main へマージする。
- origin へのプッシュに先立ち、変更内容を `README.md` に反映してからプッシュする。

## プロジェクト概要

OpenAI Whisper（large モデル）を使ったオフライン動画字幕生成 CLI ツール。動画ファイルを受け取り、SRT ファイルを出力する。

## アーキテクチャ（予定）

- **CLI エントリポイント**: コマンドライン引数で動画ファイルを受け取る
- **字幕トラック検出**: ffprobe で動画の字幕ストリームを確認
  - 日本語字幕あり → 報告して終了
  - 英語字幕あり → 字幕を SRT 形式で抽出して終了
  - それ以外 → Whisper で音声認識
- **モデル管理**: `~/Library/Application Support/whisperai/` にモデルをキャッシュ（初回のみダウンロード）
- **出力**: 動画ファイルと同じフォルダに `{basename}.{lang}.srt` を生成

## 技術スタック

- 言語: Python（予定）
- 音声認識: openai-whisper（large モデル）
- 動画処理: ffmpeg / ffprobe

## 開発コマンド

```bash
# 仮想環境のセットアップ（初回のみ）
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 仮想環境の有効化（ターミナルを開き直した場合）
source .venv/bin/activate

# 実行例（字幕トラック一覧表示 / 字幕なし動画の音声認識）
python whisperai.py "<動画ファイル>"

# 実行例（字幕トラックをそのまま抽出）
python whisperai.py "<動画ファイル>" fr

# 実行例（字幕トラックを英語に翻訳して出力）
python whisperai.py "<動画ファイル>" fr --translate
```

> パスに日本語やスペースが含まれる場合はダブルクォートで囲む。
