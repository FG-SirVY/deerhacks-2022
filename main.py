from expression import Block, Builtin, Expression, Environment, Function, Name
from pain_parser import Parser
import sys


def prepare_environment() -> Environment:
    env = Environment({})
    env.local_vars["print"] = Function(["x"], Builtin(print, [Name("x")]))
    env.local_vars["min"] = Function(["x", "y"], Builtin(min, [Name("x"), Name("y")]))
    env.local_vars["max"] = Function(["x", "y"], Builtin(max, [Name("x"), Name("y")]))

    return env


def run_file(fname: str, env: Environment) -> None:
    """
    >>> env = Environment({})
    >>> run_file("test-scripts/simple_arithmetic.pain", env)
    >>> env.get_value("test")
    11
    >>> env = Environment({})
    >>> run_file("test-scripts/more_complex_arithmetic.pain", env)
    >>> env.get_value("t")
    432
    >>> run_file("test-scripts/print.pain", prepare_environment())
    5
    >>> run_file("test-scripts/min_max_print.pain", prepare_environment())
    6
    >>> run_file("test-scripts\complex_arithmetic_and_builtins.pain", prepare_environment())
    432
    """
    expressions: list[Expression] = []

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
