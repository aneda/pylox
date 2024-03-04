from lox_callable import LoxCallable
from lox_return import LoxReturn
from environment import Environment
from stmt import Function

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool) -> None:
        self.closure = closure
        self.declaration = declaration
        self.is_initializer = is_initializer
    
    def bind(self, instance: object) -> object:
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter:object, arguments) -> object:
        environment = Environment(self.closure)
        for i in range(0, len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturn as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return "<fn " + self.declaration.name.lexeme + ">"
    

