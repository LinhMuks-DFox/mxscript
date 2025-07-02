import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.frontend import TokenStream, tokenize, TokenType


def test_simple_tokenization():
    tokens = tokenize("let x = 10;")
    types = [t.type for t in tokens]
    values = [t.value for t in tokens]
    assert types[:5] == [TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INTEGER, TokenType.SEMICOLON]
    assert values[:5] == ["let", "x", "=", "10", ";"]
    assert tokens[-1].type == TokenType.EOF


def test_token_stream_navigation():
    tokens = tokenize("let x = 1;")
    stream = TokenStream(tokens)
    assert stream.peek().value == "let"
    stream.expect(TokenType.LET, "let")
    assert stream.next().type == TokenType.IDENTIFIER
    stream.expect(TokenType.ASSIGN, "=")
    stream.expect(TokenType.INTEGER, "1")
    stream.expect(TokenType.SEMICOLON, ";")
    assert stream.next().type == TokenType.EOF


def test_hash_comment():
    tokens = tokenize("# a comment\nlet x = 1;")
    tk_types = [t.type for t in tokens if t.type != TokenType.COMMENT]
    assert tk_types[:4] == [TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INTEGER]


def test_bang_hash_comment():
    src = "!#\n multi line\n#!\nlet x = 1;"
    tokens = tokenize(src)
    tk_types = [t.type for t in tokens if t.type != TokenType.COMMENT]
    assert tk_types[:4] == [TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.INTEGER]


def test_string_escape_sequences():
    src = "\"foo\\nbar\\t\\\"baz\\\"\\\\\""
    tokens = tokenize(src)
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == 'foo\nbar\t"baz"\\'


def test_control_flow_keywords_tokenization():
    src = "if else for in until do loop break continue;"
    tokens = tokenize(src)
    kw_tokens = [t.value for t in tokens if t.type in (
        TokenType.IF,
        TokenType.ELSE,
        TokenType.FOR,
        TokenType.IN,
        TokenType.UNTIL,
        TokenType.DO,
        TokenType.LOOP,
        TokenType.BREAK,
        TokenType.CONTINUE,
    )]
    assert kw_tokens[:9] == [
        "if",
        "else",
        "for",
        "in",
        "until",
        "do",
        "loop",
        "break",
        "continue",
    ]


def test_type_keywords_tokenization():
    src = "class interface override static";
    tokens = tokenize(src)
    words = [t.value for t in tokens if t.type in (TokenType.CLASS, TokenType.INTERFACE, TokenType.OVERRIDE, TokenType.STATIC)]
    assert "class" in words
    assert "interface" in words
    assert "override" in words
    assert "static" in words
