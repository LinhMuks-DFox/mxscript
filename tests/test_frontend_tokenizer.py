import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.frontend.tokenization import Tokenizer, tokenize
from src.frontend.tokens import TokenType


def test_basic_tokens():
    tokens = tokenize("let x = 10;")
    types = [t.type for t in tokens]
    assert types[0] == TokenType.LET
    assert types[1] == TokenType.IDENTIFIER
    assert types[2] == TokenType.ASSIGN
    assert types[3] == TokenType.INTEGER
    assert types[4] == TokenType.SEMICOLON
    assert tokens[-1].type == TokenType.EOF


def test_string_escapes():
    src = "\"foo\\nbar\\t\\\"baz\\\"\\\\\""
    tokens = tokenize(src)
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == 'foo\nbar\t"baz"\\'

