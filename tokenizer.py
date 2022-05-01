import enum
from typing import Union


ROTATING_TOKEN_COUNT = 17
ROTATING_TOKEN_OFFSET = 16


class TokenType(enum.Enum):
    """
    The type which a token has. There are a few subtypes:
    UNKNOWN and EOF as control tokens,
    OPEN_PAR, CLOSING_PAR for parentheses.
    NAME for names like variable names.
    INT, FLOAT, STRING basic literals.
    ADD, ASSIGN as operators.
    """
    UNKNOWN = 0
    EOF = 1
    EOL = 2
    COMMA = 3
    RETURN = 4
    OPEN_PAR = 5
    CLOSING_PAR = 6
    OPEN_BLOCK = 7
    CLOSING_BLOCK = 8
    NAME = 9
    INT = 10
    FLOAT = 11
    STRING = 12
    CONDITIONAL = 13
    FOR_LOOP = 14
    WHILE_LOOP = 15
    ADD = 16 #A
    SUBTRACT = 17 #B
    MULTIPLY = 18 #C
    DIVIDE = 19 #D
    ASSIGN = 20 #E
    EQUAL = 21 #F
    GREATER_THAN = 22 #G
    GREATER_EQUAL = 23 #H
    LESS_THAN = 24 #I
    LESS_EQUAL = 25 #J
    TO_INT = 26 #K
    TO_FLOAT = 27 #L
    TO_BOOL = 28 #M
    NOT = 29 #N
    AND = 30 #O
    OR = 31 #P
    MOD = 32 #Q


    def is_operator(self):
        """
        Checks whether a given token is an operator.
        """
        return self.value >= ROTATING_TOKEN_OFFSET


class Token:
    """
    A Token - what can I say more.
    """
    token_type: TokenType
    payload: Union[str, int]


    def __init__(self, token_type: TokenType, payload: Union[str, int, float] = None) -> None:
        """
        Initialize token_type and payload.
        """
        self.token_type = token_type
        self.payload = payload


    def __repr__(self) -> str:
        """
        Create a string representation of this Token.
        """
        return f"Token<Type: {self.token_type.name}, Payload: {self.payload}>"


    def is_operator(self) -> bool:
        """
        Check whether this token is an operator.
        """
        return self.token_type.is_operator()


    def is_token_type(self, token_type: TokenType) -> bool:
        """
        Check whether this token is a of a specified kind.
        """
        return self.token_type == token_type


class Tokenizer:
    """
    TODO: Error handling

    Tokenize a string it receives as input
    """
    script: str
    index: int
    shift: int
    next_token: Token


    def __init__(self, script: str) -> None:
        """
        Initialize script, index and shift
        """
        self.script = script
        self.index = -1
        self.shift = 0
        self.next_token = None


    def _get_numerical_token(self) -> Token:
        """
        Parse a numerical token from the script.
        
        PRECONDITIONS:
        The current character already is a digit.
        """
        start = self.index
        self.index += 1

        while self.index < len(self.script) and self.script[self.index].isdigit():
            self.index += 1

        self.index -= 1

        return Token(TokenType.INT, int(self.script[start:self.index + 1]))


    def _get_string_token(self) -> Token:
        """
        Parse a string token from the script.

        PRECONDITIONS:
        The current character is " and the string ends somewhere.
        """
        start = self.index + 1
        self.index += 1

        while self.index < len(self.script) and self.script[self.index] != "\"":
            self.index += 1

        return Token(TokenType.STRING, self.script[start:self.index])


    def _get_operator_token_from(self, operator_string: str) -> Token:
        """
        Parse a jumbled operator token from the script.

        PRECONDIITONS:
        The current character is an uppercase letter corresponding to a valid operator.
        """
        token = Token(TokenType(ord(operator_string) - ord("A")
            + ROTATING_TOKEN_OFFSET - self.shift))
        
        # Now shift the tokens
        self.shift += 1
        self.shift %= ROTATING_TOKEN_COUNT

        return token


    def _get_control_flow_token(self) -> Token:
        """
        Parse a control flow token, such as operator or keyword
        """
        start = self.index
        self.index += 1

        while self.index < len(self.script) and self.script[self.index].isupper():
            self.index += 1

        if self.index - start == 1:
            return self._get_operator_token_from(self.script[start])
        else:
            keyword = self.script[start:self.index]

            if keyword == "IF":
                return Token(TokenType.CONDITIONAL)
            elif keyword == "FOR":
                return Token(TokenType.FOR_LOOP)
            elif keyword == "WHILE":
                return Token(TokenType.WHILE_LOOP)
            else:
                assert False


    def _get_name_token(self) -> Token:
        """
        Parse a name from the script

        PRECONDITIONS:
        The current character is alpha.
        """
        start = self.index
        self.index += 1

        while self.index < len(self.script) and self.script[self.index].isalpha():
            self.index += 1

        self.index -= 1

        return Token(TokenType.NAME, payload=self.script[start:self.index + 1])


    def peek_next_token(self) -> Token:
        """
        Returns the next token without advancing to that position.
        """
        if self.next_token is None:
            self.next_token = self.get_next_token()
        
        return self.next_token  


    def get_next_token(self) -> Token:
        """
        Parses the next token from the script.

        >>> t = Tokenizer("b B 5")
        >>> t.get_next_token()
        Token<Type: NAME, Payload: b>
        >>> t.get_next_token()
        Token<Type: SUBTRACT, Payload: None>
        >>> t.get_next_token()
        Token<Type: INT, Payload: 5>
        >>> t.get_next_token()
        Token<Type: EOF, Payload: None>
        >>> t = Tokenizer(")5 A 6( D 3")
        >>> t.get_next_token()
        Token<Type: OPEN_PAR, Payload: None>
        >>> t.get_next_token()
        Token<Type: INT, Payload: 5>
        >>> t.get_next_token()
        Token<Type: ADD, Payload: None>
        >>> t.get_next_token()
        Token<Type: INT, Payload: 6>
        >>> t.get_next_token()
        Token<Type: CLOSING_PAR, Payload: None>
        >>> t = Tokenizer("3 C )5 B 6(")
        >>> t.get_next_token()
        Token<Type: INT, Payload: 3>
        >>> t.get_next_token()
        Token<Type: MULTIPLY, Payload: None>
        >>> t.get_next_token()
        Token<Type: OPEN_PAR, Payload: None>
        >>> t.get_next_token()
        Token<Type: INT, Payload: 5>
        >>> t.get_next_token()
        Token<Type: ADD, Payload: None>
        >>> t.get_next_token()
        Token<Type: INT, Payload: 6>
        >>> t = Tokenizer("IF 5 H 5 [print)6(]")
        >>> t.get_next_token()
        Token<Type: CONDITIONAL, Payload: None>
        """
        if self.next_token is not None:
            ret = self.next_token
            self.next_token = None
            return ret

        self.index += 1
        while self.index < len(self.script) and self.script[self.index].isspace():
            self.index += 1

        if self.index >= len(self.script):
            return Token(TokenType.EOF)

        if self.script[self.index] == ")":
            return Token(TokenType.OPEN_PAR)
        elif self.script[self.index] == "(":
            return Token(TokenType.CLOSING_PAR)
        elif self.script[self.index] == "|":
            return Token(TokenType.EOL)
        elif self.script[self.index] == ",":
            return Token(TokenType.COMMA)
        elif self.script[self.index] == "[":
            return Token(TokenType.OPEN_BLOCK)
        elif self.script[self.index] == "]":
            return Token(TokenType.CLOSING_BLOCK)
        
        if self.script[self.index].isdigit():
            return self._get_numerical_token()

        if self.script[self.index] == "\"":
            return self._get_string_token()

        if self.script[self.index].isupper():
            return self._get_control_flow_token()

        if self.script[self.index].isalpha():
            return self._get_name_token()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
