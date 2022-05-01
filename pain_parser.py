from expression import Block, Expression, Function, IfBlock, Invocation, Name, Operation, Constant, Environment, ForLoop, WhileLoop
from tokenizer import Tokenizer, TokenType, Token


class Parser:
    """
    Parse a string using Tokenizer into a tree of Expressions.
    """
    tokenizer: Tokenizer


    def __init__(self, script: str) -> None:
        """
        Initialize the Tokenizer on the given script.
        """
        self.tokenizer = Tokenizer(script)

    
    def get_as_expression(self, token: Token) -> Expression:
        """
        Turn a token into token.

        Possible for float, int and string tokens.
        """
        if token.is_token_type(TokenType.FLOAT) or token.is_token_type(TokenType.INT) \
            or token.is_token_type(TokenType.STRING):
            return Constant(token.payload)
        elif token.is_token_type(TokenType.NAME):
            return Name(token.payload)

        raise Exception(f"Cannot map token of type {token.token_type} directly to Expression")


    def parse_unitary_operator(self) -> Expression:
        """
        Parse an operator which only has one operand to the right of it.
        """
        operator = self.tokenizer.get_next_token().token_type
        return Operation(None, operator, self.parse_line())


    def parse_parentheses(self) -> Expression:
        """
        Parse a set of parentheses (Highest priority),
        or just return the value if there are no parentheses.
        """
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.OPEN_PAR):
            self.tokenizer.get_next_token()
            term = self.parse_comparison()
            self.tokenizer.get_next_token()
            return term
        else:
            return self.get_as_expression(self.tokenizer.get_next_token())


    def parse_mul_div(self) -> Expression:
        """
        Parse multiplication, division or modulo arithmetic.
        """
        l_operand = self.parse_parentheses()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.MULTIPLY) \
            or next_token.is_token_type(TokenType.DIVIDE) \
            or next_token.is_token_type(TokenType.MOD):
            operator = self.tokenizer.get_next_token().token_type

            return Operation(l_operand, operator, self.parse_mul_div())
        else:
            return l_operand


    def parse_add_sub(self) -> Expression:
        """
        Parse addition or subtraction.
        """
        l_operand = self.parse_mul_div()
        next_token = self.tokenizer.peek_next_token()
        
        if next_token.is_token_type(TokenType.ADD) \
            or next_token.is_token_type(TokenType.SUBTRACT):

            operator = self.tokenizer.get_next_token().token_type
            return Operation(l_operand, operator, self.parse_add_sub())
        else:
            return l_operand


    def parse_invocation(self) -> Expression:
        """
        Parse a function invocation.
        """
        l_operand = self.parse_add_sub()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.OPEN_PAR):
            self.tokenizer.get_next_token()
            arguments = []
            next_operator = TokenType.COMMA
            while next_operator == TokenType.COMMA:
                arguments.append(self.parse_line())
                next_operator = self.tokenizer.get_next_token().token_type

            assert next_operator == TokenType.CLOSING_PAR

            return Invocation(l_operand.name, arguments)
        else:
            return l_operand

    
    def parse_term(self) -> Expression:
        """
        Decide whether to parse with a unitary operator or a binary one.
        """
        left = self.tokenizer.peek_next_token()

        if left.is_operator():
            return self.parse_unitary_operator()
        else:
            return self.parse_invocation()


    def parse_comparison(self) -> Expression:
        """
        Parse a binary comparison.
        """
        l_operand = self.parse_term()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.EQUAL) \
            or next_token.is_token_type(TokenType.LESS_EQUAL) \
            or next_token.is_token_type(TokenType.LESS_THAN) \
            or next_token.is_token_type(TokenType.GREATER_EQUAL) \
            or next_token.is_token_type(TokenType.GREATER_THAN):

            operator = self.tokenizer.get_next_token().token_type
            return Operation(l_operand, operator, self.parse_comparison())
        else:
            return l_operand

    
    def parse_and(self) -> Expression:
        """
        Parse boolean and connective.
        """
        l_operand = self.parse_comparison()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.AND):
            operator = self.tokenizer.get_next_token().token_type
            return Operation(l_operand, operator, self.parse_and())
        else:
            return l_operand

    
    def parse_or(self) -> Expression:
        """
        Parse boolean or connective.
        """
        l_operand = self.parse_and()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.OR):
            operator = self.tokenizer.get_next_token().token_type
            return Operation(l_operand, operator, self.parse_or())
        else:
            return l_operand

    
    def parse_assignment(self) -> Expression:
        """
        Parse an assignment statement.
        """
        l_operand = self.parse_or()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.ASSIGN):
            operator = self.tokenizer.get_next_token().token_type
            assert isinstance(l_operand, Name)
            return Operation(Constant(l_operand), operator, self.parse_assignment())
        else:
            return l_operand


    def parse_block(self) -> Expression:
        """
        Parse a block statement (which will have its own environment).
        """
        next_token = self.tokenizer.get_next_token()
        assert next_token.is_token_type(TokenType.OPEN_BLOCK)

        expressions = []
        expr = self.parse_line()

        while expr is not None:
            expressions.append(expr)
            expr = self.parse_line()

        assert self.tokenizer.get_next_token().is_token_type(TokenType.CLOSING_BLOCK)

        return Block(expressions)


    def parse_conditional(self, has_cond=False) -> Expression:
        """
        Parse an "if" conditional statement.
        """
        self.tokenizer.get_next_token()
        condition = self.parse_line() if has_cond else Constant(True)
        block = self.parse_block()
        branches = [(condition, block)]
        
        right = self.tokenizer.peek_next_token()
        while right.is_token_type(TokenType.EOL) \
            or right.is_token_type(TokenType.CLOSING_BLOCK):
            self.tokenizer.get_next_token()
            right = self.tokenizer.peek_next_token()
        
        if has_cond:
            if right.is_token_type(TokenType.ELIF):
                branches += self.parse_conditional(True).steps
            elif right.is_token_type(TokenType.ELSE):
                branches += self.parse_conditional(False).steps
        
        return IfBlock(branches)
    

    def parse_while_loop(self) -> Expression:
        """
        Parse a while loop.
        """
        self.tokenizer.get_next_token()
        condition = self.parse_line()
        block = self.parse_block()
        return WhileLoop(condition, block)


    def parse_for_loop(self) -> Expression:
        """
        Parse an ordinary for loop.
        """
        self.tokenizer.get_next_token()
        next_token = self.tokenizer.get_next_token()
        assert next_token.is_token_type(TokenType.OPEN_BLOCK)
        
        cond_exprs = []
        expr = self.parse_line()
        while expr is not None:
            cond_exprs.append(expr)
            expr = self.parse_line()
        assert len(cond_exprs) == 3

        self.tokenizer.get_next_token()

        block = self.parse_block()
        return ForLoop(cond_exprs[0], cond_exprs[1], cond_exprs[2], block)


    def parse_function_declaration(self) -> Expression:
        """
        Parse the declaration of a function.
        """
        self.tokenizer.get_next_token()

        params = []
        while self.tokenizer.peek_next_token().token_type != TokenType.OPEN_BLOCK:
            name = self.tokenizer.get_next_token()
            assert name.is_token_type(TokenType.NAME)
            params.append(name.payload)

        block = self.parse_block()

        return Constant(Function(params, block))


    def parse_line(self) -> Expression:
        """
        # TODO: Error handling
        Parse one line. FINALLY.

        >>> p = Parser("5 A 6")
        >>> tree = p.parse_line()
        >>> tree
        Operation<Constant<5>, TokenType.ADD, Constant<6>>
        >>> tree.evaluate({})
        11
        >>> p = Parser("5 A 6 B 3")
        >>> tree = p.parse_line()
        >>> tree
        Operation<Constant<5>, TokenType.ADD, Operation<Constant<6>, TokenType.ADD, Constant<3>>>
        >>> tree.evaluate({})
        14
        >>> Parser("3 C )5 B 6(").parse_line().evaluate({})
        33
        >>> Parser("5 C 6").parse_line().evaluate({})
        30
        >>> Parser(")5 A 6( D 3").parse_line().evaluate({})
        33
        >>> Parser("5 A 6 D 3").parse_line().evaluate({})
        23
        >>> env = Environment({})
        >>> parsed = Parser("test E 4").parse_line()
        >>> parsed
        Operation<Constant<Name<test>>, TokenType.ASSIGN, Constant<4>>
        >>> parsed.evaluate(env)
        >>> env.get_value("test")
        4
        >>> env = Environment({})
        >>> parsed = Parser("4 H 4").parse_line()
        >>> parsed
        Operation<Constant<4>, TokenType.GREATER_EQUAL, Constant<4>>
        >>> parsed.evaluate(env)
        True
        >>> env = Environment({})
        >>> parsed = Parser("IF 4 H 4 [test F 10]").parse_line()
        >>> parsed
        IfBlock<[(Operation<Constant<4>, TokenType.GREATER_EQUAL, Constant<4>>, Block<[Operation<Constant<Name<test>>, TokenType.ASSIGN, Constant<10>>]>)]>
        >>> env = Environment({})
        >>> Parser("9 Q 4").parse_line().evaluate(env)
        1
        >>> tree = Parser("1 P 0").parse_line()
        >>> tree
        Operation<Constant<1>, TokenType.OR, Constant<0>>
        >>> tree.evaluate(env)
        True
        >>> tree = Parser("FUN a [a A 10]").parse_line()
        >>> tree
        Function<['a'], Block<[Operation<Name<a>, TokenType.ADD, Constant<10>>]>>
        """
        right = self.tokenizer.peek_next_token()

        while right.is_token_type(TokenType.EOL):
            self.tokenizer.get_next_token()
            right = self.tokenizer.peek_next_token()

        if right.is_token_type(TokenType.IF):
            return self.parse_conditional(True)
        elif right.is_token_type(TokenType.WHILE_LOOP):
            return self.parse_while_loop()
        elif right.is_token_type(TokenType.FOR_LOOP):
            return self.parse_for_loop()
        elif right.is_token_type(TokenType.FUNC_DECL):
            return self.parse_function_declaration()
        elif not right.is_token_type(TokenType.EOF) and not right.is_token_type(TokenType.EOL) \
            and not right.is_token_type(TokenType.CLOSING_BLOCK) \
            and not right.is_token_type(TokenType.CLOSING_PAR):
            return self.parse_assignment()
        else:
            return None
            

if __name__ == "__main__":
    import doctest
    doctest.testmod()
