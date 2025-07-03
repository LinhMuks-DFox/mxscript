import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.frontend import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer, SemanticError



def analyze_source(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer


def test_default_param_positional():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(5); }'
    )
    analyze_source(src)


def test_default_param_override():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(5, 20); }'
    )
    analyze_source(src)


def test_keyword_arguments():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(a=5); }'
    )
    analyze_source(src)


def test_keyword_swapped():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(b=20, a=5); }'
    )
    analyze_source(src)


def test_missing_required():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(); }'
    )
    with pytest.raises(SemanticError):
        analyze_source(src)


def test_missing_positional():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(b=20); }'
    )
    with pytest.raises(SemanticError):
        analyze_source(src)


def test_unknown_keyword():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(c=10); }'
    )
    with pytest.raises(SemanticError):
        analyze_source(src)


def test_duplicate_argument():
    src = (
        'func test(a: int, b: int = 10) -> int { return a + b; }\n'
        'func main() -> int { return test(5, a=5); }'
    )
    with pytest.raises(SemanticError):
        analyze_source(src)

