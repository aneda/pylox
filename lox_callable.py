from abc import ABC, abstractmethod

class LoxCallable(ABC):

    @abstractmethod
    def arity(self)-> int:
        raise NotImplementedError
    
    @abstractmethod
    def call(self, interpreter: object, arguments: list[object]) -> object:
        raise NotImplementedError