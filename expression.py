from typing import Any, Optional, Union


class InvalidOperator(Exception):
    pass
class InvalidOperand(Exception):
    pass


def throw_exception(origin: int, message: str, exc_type: Exception):
    """
    Throws exception of type <exc_type> with message <message>.
    The message will contain a line number <origin> at the front, if <origin>
    is not -1.
    """
    if origin < 0:
        raise exc_type(message)
    else:
        raise exc_type(f"Line {origin}: " + message)


def add(args: list[Union[int, float]]) -> Union[int, float]:
    """
    Add two arguments in <args>.
    If both are of type int, the sum is returned as an int.
    Otherwise, the sum is returned as a float.
    """
    if len(args) != 2:
        raise ValueError("add operator requires exactly 2 arguments")
    if isinstance(args[0], int) and isinstance(args[1], int):
        return args[0] + args[1]
    return float(args[0]) + float(args[1])


# dict[str, tuple[bool, bool, Callable]]
# [id (one char), [has left operand, has right operand, operator function]]
OPERATORS = \
{
    'A': (True, True, add)
}


class Expression:
    """
    Base class for an expression (do not use).

    origin: represents the line number this expression originated from
            (-1 if initialized on its own)
    """
    origin: int

    def __init__(self, origin: int = -1):
        self.origin = origin
    
    def evaluate(self) -> Any:
        raise NotImplementedError


class Constant(Expression):
    """
    Expression which holds a constant value.

    value: the value
    """
    value: Any
    
    def __init__(self, value: Any, origin: int = -1):
        Expression.__init__(self, origin)
        self.value = value
    
    def evaluate(self) -> Any:
        """
        Return the constant value held within this expression.
        """
        return self.value


class Operation(Expression):
    """
    Expression which performs an operation on two operands.

    l_operand: Expression representing the left operand.
    operator: String representing the operator (must be capital ASCII letter)
    r_operand: Expression representing the right operand.
    """
    l_operand: Optional[Expression]
    operator: str
    r_operand: Optional[Expression]

    def __init__(self, l_operand: Optional[Expression], operator: str,
                 r_operand: Optional[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.l_operand = l_operand
        self.operator = operator
        self.r_operand = r_operand
    
    def evaluate(self) -> Any:
        if self.operator not in OPERATORS:
            throw_exception(self.origin,
                            f"Operator {self.operator} is invalid.",
                            InvalidOperator)
        operator = OPERATORS[self.operator]
        args = []
        if operator[0]:
            if self.l_operand is None:
                throw_exception(self.origin, "Missing left operand",
                                InvalidOperand)
            args.append(self.l_operand.evaluate())
        if operator[1]:
            if self.r_operand is None:
                throw_exception(self.origin, "Missing right operand",
                                InvalidOperand)
            args.append(self.r_operand.evaluate())
        return operator[2](args)


epic_expr = Operation(Constant(5), 'A', Constant(3))
print(epic_expr.evaluate())
