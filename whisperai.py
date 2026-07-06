#!/usr/bin/env python3
import sys
import os

from subtitle import get_subtitle_tracks, print_tracks, extract_srt, find_track_by_lang
from translate import translate_srt
from transcribe import transcribe
from output import build_output_path, write_srt
from srt_utils import parse_srt_blocks, build_srt
from filter import filter_blocks


HELP_TEXT = """使い方: whisperai.py <動画ファイル> [言語コード] [オプション]

引数:
  動画ファイル    処理する動画ファイルのパス
  言語コード      字幕トラックの言語コード（en / fr / ja など）
                  省略すると字幕トラック一覧を表示して終了

オプション:
  --translate[=言語]  字幕を指定言語に翻訳して出力（省略時 en、字幕トラックありの場合のみ有効）
                  例: --translate / --translate=ja / --translate=en
  --transcribe    字幕トラックを無視して Whisper で音声認識を強制実行
  --help          このヘルプを表示して終了

動作:
  字幕トラックあり
    言語コード省略  → 字幕トラック一覧を表示して終了
    言語コード指定  → 指定言語の字幕をそのまま SRT として出力
    --translate 付き → 指定言語の字幕を翻訳して SRT として出力（既定は英語、--translate=ja で日本語）
    --transcribe 付き → 字幕トラックを無視して Whisper で音声認識

  字幕トラックなし
    Whisper で音声認識し、検出した言語で SRT を出力（翻訳なし）

出力ファイル:
  {動画ファイルと同じフォルダ}/{ベース名}.{言語コード}.srt

例:
  whisperai.py "movie.mkv"
  whisperai.py "movie.mkv" fr
  whisperai.py "movie.mkv" fr --translate
  whisperai.py "movie.mkv" fr --translate=ja
  whisperai.py "movie.mkv" --transcribe
  whisperai.py "movie.mp4"
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if "--help" in flags:
        print(HELP_TEXT, end="")
        sys.exit(0)

    translate_target = None
    for f in flags:
        if f == "--translate":
            translate_target = "en"
        elif f.startswith("--translate="):
            translate_target = f.split("=", 1)[1].lower()
            if not translate_target:
                print("エラー: --translate= の言語コードが空です。例: --translate=ja")
                sys.exit(1)
    force_transcribe = "--transcribe" in flags

    if len(args) < 1:
        print(HELP_TEXT, end="")
        sys.exit(1)

    video_path = args[0]
    lang_code = args[1] if len(args) >= 2 else None

    if not os.path.isfile(video_path):
        print(f"エラー: ファイルが見つかりません: {video_path}")
        sys.exit(1)

    # 字幕トラックを確認
    print("字幕トラックを確認中...", end="", flush=True)
    try:
        tracks = get_subtitle_tracks(video_path)
    except RuntimeError as e:
        print(f"\nエラー: {e}")
        sys.exit(1)
    print(" 完了")

    if tracks and not force_transcribe:
        # 字幕ありの動画
        if lang_code is None:
            # 言語コード未指定 → トラック一覧を表示して終了
            print_tracks(tracks)
            print("\n言語コードを指定して再実行してください。")
            print(f"  例: whisperai.py \"{video_path}\" en")
            sys.exit(0)

        # 指定言語のトラックを検索
        track = find_track_by_lang(tracks, lang_code)
        if track is None:
            print(f"エラー: 言語 '{lang_code}' の字幕トラックが見つかりません。")
            print_tracks(tracks)
            sys.exit(1)

        print(f"字幕トラック [{track['index']}] ({track['lang']}) を抽出中 ", end="", flush=True)
        try:
            srt_text = extract_srt(video_path, track["index"])
        except RuntimeError as e:
            print(f"\nエラー: {e}")
            sys.exit(1)
        print("*")

        # フィルター適用
        blocks = parse_srt_blocks(srt_text)
        blocks = filter_blocks(blocks)
        srt_text = build_srt(blocks)

        if translate_target:
            # --translate 指定時のみ翻訳（既定 en、--translate=ja などで指定）
            try:
                srt_text = translate_srt(srt_text, src_lang=track["lang"], target_lang=translate_target)
            except RuntimeError as e:
                print(f"\nエラー: {e}")
                sys.exit(1)
            output_path = build_output_path(video_path, translate_target)
        else:
            output_path = build_output_path(video_path, lang_code)

        write_srt(output_path, srt_text)

    else:
        # 字幕なし、または --transcribe 指定 → Whisper で音声認識
        if force_transcribe and tracks:
            print("--transcribe 指定。字幕トラックを無視して Whisper で音声認識を行います。")
        else:
            print("字幕トラックなし。Whisper で音声認識を行います。")
        try:
            srt_text, detected_lang = transcribe(video_path)
        except RuntimeError as e:
            print(f"\nエラー: {e}")
            sys.exit(1)

        # フィルター適用
        blocks = parse_srt_blocks(srt_text)
        blocks = filter_blocks(blocks)
        srt_text = build_srt(blocks)

        print(f"\n検出言語: {detected_lang}")
        output_path = build_output_path(video_path, detected_lang)
        write_srt(output_path, srt_text)


if __name__ == "__main__":
    main()
