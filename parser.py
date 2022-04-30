import enum
from typing import Union


ROTATING_TOKEN_COUNT = 2
ROTATING_TOKEN_OFFSET = 8

class TokenType(enum.Enum):
    UNKNOWN = 0
    EOF = 1
    OPEN_PAR = 2
    CLOSING_PAR = 3
    NAME = 4
    INT = 5
    FLOAT = 6
    STRING = 7
    ADD = 8
    ASSIGN = 9


class Token:
    token_type: TokenType
    payload: Union[str, int]

    def __init__(self, token_type: TokenType, payload: Union[str, int, float] = None):
        self.token_type = token_type
        self.payload = payload

    def __repr__(self):
        return f"Token<Type: {self.token_type.name}, Payload: {self.payload}>"


class Tokenizer:
    #TODO: Error handling

    script: str
    index: int
    shift: int


    def __init__(self, script: str):
        """
        Initialize script, index and shift
        """
        self.script = script
        self.index = -1
        self.shift = 0


    def get_numerical_token(self):
        """
        Parse a numerical token from the script.
        
        PRECONDITIONS:
        The current character already is a digit.
        """
        start = self.index
        self.index += 1

        while self.index < len(self.script) and self.script[self.index].isdigit():
            self.index += 1

        return Token(TokenType.INT, int(self.script[start:self.index]))


    def get_string_token(self):
        """
        Parse a string token from the script.

        PRECONDITIONS:
        The current character is " and the string ends somewhere.
        """
        start = self.index
        self.index += 1

        while self.index < len(self.script) and self.script[self.index] != "\"":
            self.index += 1

        return Token(TokenType.STRING, int(self.script[start:self.index]))


    def get_operator_token(self):
        """
        Parse a jumbled operator token from the script.

        PRECONDIITONS:
        The current character is an uppercase letter corresponding to a valid operator.
        """
        token = Token(TokenType(ord(self.script[self.index]) - ord("A")
            + ROTATING_TOKEN_OFFSET + self.shift))
        
        # Now shift the tokens
        self.shift += 1
        self.shift %= ROTATING_TOKEN_COUNT

        return token


    def get_name_token(self):
        """
        Parse a name from the script

        PRECONDITIONS:
        The current character is alpha.
        """
        start = self.index
        self.index += 1

        while self.index < len(self.script) and self.script[self.index].isalpha():
            self.index += 1

        return Token(TokenType.NAME, payload=self.script[start:self.index])


    def get_next_token(self):
        """
        Parses the next token from the script.

        >>> t = Tokenizer("b B 5")
        >>> t.get_next_token()
        Token<Type: NAME, Payload: b>
        >>> t.get_next_token()
        Token<Type: ASSIGN, Payload: None>
        >>> t.get_next_token()
        Token<Type: INT, Payload: 5>
        >>> t.get_next_token()
        Token<Type: EOF, Payload: None>
        """
        self.index += 1
        while self.index < len(self.script) and self.script[self.index] == " ":
            self.index += 1

        if self.index >= len(self.script):
            return Token(TokenType.EOF)

        if self.script[self.index] == ")":
            return Token(TokenType.OPEN_PAR)
        if self.script[self.index] == "(":
            return Token(TokenType.CLOSING_PAR)
        
        if self.script[self.index].isdigit():
            return self.get_numerical_token()

        if self.script[self.index] == "\"":
            return self.get_string_token()

        if self.script[self.index].isupper():
            return self.get_operator_token()

        if self.script[self.index].isalpha():
            return self.get_name_token()


if __name__ == "__main__":
    import doctest
    doctest.testmod()

