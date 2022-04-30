from typing import Any, Optional, Union


class Error:
    """
    """
    traceback: list[str]

    def __init__(self, traceback: list[str] = []):
        self.traceback = traceback
    
    def __str__(self):
        return '\n'.join(self.traceback)

    def append(self, message: str, origin: int):
        if origin < 0:
            self.traceback.append(message)
        else:
            self.traceback.append(f"Line {origin}: {message}")


def add(args: list[Union[int, float]]) -> Union[int, float, Error]:
    """
    Add two arguments in <args>.
    If both are of type int, the sum is returned as an int.
    Otherwise, the sum is returned as a float.
    """
    if len(args) != 2:
        return Error([f"Add operator requires exactly 2 arguments."])
    # TODO: Add type check
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
            error = Error()
            error.append(f"Operator {self.operator} is invalid.", self.origin)
            return error
        operator = OPERATORS[self.operator]
        args = []
        if operator[0]:
            if self.l_operand is None:
                error = Error()
                error.append(f"Missing left operand", self.origin)
                return error
            value = self.l_operand.evaluate()
            if isinstance(value, Error):
                value.append("", self.origin)
                return value
            args.append(value)
        if operator[1]:
            if self.r_operand is None:
                error = Error()
                error.append(f"Missing right operand", self.origin)
                return error
            value = self.r_operand.evaluate()
            if isinstance(value, Error):
                value.append("", self.origin)
                return value
            args.append(value)
        return operator[2](args)


epic_expr = Operation(Operation(Constant(3, 0), 'A', Constant(5, 0), 0), 'A', Constant(3, 0), 0)
# equivalent:
# 3 + 5 + 3
print(epic_expr.evaluate())
