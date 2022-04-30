from typing import Any, Optional, Union
from tokenizer import TokenType
import math


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

        >>> e = Error("Ammo Gus")
        >>> e.append("", 0)
        >>> e.append("", 1)
        >>> e.append("")
        >>> e.append("", 3)
        >>> e
        Traceback:
            Line 3
             ---
              Line 1
               Line 0
                Ammo Gus
        """
        out = ["Traceback:"]
        for i in range(1, len(self.traceback) + 1):
            msg = self.traceback[-i]
            if len(msg) == 0:
                out.append(f"{' ' * (i + 3)}---")
            else:
                out.append(f"{' ' * (i + 3)}{msg}")
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
                self.traceback.append(f"Line {origin}")


class Operators:
    def add(args: list[Union[int, float]],
            env: dict[str, Any]) -> Union[int, float, Error]:
        """
        Add two arguments in <args> and return their sum. <env> is ignored.

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be added
        """
        if len(args) != 2:
            return Error("ADD operator requires exactly 2 operands.")
        try:
            return args[0] + args[1]
        except TypeError as te:
            return Error(str(te))

    def sub(args: list[Union[int, float]],
            env: dict[str, Any]) -> Union[int, float, Error]:
        """
        Subtract two arguments in <args> (args[0] - args[1]) and return their
        difference. <env> is ignored.

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be subtracted
        """
        if len(args) != 2:
            return Error("SUB operator requires exactly 2 operands.")
        try:
            return args[0] - args[1]
        except TypeError as te:
            return Error(str(te))

    def mul(args: list[Union[int, float]],
            env: dict[str, Any]) -> Union[int, float, Error]:
        """
        Multiply two arguments in <args> and return their product. <env> is ignored.

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be multiplied
        """
        if len(args) != 2:
            return Error("MUL operator requires exactly 2 operands.")
        try:
            return args[0] * args[1]
        except TypeError as te:
            return Error(str(te))

    def div(args: list[Union[int, float]],
            env: dict[str, Any]) -> Union[int, float, Error]:
        """
        Divide two arguments in <args> (args[0] / args[1]) and return their
        quotient. <env> is ignored.

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be divided
            - args[1] is zero
        """
        if len(args) != 2:
            return Error("DIV operator requires exactly 2 operands.")
        try:
            return args[0] / args[1]
        except TypeError as te:
            return Error(str(te))
        except ZeroDivisionError as zde:
            return Error(str(zde))

    def grt(args: list[Any], env: dict[str, Any]) -> bool:
        """
        Compare two arguments in <args> (args[0] > args[1]) and return True iff
        args[0] > args[1].

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be compared
        """
        if len(args) != 2:
            return Error("GRT operator requires exactly 2 operands.")
        try:
            return args[0] > args[1]
        except TypeError as te:
            return Error(str(te))

    def geq(args: list[Any], env: dict[str, Any]) -> bool:
        """
        Compare two arguments in <args> (args[0] >= args[1]) and return True iff
        args[0] >= args[1].

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be compared
        """
        if len(args) != 2:
            return Error("GEQ operator requires exactly 2 operands.")
        try:
            return args[0] >= args[1]
        except TypeError as te:
            return Error(str(te))

    def les(args: list[Any], env: dict[str, Any]) -> bool:
        """
        Compare two arguments in <args> (args[0] < args[1]) and return True iff
        args[0] < args[1].

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be compared
        """
        if len(args) != 2:
            return Error("LES operator requires exactly 2 operands.")
        try:
            return args[0] < args[1]
        except TypeError as te:
            return Error(str(te))

    def leq(args: list[Any], env: dict[str, Any]) -> bool:
        """
        Compare two arguments in <args> (args[0] <= args[1]) and return True iff
        args[0] <= args[1].

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be compared
        """
        if len(args) != 2:
            return Error("LEQ operator requires exactly 2 operands.")
        try:
            return args[0] <= args[1]
        except TypeError as te:
            return Error(str(te))

    def ass(args: list[Any], env: dict[str, Any]) -> Optional[Error]:
        """
        Assign args[1] to args[0], using the assign method.

        Throws if:
            - <args> does not have exactly 2 objects
            - args[0] is not assignable (doesn't have callable attribute assign)
        """
        if len(args) != 2:
            return Error("ASSIGN operator requires exactly 2 operands.")
        if not hasattr(args[0], 'assign'):
            return Error("ASSIGN operator requires assignable left operand.")
        args[0].assign(args[1], env)

    def ret(args: list[Any], env: dict[str, Any]) -> Union['RetVal', Error]:
        """
        Return args[0] as a RetVal to signify the termination of a sequence with a
        returned value.

        Throws if:
            - <args> does not have exactly 1 object
        """
        if len(args) != 1:
            return Error("RETURN operator requires exactly 1 operand.")
        return RetVal(args[0])
    
    def _str(args: list[Any], env: dict[str, Any]) -> Union[str, Error]:
        """
        Return args[0] as a string.
        Throws if:
            - <args> does not have exactly 1 object
            - the object is not convertible to int
        """
        if len(args) != 1:
            return Error("STR operator requires exactly 1 operand.")
        try:
            return str(args[0])
        except TypeError as te:
            return Error(str(te))

    def _int(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return args[0] as a int.
        Throws if:
            - <args> does not have exactly 1 object
            - the object is not convertible to int
        """
        if len(args) != 1:
            return Error("INT operator requires exactly 1 operand.")
        try:
            return int(args[0])
        except TypeError as te:
            return Error(str(te))

    def _float(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return args[0] as a float.
        Throws if:
            - <args> does not have exactly 1 object
            - the object is not convertible to float
        """
        if len(args) != 1:
            return Error("FLOAT operator requires exactly 1 operand.")
        try:
            return float(args[0])
        except TypeError as te:
            return Error(str(te))

    def _bool(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return args[0] as a bool.
        Throws if:
            - <args> does not have exactly 1 object
            - the object is not convertible to bool
        """
        if len(args) != 1:
            return Error("BOOL operator requires exactly 1 operand.")
        try:
            return bool(args[0])
        except TypeError as te:
            return Error(str(te))

    def _not(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return the negation of args[0].
        Throws if:
            - <args> does not have exactly 1 object of type bool
        """
        if len(args) != 1:
            return Error("NOT operator requires exactly 1 operand.")
        try:
            return not bool(args[0])
        except TypeError as te:
            return Error(str(te))

    def _and(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return the "and" of args[0] and args[1].
        Throws if:
            - <args> does not have exactly 2 objects of type bool
        """
        if len(args) != 2:
            return Error("AND operator requires exactly 2 operands.")
        try:
            return bool(args[0]) and bool(args[1])
        except TypeError as te:
            return Error(str(te))

    def _or(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return the "or" of args[0] and args[1].
        Throws if:
            - <args> does not have exactly 2 objects of type bool
        """
        if len(args) != 2:
            return Error("OR operator requires exactly 2 operands.")
        try:
            return bool(args[0]) or bool(args[1])
        except TypeError as te:
            return Error(str(te))

    def _mod(args: list[Any], env: dict[str, Any]) -> Union[int, Error]:
        """
        Return the mod of args[0] when divided by args[1].
        Throws if:
            - <args> does not have exactly 2 objects
            - the object is not of type int or float
        """
        if len(args) != 2:
            return Error("MOD operator requires exactly 2 operand.")
        try:
            return args[0] % args[1]
        except TypeError as te:
            return Error(str(te))


# dict[str, tuple[bool, bool, Callable]]
# [id (one char), [has left operand, has right operand, operator function]]
OPERATORS = \
{
    TokenType.ADD: (True, True, Operators.add),
    TokenType.SUBTRACT: (True, True, Operators.sub),
    TokenType.MULTIPLY: (True, True, Operators.mul),
    TokenType.DIVIDE: (True, True, Operators.div),
    TokenType.GREATER_THAN: (True, True, Operators.grt),
    TokenType.GREATER_EQUAL: (True, True, Operators.geq),
    TokenType.LESS_THAN: (True, True, Operators.les),
    TokenType.LESS_EQUAL: (True, True, Operators.leq),
    TokenType.ASSIGN: (True, True, Operators.ass),
    TokenType.RETURN: (False, True, Operators.ret),
    TokenType.TO_INT: (False, True, Operators._int),
    TokenType.TO_FLOAT: (False, True, Operators._float),
    TokenType.TO_BOOL: (False, True, Operators._bool),
    TokenType.NOT: (False, True, Operators._not),
    TokenType.AND: (True, True, Operators._and),
    TokenType.OR: (True, True, Operators._or),
    TokenType.MOD: (True, True, Operators._mod)
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


    def __repr__(self) -> str:
        return f"Constant<{self.value}>"


    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Return the constant value held within this expression.
        <env> is ignored.

        No throw guarantee.

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

    def __repr__(self) -> str:
        return f"Name<{self.name}>"

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
        Return the value in <env> referred to by self.name.

        Throws if:
            - self.name is undefined.

        >>> env = {}
        >>> n = Name("x")
        >>> n.evaluate(env)
        Traceback:
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
    operator: TokenType
    r_operand: Optional[Expression]

    def __init__(self, l_operand: Optional[Expression], operator: TokenType,
                 r_operand: Optional[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.l_operand = l_operand
        self.operator = operator
        self.r_operand = r_operand


    def __repr__(self) -> str:
        return f"Operation<{self.l_operand}, {self.operator}, {self.r_operand}>"
    
    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Evaluate required operand sides (defined by operator), and pass the
        results to the operator referred to by self.operator. Return the result
        of the operator on the operands.

        Throws if:
            - self.operator is undefined
            - a required operand expression is None
            - a required operand expression fails to evaluate
            - the operator fails to evaluate

        >>> op = Operation(Constant(2), TokenType.ADD, Constant(2))
        >>> op.evaluate({})
        4

        >>> op = Operation(None, TokenType.ADD, Constant(2))
        >>> op.evaluate({})
        Traceback:
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
        
        result = operator[2](args, env)
        if isinstance(result, Error):
            result.append("", self.origin)
        return result


class RetVal(Constant):
    pass


class Block(Expression):
    """
    An executable sequence of expressions.
    """
    steps: list[Expression]

    def __init__(self, steps: list[Expression], origin: int = -1):
        Expression.__init__(self)
        self.steps = steps
    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Throws if:
            - any step fails to evaluate
        """
        for step in self.steps:
            result = step.evaluate(env)
            if isinstance(result, Error):
                result.append("", self.origin)
            return result


class IfBlock(Expression):
    """
    A block of (condition, Block) pairs.
    """
    steps: list[tuple[Expression, Block]]

    def __init__(self, steps: list[tuple[Expression, Expression]],
                 origin: int = -1):
        Expression.__init__(self, origin)
        self.steps = steps
    
    def evaluate(self, env: dict[str, Any]):
        """
        """
        for step in self.steps:
            cond = step[0].evaluate(env)
            if isinstance(cond, Error):
                cond.append("", self.origin)
                return cond
            if cond:
                result = step[1].evaluate(env.copy())
                if isinstance(result, Error):
                    result.append("", self.origin)
                return result


class Function(Expression):
    """
    An executable sequence of expressions that may take named parameters and
    may return a value.
    """
    params: list[str]
    code: Block

    def __init__(self, params: list[str], code: Block,
                 origin: int = -1):
        Expression.__init__(self, origin)
        self.params = params
        self.code = code
    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Function code is evaluated and its value is ignored, unless this value
        is an Error or RetVal. If a RetVal is encountered, execution is halted
        and the value is returned.

        Throws if:
            - function code fails to evaluate
        """
        result = self.code.evaluate(env.copy())
        if isinstance(result, Error):
            result.append("", self.origin)
        elif isinstance(result, RetVal):
            return result.evaluate(env)
        return result


class Invocation(Expression):
    """
            functio
    """
    func: str
    args: list[Expression]

    def __init__(self, func: str, args: list[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.args = args
        self.func = func
    
    def evaluate(self, env: dict[str, Any]) -> Any:
        """
        Evaluate all expressions in self.args, and pass results to the function
        in <env> referred to by self.func. Return the result of the function.

        Throws if:
            - self.func is undefined
            - self.func is not a function
            - any of self.args fail to evaluate
            - the number of arguments does not match the number of parameters
            required by the function
        """
        if self.func not in env:
            return Error(f"Function \'{self.func}\' is undefined.", self.origin)
        func = env[self.func]
        if not isinstance(func, Function):
            return Error(f"Symbol \'{self.func}\' is not a function.",
                         self.origin)
        
        args = []
        for arg in self.args:
            arg = arg.evaluate(env)
            if isinstance(arg, Error):
                arg.append("", self.origin)
                return arg
            args.append(arg)
        if len(args) != len(func.params):
            return Error(f"Function \'{self.func}\' requires exactly \
                           {len(func.params)} parameters.", self.origin)
        
        sub_env = env.copy()
        for (i, arg) in enumerate(args):
            sub_env[func.params[i]] = arg
        
        result = func.evaluate(sub_env)
        if isinstance(result, Error):
            result.append("", self.origin)
        return result

        

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    # def max(x, y):
    #     if x > y:
    #         return x
    #     else:
    #         return y
    _max = Function(['x', 'y'],
    Block([
        IfBlock(
        [
            (Operation(Name('x'), TokenType.GREATER_THAN, Name('y')), 
                Block(
                [
                    Operation(None, TokenType.RETURN, Name('x'))
                ])),
            (Constant(True),
                Block(
                [
                    Operation(None, TokenType.RETURN, Name('y'))
                ])),
        ])
    ]))
    ivk = Invocation("max", [Constant(4), Constant(3)])
    print(ivk.evaluate({ 'max': _max }))
