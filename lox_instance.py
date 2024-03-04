from lox_token import Token
from lox_error import LoxRuntimeError

class LoxInstance:
    def __init__(self, klass) -> None:
        self.klass = klass
        self.fields = {}
    
    def get_instance(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme, None)  # native python dict get
        
        method = self.klass.find_method(name.lexeme)   # find_method from LoxClass
        if method:
            return method.bind(self)
        
        raise LoxRuntimeError(name, "Undefined property '" + name.lexeme + "'.")
    
    def set_instance(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return self.klass.name + " instance"