#!/usr/bin/env python3
import sys
import os

from subtitle import get_subtitle_tracks, print_tracks, extract_srt, find_track_by_lang
from translate import translate_srt_to_english
from transcribe import transcribe
from output import build_output_path, write_srt


def main():
    if len(sys.argv) < 2:
        print("使い方: whisperai.py <動画ファイル> [言語コード]")
        print("  例: whisperai.py movie.mp4")
        print("  例: whisperai.py movie.mp4 en")
        sys.exit(1)

    video_path = sys.argv[1]
    lang_code = sys.argv[2] if len(sys.argv) >= 3 else None

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

    if tracks:
        # 字幕ありの動画
        if lang_code is None:
            # 言語コード未指定 → トラック一覧を表示して終了
            print_tracks(tracks)
            print("\n言語コードを指定して再実行してください。")
            print(f"  例: whisperai.py {video_path} en")
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

        # 英語に翻訳
        srt_text = translate_srt_to_english(srt_text)

        output_path = build_output_path(video_path, "en")
        write_srt(output_path, srt_text)

    else:
        # 字幕なし → Whisper で音声認識
        print("字幕トラックなし。Whisper で音声認識を行います。")
        try:
            srt_text, detected_lang = transcribe(video_path)
        except RuntimeError as e:
            print(f"\nエラー: {e}")
            sys.exit(1)

        print(f"\n検出言語: {detected_lang}")
        output_path = build_output_path(video_path, detected_lang)
        write_srt(output_path, srt_text)


if __name__ == "__main__":
    main()
