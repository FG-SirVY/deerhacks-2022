from expression import Block, Expression, IfBlock, Invocation, Name, Operation, Constant, Environment, ForLoop, WhileLoop
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
        operator = self.tokenizer.get_next_token().token_type
        return Operation(None, operator, self.parse_line())


    def parse_parentheses(self) -> Expression:
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.OPEN_PAR):
            self.tokenizer.get_next_token()
            term = self.parse_comparison()
            self.tokenizer.get_next_token()
            return term
        else:
            return self.get_as_expression(self.tokenizer.get_next_token())


    def parse_mul_div(self) -> Expression:
        l_operand = self.parse_parentheses()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.MULTIPLY) \
            or next_token.is_token_type(TokenType.DIVIDE):
            operator = self.tokenizer.get_next_token().token_type
            right = self.tokenizer.peek_next_token()

            if right.is_token_type(TokenType.OPEN_PAR):
                return Operation(l_operand, operator, self.parse_parentheses())
            else:
                r_operand = self.get_as_expression(self.tokenizer.get_next_token())
                return Operation(l_operand, operator, r_operand)
        else:
            return l_operand


    def parse_add_sub(self) -> Expression:
        l_operand = self.parse_mul_div()
        next_token = self.tokenizer.peek_next_token()
        
        if next_token.is_token_type(TokenType.ADD) \
            or next_token.is_token_type(TokenType.SUBTRACT):

            operator = self.tokenizer.get_next_token().token_type
            return Operation(l_operand, operator, self.parse_line())
        else:
            return l_operand

    
    def parse_assignment(self) -> Expression:
        l_operand = self.parse_add_sub()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.ASSIGN):
            operator = self.tokenizer.get_next_token().token_type
            return Operation(Constant(l_operand), operator, self.parse_line())
        else:
            return l_operand


    def parse_invocation(self) -> Expression:
        l_operand = self.parse_assignment()
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
        left = self.tokenizer.peek_next_token()

        if left.is_operator():
            return self.parse_unitary_operator()
        elif left.is_token_type(TokenType.INT) \
            or left.is_token_type(TokenType.FLOAT) \
            or left.is_token_type(TokenType.STRING) \
            or left.is_token_type(TokenType.OPEN_PAR) \
            or left.is_token_type(TokenType.NAME):
            return self.parse_invocation()
        else:
            return None


    def parse_comparison(self) -> Expression:
        l_operand = self.parse_term()
        next_token = self.tokenizer.peek_next_token()

        if next_token.is_token_type(TokenType.LESS_EQUAL) \
            or next_token.is_token_type(TokenType.LESS_THAN) \
            or next_token.is_token_type(TokenType.GREATER_EQUAL) \
            or next_token.is_token_type(TokenType.GREATER_THAN):

            operator = self.tokenizer.get_next_token().token_type
            return Operation(l_operand, operator, self.parse_line())
        else:
            return l_operand


    def parse_block(self) -> Expression:
        next_token = self.tokenizer.get_next_token()
        assert next_token.is_token_type(TokenType.OPEN_BLOCK)

        expressions = []
        expr = self.parse_line()

        while expr is not None:
            expressions.append(expr)
            expr = self.parse_line()

        return Block(expressions)


    def parse_conditional(self) -> Expression:
        self.tokenizer.get_next_token()
        condition = self.parse_line()
        block = self.parse_block()

        return IfBlock([(condition, block)])
    

    def parse_while_loop(self) -> Expression:
        self.tokenizer.get_next_token()
        condition = self.parse_line()
        block = self.parse_block()
        return WhileLoop(condition, block)


    def parse_for_loop(self) -> Expression:
        self.tokenizer.get_next_token()
        next_token = self.tokenizer.get_next_token()
        assert next_token.is_token_type(TokenType.OPEN_BLOCK)
        
        cond_exprs = []
        expr = self.parse_line()
        while expr is not None:
            cond_exprs.append(expr)
            expr = self.parse_line()
        assert len(cond_exprs) == 3

        block = self.parse_block()
        return ForLoop(cond_exprs[0], cond_exprs[1], cond_exprs[2], block)


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
        """
        right = self.tokenizer.peek_next_token()

        while right.is_token_type(TokenType.EOL) \
            or right.is_token_type(TokenType.CLOSING_BLOCK):
            self.tokenizer.get_next_token()
            right = self.tokenizer.peek_next_token()

        if right.is_token_type(TokenType.CONDITIONAL):
            return self.parse_conditional()
        elif right.is_token_type(TokenType.WHILE_LOOP):
            return self.parse_while_loop()
        elif right.is_token_type(TokenType.FOR_LOOP):
            return self.parse_for_loop()
        elif not right.is_token_type(TokenType.EOF) and not right.is_token_type(TokenType.EOL) \
            and not right.is_token_type(TokenType.CLOSING_BLOCK) \
            and not right.is_token_type(TokenType.CLOSING_PAR):
            return self.parse_comparison()
        else:
            return None
            

if __name__ == "__main__":
    import doctest
    doctest.testmod()
