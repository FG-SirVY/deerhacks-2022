from expression import Expression, Operation, Constant
from tokenizer import Tokenizer, TokenType, Token


class Parser:
    """
    Parses a string using Tokenizer into a tree of Expressions.
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

        raise Exception(f"Cannot map token of type {token.token_type} directly to Expression")


    def parse(self) -> Expression:
        """
        Parse one it. FINALLY.

        >>> p = Parser("5 A 6")
        >>> tree = p.parse()
        >>> tree
        Operation<l: Constant<c: 5>, op: TokenType.ADD, r: Constant<c: 6>>
        >>> tree.evaluate({})
        11
        >>> p = Parser("5 A 6 B 3")
        >>> tree = p.parse()
        >>> tree
        Operation<l: Constant<c: 5>, op: TokenType.ADD, r: Operation<l: Constant<c: 6>, op: TokenType.ADD, r: Constant<c: 3>>>
        >>> tree.evaluate({})
        14
        """
        left = self.tokenizer.get_next_token()

        if left.token_type == TokenType.OPEN_PAR:
            return self.parse()
        elif left.is_operator():
            operator = left.token_type
            operand = self.parse()
            return Operation(None, operator, operand)
        else:
            l_operand = self.get_as_expression(left)
            middle = self.tokenizer.get_next_token()

            if middle.is_token_type(TokenType.CLOSING_PAR) or middle.is_token_type(TokenType.EOF):
                return l_operand
            elif middle.is_token_type(TokenType.ADD):
                operator = middle.token_type
                r_operand = self.parse()
                return Operation(l_operand, operator, r_operand)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

