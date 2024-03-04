from lox_token import Token, TokenType

from lox_error import LoxError


class Scanner:
    def __init__(self, source: str, lox_error: LoxError) -> None:
        self.source = source
        self.tokens = []
        self.lox_error = lox_error

        self.start = 0
        self.current = 0
        self.line = 1
    
        self.keywords = {
            "and" : TokenType.AND,
            "class" : TokenType.CLASS,
            "else" : TokenType.ELSE,
            "false" : TokenType.FALSE,
            "for" : TokenType.FOR,
            "fun" : TokenType.FUN,
            "if" : TokenType.IF,
            "nil" : TokenType.NIL,
            "or" : TokenType.OR,
            "print" : TokenType.PRINT,
            "return" : TokenType.RETURN,
            "super" : TokenType.SUPER,
            "this" : TokenType.THIS,
            "true" : TokenType.TRUE,
            "var" : TokenType.VAR,
            "while" : TokenType.WHILE
        }

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in [' ', '\r', '\t']:
            # Ignore whitespace.
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            self.lox_error.error(self.line, f"Unexpected character: '{c}'.")


    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        # Consumes the next character in the source file and retunrs it.
        self.current += 1
        return self.source[self.current - 1]
    
    def add_token(self, token_type, literal=None) -> None:
        # Takes the text of the current lexeme and creates a new token for it. 
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        # Similair to a conditional advance().
        # We only consume the current character if it's what we are looking for.
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        # Unterminated string.
        if self.is_at_end():
            self.lox_error.error(self.line, "Unterminated string.")

        # The closing.
        self.advance()

        # Trim the surrounding qoutes.
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def number(self,) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fraction part.
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the ".".
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def peek_next(self) -> str:
        if (self.current + 1) >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source[self.start: self.current]
        token_type = self.keywords.get(text, None)
        if token_type is None:
            token_type = TokenType.IDENTIFIER
        self.add_token(token_type)

    def is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or \
            (c >= 'A' and c <= 'Z') or \
            c == '_'

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

        
        