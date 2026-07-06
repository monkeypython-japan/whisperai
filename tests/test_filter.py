from filter import filter_blocks


def _block(index, text, timecode="00:00:01,000 --> 00:00:02,000"):
    return {"index": str(index), "timecode": timecode, "text": text}


def test_removes_empty_blocks():
    blocks = [_block(1, ""), _block(2, "Hello")]
    result = filter_blocks(blocks)
    assert [b["text"] for b in result] == ["Hello"]


def test_removes_credit_patterns():
    blocks = [
        _block(1, "Sous-titrage MFP."),
        _block(2, "Subtitled by XYZ"),
        _block(3, "www.opensubtitles.org"),
        _block(4, "© 2020 Studio"),
        _block(5, "Real dialogue"),
    ]
    result = filter_blocks(blocks)
    assert [b["text"] for b in result] == ["Real dialogue"]


def test_removes_consecutive_duplicates():
    blocks = [
        _block(1, "I'm sorry."),
        _block(2, "I'm sorry."),
        _block(3, "I'm sorry."),
        _block(4, "Something else"),
        _block(5, "I'm sorry."),
    ]
    result = filter_blocks(blocks)
    assert [b["text"] for b in result] == ["I'm sorry.", "Something else", "I'm sorry."]


def test_removes_misparsed_blocks():
    blocks = [_block(1, "00:00:01,000 --> 00:00:02,000\nbroken"), _block(2, "OK")]
    result = filter_blocks(blocks)
    assert [b["text"] for b in result] == ["OK"]


def test_reindexes():
    blocks = [_block(5, "A"), _block(9, "B")]
    result = filter_blocks(blocks)
    assert [b["index"] for b in result] == ["1", "2"]


def test_keeps_normal_dialogue():
    blocks = [_block(1, "Hello"), _block(2, "How are you?")]
    result = filter_blocks(blocks)
    assert len(result) == 2
