from expression import Expression
from pain_parser import Parser
import sys
from typing import Any


def run_file(fname: str, env: dict[str, Any]) -> None:
    """
    >>> env = {}
    >>> run_file("test-scripts/simple_arithmetic.pain", env)
    >>> env
    {'test': 11}
    >>> env = {}
    >>> run_file("test-scripts/more_complex_arithmetic.pain", env)
    >>> env
    {'t': 432}
    """
    expressions: list[Expression] = []
    #filename = sys.argv[1]

    with open(fname) as f:
        contents = f.read()
        parser = Parser(contents)

        while True:
            expr = parser.parse_line()
            if expr is not None:
                expressions.append(expr)
            else:
                break

    for e in expressions:
        e.evaluate(env)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
