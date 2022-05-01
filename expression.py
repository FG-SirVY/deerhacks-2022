from typing import Any, Callable, Optional, Union
from tokenizer import TokenType


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


class Environment:
    """
    """
    parent_env: 'Environment'
    local_vars: dict[str, Any]

    def __init__(self, local_vars: dict[str, any], parent_env: 'Environment' = None):
        self.local_vars = local_vars
        self.parent_env = parent_env
    
    def get_parent_vars(self) -> list[str]:
        if self.parent_env is not None:
            return list(self.parent_env.local_vars.keys()) \
                + self.parent_env.get_parent_vars()
        return []
    
    def get_value(self, name: str) -> Any:
        if name in self.local_vars:
            return self.local_vars[name]
        elif self.parent_env is not None:
            return self.parent_env.get_value(name)
        return Error(f"Name \'{name}\' is not defined.")
    
    def get_dict_of(self, name: str) -> dict[str, Any]:
        if name in self.local_vars:
            return self.local_vars
        elif self.parent_env is not None:
            return self.parent_env.get_dict_of(name)
        return Error(f"Name \'{name}\' is not defined.")


class Operators:
    def add(args: list[Union[int, float]],
            env: Environment) -> Union[int, float, Error]:
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
            env: Environment) -> Union[int, float, Error]:
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
            env: Environment) -> Union[int, float, Error]:
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
            env: Environment) -> Union[int, float, Error]:
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

    def grt(args: list[Any], env: Environment) -> bool:
        """
        Compare two arguments in <args> (args[0] > args[1]) and return True iff
        args[0] > args[1]. <env> is ignored.

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

    def geq(args: list[Any], env: Environment) -> bool:
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

    def les(args: list[Any], env: Environment) -> bool:
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

    def leq(args: list[Any], env: Environment) -> bool:
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

    def ass(args: list[Any], env: Environment) -> Optional[Error]:
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

    def ret(args: list[Any], env: Environment) -> Union['RetVal', Error]:
        """
        Return args[0] as a RetVal to signify the termination of a function with a
        returned value.

        Throws if:
            - <args> does not have exactly 1 object
        """
        if len(args) != 1:
            return Error("RETURN operator requires exactly 1 operand.")
        return RetVal(args[0])
    
    def _str(args: list[Any], env: Environment) -> Union[str, Error]:
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

    def _int(args: list[Any], env: Environment) -> Union[int, Error]:
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

    def _float(args: list[Any], env: Environment) -> Union[int, Error]:
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

    def _bool(args: list[Any], env: Environment) -> Union[int, Error]:
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

    def _not(args: list[Any], env: Environment) -> Union[int, Error]:
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

    def _and(args: list[Any], env: Environment) -> Union[int, Error]:
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

    def _or(args: list[Any], env: Environment) -> Union[int, Error]:
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
    TokenType.OR: (True, True, Operators._or)
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
    
    def evaluate(self, env: Environment) -> Any:
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
    
    def evaluate(self, env: Environment) -> Any:
        """
        Return the constant value held within this expression.
        <env> is ignored.

        No throw guarantee.

        >>> c = Constant('bruh')
        >>> c.evaluate(Environment({}))
        'bruh'
        """
        return self.value


class Name(Expression):
    """
    Named reference to a variable in an environment.

    name: the name
    """
    name: str

    def __init__(self, name: str, origin: int = -1):
        Expression.__init__(self, origin)
        self.name = name

    def __repr__(self) -> str:
        return f"Name<{self.name}>"

    def assign(self, value: Any, env: Environment) -> None:
        """
        Assign <value> to the name in env.

        >>> env = Environment({})
        >>> name = Name('x')
        >>> name.assign(5, env)
        >>> name.evaluate(env)
        5
        """
        tgt_dict = env.get_dict_of(self.name)
        if isinstance(tgt_dict, Error):
            tgt_dict = env.local_vars
        tgt_dict[self.name] = value
    
    def evaluate(self, env: Environment) -> Any:
        """
        Return the value in <env> referred to by self.name.

        Throws if:
            - self.name is undefined.

        >>> env = Environment({})
        >>> n = Name("x")
        >>> n.evaluate(env)
        Traceback:
            ---
             Name 'x' is not defined.
        >>> n.assign(5, env)
        >>> n.evaluate(env)
        5
        """
        val = env.get_value(self.name)
        if isinstance(val, Error):
            val.append("", self.origin)
        return val


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
    
    def evaluate(self, env: Environment) -> Any:
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
        >>> op.evaluate(Environment({}))
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

    steps: the sequence of expressions to be executed
    """
    steps: list[Expression]

    def __init__(self, steps: list[Expression], origin: int = -1):
        Expression.__init__(self)
        self.steps = steps

    def __repr__(self) -> str:
        return f"Block<{self.steps}>"
    
    def evaluate(self, env: Environment) -> Any:
        """
        Step through expressions in self.steps and evaluate them.
        If any expression evaluates to a RetVal, this result is returned
        immediately and execution halts.

        Throws if:
            - any step fails to evaluate
        
        >>> env = Environment({})
        >>> blk = Block([ \
                Operation(Constant(Name('x')), TokenType.ASSIGN, Constant(5)), \
                Operation(None, TokenType.RETURN, Name('x')) \
            ])
        >>> blk.evaluate(env).evaluate(env)
        5
        """
        for step in self.steps:
            result = step.evaluate(env)
            if isinstance(result, Error):
                result.append("", self.origin)
                return result
            elif isinstance(result, RetVal):
                return result


class IfBlock(Expression):
    """
    A branch where the execution of each block is contingent on its associated
    expression evaluating to True. If it is False, the next condition is
    checked.
    """
    steps: list[tuple[Expression, Block]]

    def __init__(self, steps: list[tuple[Expression, Expression]],
                 origin: int = -1):
        Expression.__init__(self, origin)
        self.steps = steps

    def __repr__(self) -> str:
        return f"IfBlock<{self.steps}>"
    
    def evaluate(self, env: Environment):
        """
        """
        for step in self.steps:
            cond = step[0].evaluate(env)
            if isinstance(cond, Error):
                cond.append("", self.origin)
                return cond
            if not isinstance(cond, bool):
                try:
                    cond = bool(cond)
                except TypeError as te:
                    return Error(str(te))
            if cond:
                result = step[1].evaluate(Environment({}, env))
                if isinstance(result, Error):
                    result.append("", self.origin)
                return result


class WhileLoop(Expression):
    """
    """
    cond: Expression
    code: Block

    def __init__(self, cond: Expression, code: Block, origin: int = -1):
        Expression.__init__(self, origin)
        self.cond = cond
        self.code = code
    
    def evaluate(self, env: Environment):
        """
        """
        while True:
            cond = self.cond.evaluate(env)
            if isinstance(cond, Error):
                cond.append("", self.origin)
                return cond
            if not cond:
                break
            result = self.code.evaluate(Environment({}, env))
            if isinstance(result, Error):
                result.append("", self.origin)
                return result
            elif isinstance(result, RetVal):
                return result


class ForLoop(Expression):
    """
    """
    first: Expression
    cond: Expression
    on_rpt: Expression
    code: Block

    def __init__(self, first: Expression, cond: Expression, on_rpt: Expression, 
                 code: Block, origin: int = -1):
        Expression.__init__(self, origin)
        self.first = first
        self.cond = cond
        self.on_rpt = on_rpt
        self.code = code

    def evaluate(self, env: Environment) -> Any:
        """
        """
        loop_env = Environment({}, env)
        result = self.first.evaluate(loop_env)
        if isinstance(result, Error):
            result.append("", self.origin)
            return result
        elif isinstance(result, RetVal):
            return result
        
        while True:
            cond = self.cond.evaluate(loop_env)
            if isinstance(cond, Error):
                cond.append("", self.origin)
                return cond
            if not cond:
                break

            result = self.code.evaluate(Environment({}, env))
            if isinstance(result, Error):
                result.append("", self.origin)
                return result
            elif isinstance(result, RetVal):
                return result
            
            result = self.on_rpt.evaluate(loop_env)
            if isinstance(result, Error):
                result.append("", self.origin)
                return result
            elif isinstance(result, RetVal):
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

    def __repr__(self) -> str:
        return f"Function<{self.params}, {self.code}>"
    
    def evaluate(self, env: Environment) -> Any:
        """
        Function code is evaluated and its value is ignored, unless this value
        is an Error or RetVal. If a RetVal is encountered, execution is halted
        and the value is returned.

        Throws if:
            - function code fails to evaluate
        """
        result = self.code.evaluate(Environment({}, env))
        if isinstance(result, Error):
            result.append("", self.origin)
            return result
        elif isinstance(result, RetVal):
            return result.evaluate(env)
    

class Builtin(Expression):
    """
    """
    func: Callable
    args: list[Expression]

    def __init__(self, func: Callable, args: list[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.func = func
        self.args = args
    
    def evaluate(self, env: Environment) -> Any:
        """
        """
        args = []
        for arg in self.args:
            arg = arg.evaluate(env)
            if isinstance(arg, Error):
                arg.append("", self.origin)
                return arg
            args.append(arg)
        try:
            result = self.func(*args)
        except Exception as e:
            return Error(str(e), self.origin)
        if isinstance(result, Error):
            result.append("", self.origin)
            return result
        return RetVal(result)


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

    def __repr__(self) -> str:
        return f"Invocation<{self.func}, {self.args}>"
    
    def evaluate(self, env: Environment) -> Any:
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
        func = env.get_value(self.func)
        if isinstance(func, Error):
            func.append("", self.origin)
            return func
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
        
        sub_env = Environment({}, env)
        for (i, arg) in enumerate(args):
            sub_env.local_vars[func.params[i]] = arg
        
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
        Operation(Constant(Name('z')), TokenType.ASSIGN, Constant(0)),
        IfBlock(
        [
            (Operation(Name('x'), TokenType.GREATER_THAN, Name('y')), 
                Block(
                [
                    Operation(Constant(Name('z')), TokenType.ASSIGN, Name('x')),
                    Builtin(print, [Name('z')])
                ])),
            (Constant(True),
                Block(
                [
                    Operation(Constant(Name('z')), TokenType.ASSIGN, Name('y')),
                    Builtin(print, [Name('z')])
                ])),
        ]),
        Operation(None, TokenType.RETURN, Name('z')),
    ]))
    ivk = Invocation("max", [Constant(1), Constant(8)])
    print(ivk.evaluate(Environment({ 'max': _max })))
