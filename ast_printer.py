from expr import *
from lox_token import Token, TokenType


class ASTPrinter(ExprVisitor):

    def print_ast(self, expr: Expr) -> None:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> None:
        print(expr.operator)
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_literal_expr(self, expr: Literal) -> None:
        return str(expr.value)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        return self.parenthesize("group", expr.expression)

    def visit_unary_expr(self, expr: Unary) -> None:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_call_expr(self, expr) -> None:
        return self.parenthesize(expr.callee, expr.paren, expr.arguements)
    
    def visit_get_expr(self, expr) -> None:
        return self.parenthesize(expr.object, expr.name)
    
    def visit_set_expr(self, expr) -> None:
        return self.parenthesize(expr.object, expr.name, expr.value)
    
    def visit_super_expr(self, expr) -> None:
        return self.parenthesize(expr.keyword, expr.method)
    
    def visit_this_expr(self, expr) -> None:
        return self.parenthesize(expr.keyword)
    
    def visit_variable_expr(self, expr) -> None:
        return self.parenthesize(expr.name)
    
    def visit_logical_expr(self, expr) -> None:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_assign_expr(self, expr) -> None:
        return self.parenthesize(expr.name, expr.value)

    def parenthesize(self, name, *exprs):
        string_builder = "(" + name

        for expr in exprs:
            string_builder += " "
            string_builder += expr.accept(self)
        
        string_builder += ")"

        return string_builder
    
if __name__ == "__main__":
    ast_printer = ASTPrinter()
    expression = Binary(
        Binary(
            Unary(Token(TokenType.MINUS, "-", None, 1), Literal(1)),
            Token(TokenType.PLUS, "+", None, 1), Literal(2)),
        Token(TokenType.SLASH, "/", None, 1),
        Grouping(Unary(Token(TokenType.MINUS, "-", None, 1), Literal(3))))
    print(ast_printer.print_ast(expression))