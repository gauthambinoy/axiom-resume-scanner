from app.utils.text_processing import (
    clean_text,
    tokenize_sentences,
    tokenize_bullets,
    count_words,
    extract_numbers,
    calculate_readability,
)


def test_clean_text_strips_html():
    assert clean_text("<b>Hello</b> world") == "Hello world"


def test_clean_text_normalizes_unicode():
    result = clean_text("\u201cHello\u201d \u2013 world")
    assert '"' in result
    assert "-" in result


def test_clean_text_removes_zero_width():
    assert clean_text("Hello\u200bWorld") == "HelloWorld"


def test_clean_text_normalizes_whitespace():
    assert clean_text("Hello   world   foo") == "Hello world foo"


def test_tokenize_sentences():
    text = "Hello world. This is a test. Another sentence here."
    sentences = tokenize_sentences(text)
    assert len(sentences) >= 2


def test_tokenize_bullets():
    text = "- First bullet\n- Second bullet\n- Third bullet"
    bullets = tokenize_bullets(text)
    assert len(bullets) == 3
    assert bullets[0] == "First bullet"


def test_tokenize_bullets_various_markers():
    text = "• Bullet one\n* Bullet two\n▪ Bullet three"
    bullets = tokenize_bullets(text)
    assert len(bullets) == 3


def test_count_words():
    assert count_words("Hello world foo bar") == 4
    assert count_words("") == 0
    assert count_words("   ") == 0


def test_extract_numbers_percentages():
    numbers = extract_numbers("Improved performance by 45% and reduced costs by 20%")
    pcts = [n for n in numbers if n.number_type == "percentage"]
    assert len(pcts) >= 2


def test_extract_numbers_multipliers():
    numbers = extract_numbers("Achieved a 3x improvement in throughput")
    mults = [n for n in numbers if n.number_type == "multiplier"]
    assert len(mults) >= 1


def test_calculate_readability():
    text = "This is a simple sentence. Here is another one. And a third."
    result = calculate_readability(text)
    assert result.avg_sentence_length > 0
    assert result.avg_word_length > 0


def test_empty_inputs():
    assert clean_text("") == ""
    assert tokenize_sentences("") == []
    assert tokenize_bullets("") == []
    assert count_words("") == 0
    assert extract_numbers("") == []
