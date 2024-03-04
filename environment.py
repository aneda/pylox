from lox_token import Token
from lox_error import LoxRuntimeError

class Environment:

    def __init__(self, enclosing=None) -> None:
        self.enclosing = enclosing
        self.values = {}

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def ancestor(self, distance: int) -> object:
        environment = self
        for _ in range(0, distance):
            environment = environment.enclosing
        return environment
    
    def get_env(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values.get(name.lexeme) # python get
        elif self.enclosing:
            return self.enclosing.get_env(name) 
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
        
    def get_at(self, distance: int, name: str) -> object:
        return self.ancestor(distance).values.get(name, None)
    
    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
        
    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self.ancestor(distance).values[name.lexeme] = value

