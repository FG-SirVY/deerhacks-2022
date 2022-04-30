from expression import Expression, Invocation, Name, Operation, Constant, Environment
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
        self.tokenizer.get_next_token()
        l_operand = self.parse_term(self.parse_line())
        self.tokenizer.get_next_token()
        return self.parse_term(l_operand)


    def parse_mul_div(self, l_operand) -> Expression:
        operator = self.tokenizer.get_next_token().token_type
        right = self.tokenizer.peek_next_token()

        if right.is_token_type(TokenType.OPEN_PAR):
            return self.parse_term(Operation(l_operand, operator,
                self.parse_parentheses()))
        else:
            r_operand = self.get_as_expression(self.tokenizer.get_next_token())
            return self.parse_term(Operation(l_operand, operator, r_operand))       


    def parse_add_sub(self, l_operand) -> Expression:
        operator = self.tokenizer.get_next_token().token_type
        return Operation(l_operand, operator, self.parse_line())

    
    def parse_assignment(self, l_operand) -> Expression:
        operator = self.tokenizer.get_next_token().token_type
        return Operation(Constant(l_operand), operator, self.parse_line())

    
    def parse_invocation(self, name: Token) -> Expression:
        assert name.token_type == TokenType.NAME

        self.tokenizer.get_next_token()

        arguments = []
        next_operator = TokenType.COMMA
        while next_operator == TokenType.COMMA:
            arguments.append(self.parse_line())
            next_operator = self.tokenizer.get_next_token()

        assert next_operator == TokenType.CLOSING_PAR

        return Invocation(name.payload, arguments)

    
    def parse_term(self, l_operand) -> Expression:
        operator = self.tokenizer.peek_next_token()

        if operator.is_token_type(TokenType.MULTIPLY) \
            or operator.is_token_type(TokenType.DIVIDE):
            return self.parse_mul_div(l_operand)
        elif operator.is_token_type(TokenType.ADD) \
            or operator.is_token_type(TokenType.SUBTRACT):
            return self.parse_add_sub(l_operand)
        elif operator.is_token_type(TokenType.ASSIGN):
            return self.parse_assignment(l_operand)
        elif operator.is_token_type(TokenType.OPEN_PAR):
            return self.parse_invocation(l_operand)
        elif operator.is_token_type(TokenType.EOF) \
            or operator.is_token_type(TokenType.EOL):
            self.tokenizer.get_next_token()
            return l_operand
        else:
            return l_operand


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
        """
        left = self.tokenizer.peek_next_token()

        if left.is_operator():
            return self.parse_unitary_operator()
        elif left.is_token_type(TokenType.OPEN_PAR):
            return self.parse_parentheses()
        elif left.is_token_type(TokenType.EOF) or left.is_token_type(TokenType.EOL):
            return None
        else:
            l_operand = self.get_as_expression(self.tokenizer.get_next_token())
            return self.parse_term(l_operand)
            

if __name__ == "__main__":
    import doctest
    doctest.testmod()
