import sys
from typing import Self

from lox_error import LoxError
from scanner import Scanner
from lox_parser import LoxParser
from ast_printer import ASTPrinter
from interpreter import Interpreter
from resolver import Resolver
  

class Lox:

    def __init__(self) -> None:
        self.lox_error = LoxError()
        
    def run_file(self, path: str) -> Self:
        try:
            with open(path, 'r') as reader:
                file_bytes = reader.read()
                self.run(file_bytes)
                if self.lox_error.had_error:
                    SystemExit(65)
                if self.lox_error.had_runtime_error:
                    SystemExit(70)
        except OSError as e:
            print("Unexpected error opening {path} is", e.strerror)
            SystemExit(1)

    def run_prompt(self) -> Self:
        try:
            while True:
                line = input("pylox> ") 
                self.run(line)
                self.lox_error.had_error = False
        except EOFError as e:
            print("\n Exiting due to {e}, Goodbye!")

    def run(self, source) -> Self:
        
        scanner = Scanner(source, self.lox_error)
        tokens = scanner.scan_tokens()
        parser = LoxParser(tokens, self.lox_error)
        statements = parser.parse()

        if self.lox_error.had_error:
             SystemExit(65)

        interpreter = Interpreter(self.lox_error)
        resolver = Resolver(interpreter, self.lox_error)
        resolver.resolve_block(statements)
        if self.lox_error.had_error:
            return
        interpreter.interpret(statements)

        # print(ASTPrinter().print_ast(expression))
        # for token in tokens:
        #     print(token)


if __name__ == "__main__":
    lox = Lox()
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: pylox [script]")
        sys.exit(1)
    elif len(args) == 1:
        lox.run_file(args[0])
    else:
        lox.run_prompt()           