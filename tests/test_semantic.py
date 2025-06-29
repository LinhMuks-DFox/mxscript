import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer, SemanticError


def analyze(src: str) -> None:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


def test_semantic_success():
    analyze("let x = 1; x + 2;")


def test_semantic_undefined():
    with pytest.raises(SemanticError):
        analyze("x + 1;")
