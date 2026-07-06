#!/usr/bin/env python3
import sys
import os
from pathlib import Path

from subtitle import get_subtitle_tracks, print_tracks, extract_srt, find_track_by_lang, is_image_subtitle
from translate import translate_srt
from transcribe import transcribe
from output import build_output_path, write_srt
from srt_utils import parse_srt_blocks, build_srt
from filter import filter_blocks


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".m4v", ".avi", ".mov", ".webm", ".ts", ".wmv"}

HELP_TEXT = """使い方: whisperai.py <動画ファイル|フォルダ>... [言語コード] [オプション]

引数:
  動画ファイル    処理する動画ファイルのパス（複数指定可）
  フォルダ        フォルダ内の動画ファイルを一括処理（サブフォルダも対象）
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
  whisperai.py "season1/" en --translate=ja
  whisperai.py "ep1.mkv" "ep2.mkv" en
"""


def collect_videos(paths: list[str]) -> list[str]:
    """ファイル・フォルダの指定から動画ファイル一覧を組み立てる"""
    videos = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            videos.append(str(path))
        elif path.is_dir():
            found = sorted(
                str(f) for f in path.rglob("*")
                if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
            )
            if not found:
                print(f"警告: フォルダに動画ファイルが見つかりません: {p}")
            videos.extend(found)
        else:
            print(f"エラー: ファイルが見つかりません: {p}")
            sys.exit(1)
    return videos


def process_video(video_path: str, lang_code: str | None,
                  translate_target: str | None, force_transcribe: bool) -> bool:
    """1本の動画を処理する。成功なら True"""
    # 字幕トラックを確認
    print("字幕トラックを確認中...", end="", flush=True)
    try:
        tracks = get_subtitle_tracks(video_path)
    except RuntimeError as e:
        print(f"\nエラー: {e}")
        return False
    print(" 完了")

    if tracks and not force_transcribe:
        # 字幕ありの動画
        if lang_code is None:
            # 言語コード未指定 → トラック一覧を表示するのみ
            print_tracks(tracks)
            print("\n言語コードを指定して再実行してください。")
            print(f"  例: whisperai.py \"{video_path}\" en")
            return True

        # 指定言語のトラックを検索
        track = find_track_by_lang(tracks, lang_code)
        if track is None:
            print(f"エラー: 言語 '{lang_code}' の字幕トラックが見つかりません。")
            print_tracks(tracks)
            return False

        if is_image_subtitle(track):
            print(f"エラー: トラック [{track['index']}] ({track['lang']}) は画像字幕（{track['codec']}）のため、テキストとして抽出できません。")
            print("音声認識で字幕を生成する場合は --transcribe を指定してください。")
            print(f"  例: whisperai.py \"{video_path}\" --transcribe")
            return False

        print(f"字幕トラック [{track['index']}] ({track['lang']}) を抽出中 ", end="", flush=True)
        try:
            srt_text = extract_srt(video_path, track["index"])
        except RuntimeError as e:
            print(f"\nエラー: {e}")
            return False
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
                return False
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
            return False

        # フィルター適用
        blocks = parse_srt_blocks(srt_text)
        blocks = filter_blocks(blocks)
        srt_text = build_srt(blocks)

        print(f"\n検出言語: {detected_lang}")
        output_path = build_output_path(video_path, detected_lang)
        write_srt(output_path, srt_text)

    return True


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

    # 位置引数の解釈:
    #   存在するファイル・フォルダ → 入力
    #   それ以外の 2〜3 文字の引数 → 言語コード
    input_paths = []
    lang_code = None
    for a in args:
        if os.path.exists(a):
            input_paths.append(a)
        elif lang_code is None and 2 <= len(a) <= 3 and a.isalpha():
            lang_code = a.lower()
        else:
            print(f"エラー: ファイルが見つかりません: {a}")
            sys.exit(1)

    if not input_paths:
        print("エラー: 入力ファイルまたはフォルダを指定してください。")
        sys.exit(1)

    videos = collect_videos(input_paths)
    if not videos:
        print("エラー: 処理対象の動画ファイルがありません。")
        sys.exit(1)

    if len(videos) == 1:
        ok = process_video(videos[0], lang_code, translate_target, force_transcribe)
        sys.exit(0 if ok else 1)

    # 一括処理
    print(f"一括処理: {len(videos)} 本の動画を処理します。\n")
    failed = []
    for i, v in enumerate(videos, 1):
        print(f"=== [{i}/{len(videos)}] {v}")
        if not process_video(v, lang_code, translate_target, force_transcribe):
            failed.append(v)
        print()

    print(f"完了: {len(videos) - len(failed)}/{len(videos)} 本成功")
    if failed:
        print("失敗したファイル:")
        for v in failed:
            print(f"  {v}")
        sys.exit(1)


if __name__ == "__main__":
    main()
