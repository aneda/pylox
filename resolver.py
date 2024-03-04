from enum import Enum

from interpreter import Interpreter
from lox_token import Token
from lox_error import LoxError
from expr import ExprVisitor, Literal, Grouping, Expr, Unary, \
                 Binary, Variable, Assign, Logical, Call, Get, Set, \
                 This, Super
from stmt import StmtVisitor, Stmt, Expression, Print, Var, Block, \
                 If, While, Function, Return, Class


class FunctionType(Enum):
    Null = "none"
    METHOD = "method"
    INITIALIZER = "initializer"
    Function = "function"

class ClassType(Enum):
    Null = "none"
    SUBCLASS = "subclass"
    CLASS = "class"

class Resolver(ExprVisitor, StmtVisitor):

    def __init__(self, interpreter: Interpreter, lox_error: LoxError) -> None:
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.Null
        self.current_class = ClassType.Null
        self.lox_error = lox_error

    
    def resolve_block(self, statements: list[object]) -> None:
        for statement in statements:
            self.resolve(statement)
    
    def resolve(self, stmt: object) -> None:
        stmt.accept(self)
        
    
    def resolve_function(self, fun: Function, type: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in fun.params:
            self.declare(param)
            self.define(param)
        self.resolve_block(fun.body)
        self.end_scope()
        self.current_function = enclosing_function
    
    def begin_scope(self) -> None:
        self.scopes.append({})
    
    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if self.scopes:
            scope = self.scopes[-1]
            if name.lexeme in scope:
                self.lox_error.error(name, "Already a variable with this name in this scope.")
            scope[name.lexeme] = False
        else:
            return None
            
    def define(self, name: Token) -> None:
        if self.scopes:
            self.scopes[-1][name.lexeme] = True
        else:
            return None
            
    
    def resolve_local(self, expr: Expr, name: Token) -> None:
        # variable in current scope 0
        # variable in enclosing scope 1
        # variable not found means it is global
        # decrement len(self.scopes) - 1 >= i >= 0
        for i in range(len(self.scopes)-1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return None
    
    def visit_block_stmt(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve_block(stmt.statements)
        self.end_scope()
    
    def visit_class_stmt(self, stmt: Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.super_class and stmt.name.lexeme == stmt.super_class.name.lexeme:
            self.lox_error.error(stmt.super_class.name.line, "A class can't inherit from itself.")
        
        if stmt.super_class:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.super_class)
        
        if stmt.super_class:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.super_class:
            self.end_scope()
        
        self.current_class = enclosing_class

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.resolve(stmt.expression)
    
    def visit_function_stmt(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.Function)

    def visit_if_stmt(self, stmt: If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)
    
    def visit_print_stmt(self, stmt: Print) -> None:
        self.resolve(stmt.expression)
    
    def visit_return_stmt(self, stmt: Return) -> None:
        if self.current_function == FunctionType.Null:
            self.lox_error.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value:
            if self.current_function == FunctionType.INITIALIZER:
                self.lox_error.error(stmt.keyword.line, "Can't return from top-level code.")
            self.resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
    
    def visit_variable_expr(self, expr: Variable) -> None:
        if self.scopes and self.scopes[-1].get(expr.name.lexeme, None) == False:
            self.lox_error.error(expr.name, "Can't read local variable in its own initializer")
        self.resolve_local(expr, expr.name)
    
    def visit_assign_expr(self, expr: Assign) -> None:
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
    
    def visit_binary_expr(self, expr: Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visit_call_expr(self, expr: Call) -> None:
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
    
    def visit_get_expr(self, expr: Get) -> object:
        self.resolve(expr.object)
    
    def visit_grouping_expr(self, expr: Grouping) -> None:
        self.resolve(expr.expression)
    
    def visit_literal_expr(self, expr: Literal):
        return None
    
    def visit_logical_expr(self, expr: Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visit_set_expr(self, expr: Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.object)
    
    def visit_super_expr(self, expr: Super) -> None:
        if self.current_class == ClassType.Null:
            self.lox_error.error(expr.keyword.line, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            self.lox_error.error(expr.keyword.line, "Can't use 'super' in a class with no superclass.")
        
        self.resolve_local(expr, expr.keyword)
    
    def visit_this_expr(self, expr: This):
        if self.current_class == ClassType.Null:
            self.lox_error.error(expr.keyword.line, "Can't use 'this' outside of a class.")

        self.resolve_local(expr, expr.keyword)
    
    def visit_unary_expr(self, expr: Unary) -> None:
        self.resolve(expr.right)

    
    
    
