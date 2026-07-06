from srt_utils import parse_srt_blocks, build_srt


SIMPLE_SRT = """1
00:00:01,000 --> 00:00:03,000
Hello world

2
00:00:04,000 --> 00:00:06,000
Second line
"""


def test_parse_basic():
    blocks = parse_srt_blocks(SIMPLE_SRT)
    assert len(blocks) == 2
    assert blocks[0]["text"] == "Hello world"
    assert blocks[0]["timecode"] == "00:00:01,000 --> 00:00:03,000"
    assert blocks[1]["index"] == "2"


def test_parse_with_bom():
    blocks = parse_srt_blocks("﻿" + SIMPLE_SRT)
    assert len(blocks) == 2


def test_parse_crlf():
    blocks = parse_srt_blocks(SIMPLE_SRT.replace("\n", "\r\n"))
    assert len(blocks) == 2
    assert blocks[0]["text"] == "Hello world"


def test_parse_multiline_text():
    srt_text = """1
00:00:01,000 --> 00:00:03,000
Line one
Line two
"""
    blocks = parse_srt_blocks(srt_text)
    assert len(blocks) == 1
    assert blocks[0]["text"] == "Line one\nLine two"


def test_roundtrip():
    blocks = parse_srt_blocks(SIMPLE_SRT)
    rebuilt = build_srt(blocks)
    blocks2 = parse_srt_blocks(rebuilt)
    assert blocks == blocks2


def test_parse_empty():
    assert parse_srt_blocks("") == []
