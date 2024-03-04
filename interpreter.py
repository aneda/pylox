import time

from environment import Environment
from lox_error import LoxError, LoxRuntimeError
from lox_callable import LoxCallable
from lox_function import LoxFunction
from lox_token import TokenType, Token
from lox_return import LoxReturn
from lox_class import LoxClass
from lox_instance import LoxInstance

from expr import ExprVisitor, Literal, Grouping, Expr, Unary, \
                 Binary, Variable, Assign, Logical, Call, Get, Set, \
                 This, Super

from stmt import StmtVisitor, Stmt, Expression, Print, Var, Block, \
                 If, While, Function, Return, Class


class Interpreter(ExprVisitor, StmtVisitor):

    class LoxClock(LoxCallable):
        def arity(self) -> int:
            return 0
        
        def call(self, interpreter: object, arguments: list[object]) -> object:
            return time.time()
        
        def __str__(self) -> str:
            return "<native fn>;"

    def __init__(self, lox_error: LoxError) -> None:
        self.lox_error = lox_error
        self.lox_globals = Environment()
        self.environment = self.lox_globals
        self.lox_globals.define("clock", self.LoxClock())
        self.locals = {}

    def interpret(self, statements: [Stmt]):
        try:
            for statemet in statements:
                self.execute(statemet)
        except LoxRuntimeError as e:
            self.lox_error.runtime_error(e)
    
    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)
    
    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)
    
    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth
    
    def execute_block(self, statements, environment) -> None:
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value
    
    def visit_logical_expr(self, expr: Logical) -> object:
        left = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR :
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expr.right)
    
    def visit_set_expr(self, expr: Set) -> None:
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "only instances have fields.")
        
        value = self.evaluate(expr.value)
        obj.set_instance(expr.name, value)
        return value
    
    def visit_super_expr(self, expr: Super) -> object:
        distance = self.locals.get(expr, 0) # python dict get
        super_class = self.environment.get_at(distance, "super")
        obj = self.environment.get_at(distance - 1, "this")
 
        method = super_class.find_method(expr.method.lexeme) # find_method from LoxClass
        if not method:
            raise LoxRuntimeError(expr.method, "Undefined property '" + expr.method.lexeme + "'.")
        return method.bind(obj)
    
    def visit_this_expr(self, expr: This) -> object:
        return self.lookup_variable(expr.keyword, expr)
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_class_stmt(self, stmt: Class):
        super_class = None
        if stmt.super_class:
            super_class = self.evaluate(stmt.super_class)
            if not isinstance(super_class, LoxClass):
                raise LoxRuntimeError(stmt.super_class.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.super_class:
            self.environment = Environment(self.environment)
            self.environment.define("super", super_class)

        methods = {}
        for method in stmt.methods:
            fun = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = fun
        
        klass = LoxClass(stmt.name.lexeme, super_class, methods)

        if super_class:
            self.environment = self.environment.enclosing
        
        self.environment.assign(stmt.name, klass)
    
    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)
    
    def visit_function_stmt(self, stmt: Function):
        lox_function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, lox_function)
    
    def visit_if_stmt(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print( self.stringify(value))
    
    def visit_return_stmt(self, stmt: Return) -> object:
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        
        raise LoxReturn(value)
    
    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Assign) -> object:
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr, 0)
        if distance == 0:
            self.lox_globals.assign(expr.name, value)
        else:
            self.environment.assign_at(distance, expr.name, value)
        return value
    
    def visit_unary_expr(self, expr: Unary) -> object:
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.BANG:
            return not self.is_thruthy(right)
        elif expr.operator.token_type == TokenType.MINUS:
            return -1 * self.format_number(right)
        
        return None
    
    def visit_variable_expr(self, expr: Variable) -> object:
        return self.lookup_variable(expr.name, expr)
    
    def lookup_variable(self, name: Token, expr: Expr) -> object:
        distance = self.locals.get(expr, None)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.lox_globals.get_env(name)
            
    
    def is_truthy(self, obj:object) -> bool:
        if obj == None:
            return False
        elif isinstance(obj, bool):
            return bool(obj)
        else:
            return True
        
    def check_number_oprands(self, operator: TokenType, left: object, right:object) -> bool:
        if isinstance(left, (float, int)) and isinstance(right, (float, int)):
            return True
        else:
            raise LoxRuntimeError(operator, "operand must be a number")
        
    def format_number(self, operand):
        if isinstance(operand, float):
            return float(operand)
        elif isinstance(operand, int):
            return int(operand)
        else:
            raise LoxRuntimeError(operand, "operand must be a number") 
        
    def visit_binary_expr(self, expr: Binary) -> object:
        right = self.evaluate(expr.right)
        left = self.evaluate(expr.left)
        
        operator_type = expr.operator.token_type
        
        if operator_type == TokenType.MINUS:
            self.check_number_oprands(operator_type, left, right)
            return self.format_number(left) - self.format_number(right)
        elif operator_type == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            elif self.check_number_oprands(operator_type, left, right):
                return self.format_number(left) + self.format_number(right)
            else:
                raise LoxRuntimeError(expr.operator, "operands must be two numbers or two strings")
        elif operator_type == TokenType.SLASH:
            self.check_number_oprands(operator_type, left, right)
            return self.format_number(left) / self.format_number(right)
        elif operator_type == TokenType.STAR:
            self.check_number_oprands(operator_type, left, right)
            return self.format_number(left) * self.format_number(right)
        elif operator_type == TokenType.GREATER:
            return self.format_number(left) > self.format_number(right)
        elif operator_type == TokenType.GREATER_EQUAL:
            return self.format_number(left) >= self.format_number(right)
        elif operator_type == TokenType.LESS:
            return self.format_number(left) < self.format_number(right)
        elif operator_type == TokenType.LESS_EQUAL:
            return self.format_number(left) <= self.format_number(right)
        elif operator_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif operator_type == TokenType.BANG_EQUAL:
            return self.is_equal(left, right)
        else:
            return None
    
    def visit_call_expr(self, expr: Call)-> object:
        callee = self.evaluate(expr.callee)

        arguments = []
        for arguement in expr.arguments:
            arguments.append(self.evaluate(arguement))
        
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")
        
        fun = callee
        if len(arguments) != fun.arity():
            raise LoxRuntimeError(expr.paren, \
                                  f"Expected {fun.arity()} argumenets but got {len(arguments)}.")

        return fun.call(self, arguments)
    
    def visit_get_expr(self, expr: Get) -> object:
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get_instance(expr.name) # get instance property for expr.name
        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def is_equal(self, a: object, b: object) -> bool:
        if a == None and b == None:
            return True
        elif a == None:
            return False
        else:
            return a == b
        
    def stringify(self, obj: object) -> str:
        if obj == None:
            return "nil"
        
        text = str(obj)
        if isinstance(obj, float) and text.endswith(".0"):
            text = text[:-2]

        return text
    
