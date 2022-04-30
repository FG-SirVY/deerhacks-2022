from typing import Any, Optional, Union
from tokenizer import Token, TokenType


class Error:
    """

    """
    traceback: list[str]

    def __init__(self, traceback: list[str]):
        self.traceback = traceback
    
    def __repr__(self):
        return '\n'.join(self.traceback)

    def append(self, message: str, origin: int):
        if origin < 0:
            self.traceback.append(message)
        else:
            self.traceback.append(f"Line {origin}: {message}")


def add(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be added.
    Adds two arguments in <args> and return their sum.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error(["ADD operator requires exactly 2 arguments."])
    try:
        return args[0] + args[1]
    except TypeError as te:
        return Error([str(te)])


def sub(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be added.
    Subtracts two arguments in <args> and return their difference.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error(["SUB operator requires exactly 2 arguments."])
    try:
        return args[0] - args[1]
    except TypeError as te:
        return Error([str(te)])


def mul(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be added.
    Multiplies two arguments in <args> and return their product.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error(["MUL operator requires exactly 2 arguments."])
    try:
        return args[0] * args[1]
    except TypeError as te:
        return Error([str(te)])


def div(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be added.
    Divides two arguments in <args> and return their quotient.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error(["DIV operator requires exactly 2 arguments."])
    try:
        return args[0] / args[1]
    except TypeError as te:
        return Error([str(te)])
    except ZeroDivisionError as zde:
        return Error([str(zde)])


def assign(args: list[Any], env: dict[str, Any]) -> None:
    """
    Throws unless args[0] is assignable (hasattr(args[0]) == True) and args[1]
    exists.
    Assign a given value (args[1]) to a given reference (args[0]) in <env>.
    """
    if len(args) != 2:
        return Error(["ASSIGN operator requires exactly 2 arguments."])
    if not hasattr(args[0], 'assign'):
        return Error(["ASSIGN operator requires name as left operand."])
    args[0].assign(args[1], env)


# dict[str, tuple[bool, bool, Callable]]
# [id (one char), [has left operand, has right operand, operator function]]
OPERATORS = \
{
    TokenType.ADD: (True, True, add),
    TokenType.SUBTRACT: (True, True, sub),
    TokenType.MULTIPLY: (True, True, mul),
    TokenType.DIVIDE: (True, True, div),
    TokenType.ASSIGN: (True, True, assign)
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
    
    def evaluate(self, env: dict[str, Any]) -> Any:
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

    
    def __repr__(self):
        return f"Constant<c: {self.value}>"

    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Return the constant value held within this expression.
        <env> is ignored.

        >>> c = Constant('bruh')
        >>> c.evaluate({})
        'bruh'
        """
        return self.value


class Name(Expression):
    """
    """
    name: str

    def __init__(self, name: str, origin: int = -1):
        Expression.__init__(self, origin)
        self.name = name

    def assign(self, value: Any, env: dict[str, Any]) -> None:
        """
        Assign <value> to the name in env.

        >>> env = {}
        >>> n = Name("x")
        >>> n.assign(5, env)
        >>> n.evaluate(env)
        5
        """
        env[self.name] = value
    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Search <env> for a value associated with this name attribute.
        If not found, return an error indicating as such.
        If found, return the associated value.

        >>> env = {}
        >>> n = Name("x")
        >>> n.evaluate(env)
        Name 'x' not defined.
        >>> n.assign(5, env)
        >>> n.evaluate(env)
        5
        """
        if self.name not in env:
            error = Error([])
            error.append(f"Name \'{self.name}\' not defined.", self.origin)
            return error
        else:
            return env[self.name]


class Operation(Expression):
    """
    Expression which performs an operation on two operands.

    l_operand: Expression representing the left operand.
    operator: String representing the operator (must be capital ASCII letter)
    r_operand: Expression representing the right operand.
    """
    l_operand: Optional[Expression]
    operator: TokenType
    r_operand: Optional[Expression]


    def __init__(self, l_operand: Optional[Expression], operator: TokenType,
                 r_operand: Optional[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.l_operand = l_operand
        self.operator = operator
        self.r_operand = r_operand


    def __repr__(self):
        return f"Operation<l: {self.l_operand}, op: {self.operator}, r: {self.r_operand}>"


    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Search for self.operator in OPERATORS, evaluate l_operand and
        r_operand as needed, and return the value resulting from the operation.

        >>> op = Operation(Constant(2), TokenType.ADD, Constant(2))
        >>> op.evaluate({})
        4
        >>> op = Operation(None, TokenType.ADD, Constant(2))
        >>> op.evaluate({})
        Missing left operand.
        """
        if self.operator not in OPERATORS:
            error = Error([])
            error.append(f"Operator \'{self.operator}\' is invalid.",
                         self.origin)
            return error
        operator = OPERATORS[self.operator]
        args = []

        if operator[0]: # LEFT OPERAND
            if self.l_operand is None:
                error = Error([])
                error.append(f"Missing left operand.", self.origin)
                return error
            value = self.l_operand.evaluate(env)
            if isinstance(value, Error):
                value.append("", self.origin)
                return value
            args.append(value)
        
        if operator[1]: # RIGHT OPERAND
            if self.r_operand is None:
                error = Error([])
                error.append(f"Missing right operand.", self.origin)
                return error
            value = self.r_operand.evaluate(env)
            if isinstance(value, Error):
                value.append("", self.origin)
                return value
            args.append(value)
        
        return operator[2](args, env)


# epic_expr = Operation(Operation(Constant(3, 0), 'A', Constant(5, 0), 0), 'A', Constant(3, 0), 0)
# # equivalent:
# # 3 + 5 + 3
# print(epic_expr.evaluate())

if __name__ == "__main__":
    import doctest
    doctest.testmod()