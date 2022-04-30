from typing import Any, Optional, Union


class Error:
    """
    A traceback of errors.

    traceback: A list of errors, where the first item represents the origin of
        the error, and each subsequent error is one level higher.
    """
    traceback: list[str]

    def __init__(self, message: str = "", origin: int = -1):
        self.traceback = []
        if len(message) != 0:
            self.append(message, origin)
    
    def __repr__(self):
        """
        Return all traceback messages on separate lines, where each line starts
        with the same number of spaces as the level of the error in the
        expression tree.

        >>> e = Error("ADD operator requires exactly 2 arguments.")
        >>> e.append("", 0)
        >>> e.append("", 1)
        >>> e.append("")
        >>> e.append("", 3)
        >>> e
        Line 3:
         ---
          Line 1:
           Line 0:
            ADD operator requires exactly 2 arguments.
        """
        out = []
        for i in range(1, len(self.traceback) + 1):
            msg = self.traceback[-i]
            if len(msg) == 0:
                out.append(f"{' ' * (i - 1)}---")
            else:
                out.append(f"{' ' * (i - 1)}{msg}")
        return '\n'.join(out)

    def append(self, message: str, origin: int = -1):
        """
        Append an error to the traceback. If origin >= 0, include a line
        indicator at the start of the message.
        """
        if origin < 0:
            self.traceback.append(message)
        else:
            if len(message) != 0:
                self.traceback.append(f"Line {origin}: {message}")
            else:
                self.traceback.append(f"Line {origin}:")


def add(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be added.
    Adds two arguments in <args> and return their sum.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error("ADD operator requires exactly 2 arguments.")
    try:
        return args[0] + args[1]
    except TypeError as te:
        return Error(str(te))


def sub(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be subtracted.
    Subtracts two arguments in <args> and return their difference.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error("SUB operator requires exactly 2 arguments.")
    try:
        return args[0] - args[1]
    except TypeError as te:
        return Error(str(te))


def mul(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be multiplied.
    Multiplies two arguments in <args> and return their product.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error("MUL operator requires exactly 2 arguments.")
    try:
        return args[0] * args[1]
    except TypeError as te:
        return Error(str(te))


def div(args: list[Union[int, float]],
        env: dict[str, Any]) -> Union[int, float, Error]:
    """
    Throws unless <args> is a list of 2 objects.
    Throws unless both objects in <args> may be divided.
    Throws if args[1] is 0.
    Divides two arguments in <args> and return their quotient.
    <env> is ignored.
    """
    if len(args) != 2:
        return Error("DIV operator requires exactly 2 arguments.")
    try:
        return args[0] / args[1]
    except TypeError as te:
        return Error([str(te)])
    except ZeroDivisionError as zde:
        return Error(str(zde))


def assign(args: list[Any], env: dict[str, Any]) -> None:
    """
    Throws unless args[0] is assignable (hasattr(args[0]) == True) and args[1]
    exists.
    Assign a given value (args[1]) to a given reference (args[0]) in <env>.
    """
    if len(args) != 2:
        return Error("ASSIGN operator requires exactly 2 arguments.")
    if not hasattr(args[0], 'assign'):
        return Error("ASSIGN operator requires name as left operand.")
    args[0].assign(args[1], env)


# dict[str, tuple[bool, bool, Callable]]
# [id (one char), [has left operand, has right operand, operator function]]
OPERATORS = \
{
    '+': (True, True, add),
    '-': (True, True, sub),
    '*': (True, True, mul),
    '/': (True, True, div),
    '=': (True, True, assign)
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
            return Error(f"Name \'{self.name}\' not defined.", self.origin)
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
    operator: str
    r_operand: Optional[Expression]

    def __init__(self, l_operand: Optional[Expression], operator: str,
                 r_operand: Optional[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.l_operand = l_operand
        self.operator = operator
        self.r_operand = r_operand
    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Search for self.operator in OPERATORS, evaluate l_operand and
        r_operand as needed, and return the value resulting from the operation.

        >>> op = Operation(Constant(2), '+', Constant(2))
        >>> op.evaluate({})
        4

        >>> op = Operation(None, '+', Constant(2))
        >>> op.evaluate({})
        Missing left operand.
        """
        if self.operator not in OPERATORS:
            return Error(f"Operator \'{self.operator}\' is invalid.",
                         self.origin)
        operator = OPERATORS[self.operator]
        args = []

        if operator[0]: # LEFT OPERAND
            if self.l_operand is None:
                return Error(f"Missing left operand.", self.origin)
            value = self.l_operand.evaluate(env)
            if isinstance(value, Error):
                value.append("", self.origin)
                return value
            args.append(value)
        
        if operator[1]: # RIGHT OPERAND
            if self.r_operand is None:
                return Error(f"Missing right operand.", self.origin)
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