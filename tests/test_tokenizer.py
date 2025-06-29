import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize


def test_simple_tokenization():
    tokens = tokenize("let x = 10;")
    types = [t.tk_type for t in tokens]
    values = [t.value for t in tokens]
    assert types[:5] == ["KEYWORD", "IDENTIFIER", "OPERATOR", "INTEGER", "OPERATOR"]
    assert values[:5] == ["let", "x", "=", "10", ";"]
    assert tokens[-1].tk_type == "EOF"


def test_token_stream_navigation():
    tokens = tokenize("let x = 1;")
    stream = TokenStream(tokens)
    assert stream.peek().value == "let"
    stream.expect("KEYWORD", "let")
    assert stream.next().tk_type == "IDENTIFIER"
    stream.expect("OPERATOR", "=")
    stream.expect("INTEGER", "1")
    stream.expect("OPERATOR", ";")
    assert stream.next().tk_type == "EOF"
