from typing import Any, Callable, Optional, Union
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
             Line 1
              Line 0
               Ammo Gus
        """
        out = ["Traceback:"]
        indent = 4
        for i in range(1, len(self.traceback) + 1):
            msg = self.traceback[-i]
            if len(msg) != 0:
                out.append(f"{' ' * indent}{msg}")
                indent += 1
        return '\n'.join(out)

    def append(self, message: str, origin: int = -1):
        """
        Append an error to the traceback. If origin >= 0, include a line
        indicator at the start of the message.

        >>> e = Error()
        >>> e.append("hi", 0)
        >>> e.append("", 1)
        >>> e.append("yo", -1)
        >>> e
        Traceback:
            yo
             Line 1
              Line 0: hi
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
    Environment that holds local named variables, and an optional reference to
    a parent environment.
    """
    parent_env: 'Environment'
    local_vars: dict[str, Any]

    def __init__(self, local_vars: dict[str, any], parent_env: 'Environment' = None):
        self.local_vars = local_vars
        self.parent_env = parent_env
    
    def get_value(self, name: str) -> Any:
        """
        Searches for <name> in <local_vars>. If not found, it then searches
        the parent environment recursively.
        If <name> is located somewhere, its associated value is returned.

        Throws if:
            - <name> is undefined in both local_vars and parent_env
        
        >>> env1 = Environment({'a': 1, 'b': 2})
        >>> env2 = Environment({'c': 3}, env1)
        >>> env1.get_value('a')
        1
        >>> env2.get_value('a')
        1
        >>> env2.get_value('c')
        3
        >>> env1.get_value('c')
        Traceback:
            Name 'c' is not defined.
        """
        if name in self.local_vars:
            return self.local_vars[name]
        elif self.parent_env is not None:
            return self.parent_env.get_value(name)
        return Error(f"Name \'{name}\' is not defined.")
    
    def get_dict_of(self, name: str) -> dict[str, Any]:
        """
        Searches for <name> in <local_vars>. If not found, it then searches
        the parent environment recursively.
        If <name> is located somewhere, its containing dictionary is returned.

        >>> env1 = Environment({'a': 1, 'b': 2})
        >>> env2 = Environment({'c': 3}, env1)
        >>> env1.get_dict_of('a')
        {'a': 1, 'b': 2}
        >>> env2.get_dict_of('a')
        {'a': 1, 'b': 2}
        >>> env2.get_dict_of('c')
        {'c': 3}
        >>> env1.get_dict_of('c')
        Traceback:
            Name 'c' is not defined.
        """
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
    
    def mod(args: list[Any], env: Environment) -> Any:
        """
        Divide two arguments in <args> (args[0] / args[1]) and return their
        remainder. <env> is ignored.

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be divided with remainder
            - args[1] is zero
        """
        if len(args) != 2:
            return Error("MOD operator requires exactly 2 operands.")
        try:
            return args[0] % args[1]
        except TypeError as te:
            return Error(str(te))
        except ZeroDivisionError as zde:
            return Error(str(zde))

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
    
    def eql(args: list[Any], env: Environment) -> bool:
        """
        Compare two arguments in <args> (args[0] == args[1]) and return True iff
        args[0] == args[1]. <env> is ignored.

        Throws if:
            - <args> does not have exactly 2 objects
            - objects in <args> may not be compared
        """
        if len(args) != 2:
            return Error("EQL operator requires exactly 2 operands.")
        try:
            return args[0] == args[1]
        except TypeError as te:
            return Error(str(te))

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
        if len(args) != 1:
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
        if len(args) != 1:
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
    TokenType.MOD: (True, True, Operators.mod),
    TokenType.EQUAL: (True, True, Operators.eql),
    TokenType.GREATER_THAN: (True, True, Operators.grt),
    TokenType.GREATER_EQUAL: (True, True, Operators.geq),
    TokenType.LESS_THAN: (True, True, Operators.les),
    TokenType.LESS_EQUAL: (True, True, Operators.leq),
    TokenType.ASSIGN: (True, True, Operators.ass),
    TokenType.RETURN: (False, True, Operators.ret),
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
    A branch where the execution of each block is dependent on its associated
    expression evaluating to True. If it is False, the next condition is
    checked.
    """
    steps: list[tuple[Expression, Block]]

    def __init__(self, steps: list[tuple[Expression, Expression]],
                 origin: int = -1):
        Expression.__init__(self, origin)
        self.steps = steps
    
    def evaluate(self, env: Environment):
        """
        Evaluate condition for first step, and continue if the condition is
        False until a condition evaluates to True, or until the end is reached.

        Throws if:
            - a condition fails to evaluate
            - a condition evaluates to a non bool type, and the type cannot be
                converted to a bool
            - a block fails to evaluate
        
        >>> blk = \
        IfBlock( \
        [ \
            (Operation(Name('x'), TokenType.GREATER_THAN, Constant(3)), \
                Operation(Constant(Name('x')), TokenType.ASSIGN, Constant(1))),\
            (Operation(Name('x'), TokenType.GREATER_THAN, Constant(2)), \
                Operation(Constant(Name('x')), TokenType.ASSIGN, Constant(2))),\
            (Constant(True), \
                Operation(Constant(Name('x')), TokenType.ASSIGN, Constant(3))) \
        ])
        >>> env = Environment({'x': 4})
        >>> blk.evaluate(env)
        >>> env.get_value('x')
        1
        >>> env = Environment({'x': 3})
        >>> blk.evaluate(env)
        >>> env.get_value('x')
        2
        >>> env = Environment({'x': 2})
        >>> blk.evaluate(env)
        >>> env.get_value('x')
        3
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
    A loop that executes a code block as long as its condition evaluates to
    True.

    cond: the condition that continues loop execution
    code: the code block to be executed
    """
    cond: Expression
    code: Block

    def __init__(self, cond: Expression, code: Block, origin: int = -1):
        Expression.__init__(self, origin)
        self.cond = cond
        self.code = code
    
    def evaluate(self, env: Environment):
        """
        If <cond> evaluates to True, execute <code> and repeat until <cond>
        evaluates to False.

        Throws if:
            - the condition fails to evaluate
            - the condition evaluates to a non bool type, and the type cannot be
                converted to a bool
            - the code block fails to execute
        
        >>> b_print = Function(['x'], Block([Builtin(print, [Name('x')])]))
        >>> loop = \
        WhileLoop(Operation(Name('n'), TokenType.GREATER_THAN, Constant(0)), \
        Block([ \
            Invocation('b_print', [Name('n')]), \
            Operation(Constant(Name('n')), TokenType.ASSIGN, \
                      Operation(Name('n'), TokenType.SUBTRACT, Constant(1))) \
        ]))
        >>> loop.evaluate(Environment({'n': 5, 'b_print': b_print}))
        5
        4
        3
        2
        1
        """
        while True:
            if self.cond is not None:
                cond = self.cond.evaluate(env)
                if isinstance(cond, Error):
                    cond.append("", self.origin)
                    return cond
                if not isinstance(cond, bool):
                    try:
                        cond = bool(cond)
                    except TypeError as te:
                        return Error(str(te))
                if not cond:
                    break
            if self.code is not None:
                result = self.code.evaluate(Environment({}, env))
                if isinstance(result, Error):
                    result.append("", self.origin)
                    return result
                elif isinstance(result, RetVal):
                    return result


class ForLoop(Expression):
    """
    This loop only executes as long as the condition evaluated before loop
    execution is True.

    first: the expression evaluated before the loop begins
    cond: the expression evaluated before each loop iteration, and that must
        evaluate to True in order for the loop to iterate
    on_rpt: the expression evaluated after each loop iteration
    code: the code block executed each iteration
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
        Execute self.first.
        Execute self.cond. If self.cond evaluates to True, execute self.code.
        Then, execute self.on_rpt. Repeat from 2nd line until self.cond is
        False.

        Throws if:
            - self.first fails to evaluate
            - self.cond fails to evaluate
            - self.cond evaluates to a non bool type, and the type cannot be
                converted to a bool
            - self.on_rpt fails to evaluate
            - self.code fails to evaluate
        
        >>> b_print = Function(['x'], Block([Builtin(print, [Name('x')])]))
        >>> l = \
        ForLoop(Operation(Constant(Name('i')), TokenType.ASSIGN, \
                          Constant(0)), \
                Operation(Name('i'), TokenType.LESS_THAN, \
                          Constant(5)), \
                Operation(Constant(Name('i')), TokenType.ASSIGN, \
                          Operation(Name('i'), TokenType.ADD, Constant(1))), \
                Block([ \
                    Invocation('b_print', [Name('i')]) \
                ]))
        >>> l.evaluate(Environment({'b_print': b_print}))
        0
        1
        2
        3
        4
        """
        loop_env = Environment({}, env)
        if self.first is not None:
            result = self.first.evaluate(loop_env)
            if isinstance(result, Error):
                result.append("", self.origin)
                return result
            elif isinstance(result, RetVal):
                return result
        while True:
            if self.cond is not None:
                cond = self.cond.evaluate(loop_env)
                if isinstance(cond, Error):
                    cond.append("", self.origin)
                    return cond
                if not isinstance(cond, bool):
                    try:
                        cond = bool(cond)
                    except TypeError as te:
                        return Error(str(te))
                if not cond:
                    break
            
            if self.code is not None:
                result = self.code.evaluate(loop_env)
                if isinstance(result, Error):
                    result.append("", self.origin)
                    return result
                elif isinstance(result, RetVal):
                    return result
            
            if self.on_rpt is not None:
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
    
    """
    func: str
    args: list[Expression]

    def __init__(self, func: str, args: list[Expression], origin: int = -1):
        Expression.__init__(self, origin)
        self.args = args
        self.func = func
    
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

# garbage recursive fibonacci algorithm
fn_fib = Function(['n'], Block(
[
    IfBlock(
    [
        (Operation(Name('n'), TokenType.LESS_EQUAL, Constant(2)), Block(
        [
            Operation(None, TokenType.RETURN, Constant(1))
        ])),
        (Constant(True), Block(
        [
            Operation(None, TokenType.RETURN, Operation(
                Invocation('fib', [Operation(Name('n'), TokenType.SUBTRACT,
                                             Constant(1))]),
                TokenType.ADD,
                Invocation('fib', [Operation(Name('n'), TokenType.SUBTRACT,
                                             Constant(2))]),
            )),
        ])),
    ]),
]), 1)
ivk = Invocation('fib', [Constant(10)], 0)
print(ivk.evaluate(Environment({'fib': fn_fib})))

if __name__ == "__main__":
    import doctest
    doctest.testmod()