from lox_token import Token, TokenType
from lox_error import LoxError, ParseError
from expr import Binary, Literal, Grouping, Variable, Expr, \
                 Assign, Logical, Call, Get, Set, This, Super
from stmt import Print, Expression, Stmt, Var, Block, If, \
                 While, Function, Return, Class

class LoxParser:
    def __init__(self, tokens:[Token], lox_error: LoxError) -> None:
        self.tokens = tokens
        self.current = 0
        self.lox_error = lox_error

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements
    
    def expression(self):
        return self.assignment()
    
    def declaration(self) -> Stmt:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.stmt_function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            else:
                return self.statement()
        except ParseError as error:
            self.synchronize()
            return None
    
    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        super_class = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            super_class = Variable(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.stmt_function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Class(name, super_class, methods)

    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        else:
            return self.expression_statement()
        
    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            inilitializer = None
        elif self.match(TokenType.VAR):
            inilitializer = self.var_declaration()
        else:
            inilitializer = self.expression_statement()
        
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()
        
        if increment:
            body = Block([body, Expression(increment)])
        
        if not condition:
            condition = Literal(True)
        body = While(condition, body)

        if inilitializer:
            body = Block([inilitializer, body])
        
        return body
    
    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return If(condition, then_branch, else_branch)
        
    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)
    
    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)
    
    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return While(condition, body)
    
    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)
    
    def stmt_function(self, kind:str) -> Function:
        name = self.consume(TokenType.IDENTIFIER, "Expect " + kind + " name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after " + kind + " name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break
            
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()
        return Function(name, parameters, body)

    
    def block(self):
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and \
              not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self) -> Expr:
        expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            else:
                self.error(equals, "Invalid assignment target.")
        return expr

    def logical_or(self):
        expr = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def logical_and(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr
    
    def match(self, *token_types) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def check(self, token_type) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr
    
    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Binary(operator, right)
        
        return self.call()
    
    def finish_call(self, callee):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguements.")

                arguments.append(self.expression())

                if not self.match(TokenType.COMMA):
                    break

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)
    
    def call(self):
        expr = self.primary()

        while (True):
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'")
                expr = Get(expr, name)
            else:
                break

        return expr
    
    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        elif self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        elif self.match(TokenType.THIS):
            return This(self.previous())
        elif self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        else:
            raise self.error(self.peek(), "Expect expression.")

    def consume(self, token_type, msg):
        if self.check(token_type):
            return self.advance()
        
        raise self.error(self.peek(), msg)
    
    def error(self, token, msg):
        self.lox_error.parse_error(token, msg)
        raise ParseError(f"An error accord during parsing due to '{msg}'")

    def synchronize(self):
        statement_keywords = [TokenType.CLASS, TokenType.FOR, TokenType.FUN, \
                              TokenType.IF, TokenType.PRINT, TokenType.RETURN,\
                              TokenType.VAR,  TokenType.WHILE]
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            if self.peek().token_type in statement_keywords:
                return

            self.advance()
               
            

