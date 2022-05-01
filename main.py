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
    >>> run_file("test-scripts/function_print_wrapper.pain", prepare_environment())
    Custom Print
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
    5.0
    5.0
    Test
    >>> run_file("test-scripts/min_max_print.pain", prepare_environment())
    6
    >>> run_file("test-scripts/complex_arithmetic_and_builtins.pain", prepare_environment())
    432
    >>> run_file("test-scripts/if_stmt.pain", prepare_environment())
    10
    >>> run_file("test-scripts/more_tests.pain", prepare_environment())
    print
    a is less than b
    >>> run_file("test-scripts/reuse_test.pain", prepare_environment())
    3
    >>> run_file("test-scripts/and.pain", prepare_environment())
    True
    False
    >>> run_file("test-scripts/or.pain", prepare_environment())
    True
    True
    >>> run_file("test-scripts/modulo.pain", prepare_environment())
    1
    >>> run_file("test-scripts/and_or.pain", prepare_environment())
    True
    False
    True
    >>> run_file("test-scripts/if_elif.pain", prepare_environment())
    4 == 4 (3)
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
        print(e)
        e.evaluate(env)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_file(sys.argv[1], prepare_environment())
    else:
        run_file("test-scripts/if_for_while.pain", prepare_environment())
        """import doctest
        doctest.testmod()"""
