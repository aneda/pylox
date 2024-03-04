from lox_callable import LoxCallable
from lox_instance import LoxInstance
from lox_function import LoxFunction

class LoxClass(LoxCallable):
    def __init__(self, name: str, super_class: object, methods: dict) -> None:
        self.name = name
        self.super_class = super_class
        self.methods = methods
    
    def __str__(self) -> str:
        return self.name
    
    def find_method(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods.get(name, None) # Python dict get
        if self.super_class:
            return self.super_class.find_method(name)
        return None
    
    def call(self, interpreter: object, arguments: list) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance
    
    def arity(self) -> int:
        initializer = self.find_method("init")
        if not initializer:
            return 0
        else:
            return initializer.arity()