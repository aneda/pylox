from lox_token import Token, TokenType

class LoxRuntimeError(RuntimeError):

    def __init__(self, token: Token, message: str) -> None:
        super().__init__()
        self.token = token
        self.message = message
    
    def report(self) -> str:
        return f"{self.message}\n[line: {self.token.line}]"

class LoxError:

    def __init__(self) -> None:
        self.had_error = False
        self.had_runtime_error = False

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)
    
    def runtime_error(self, error: LoxRuntimeError) -> None:
        print(error.report())
        self.had_runtime_error = True

    
    def parse_error(self, token, message) -> None:
        if token.token_type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "'", message)

    def report(self, line: int, where: str, message:str) -> None:
        print("[line " + str(line) + " Error]" + where + ": " + message)
        self.had_error = True
    

class ParseError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


