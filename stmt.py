from abc import ABC, abstractmethod

class StmtVisitor(ABC):

	@abstractmethod
	def visit_block_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_class_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_expression_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_function_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_if_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_print_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_return_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_while_stmt(self, stmt) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_var_stmt(self, stmt) -> None:
		raise NotImplementedError

class Stmt(ABC):

	@abstractmethod
	def accept(self, visitor: StmtVisitor) -> None:
		raise NotImplementedError


class Block(Stmt):

	def __init__(self, statements) -> None:
		self.statements = statements

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_block_stmt(self)


class Class(Stmt):

	def __init__(self, name, super_class, methods) -> None:
		self.name = name
		self.super_class = super_class
		self.methods = methods

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_class_stmt(self)


class Expression(Stmt):

	def __init__(self, expression) -> None:
		self.expression = expression

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_expression_stmt(self)


class Function(Stmt):

	def __init__(self, name, params, body) -> None:
		self.name = name
		self.params = params
		self.body = body

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_function_stmt(self)


class If(Stmt):

	def __init__(self, condition, then_branch, else_branch) -> None:
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_if_stmt(self)


class Print(Stmt):

	def __init__(self, expression) -> None:
		self.expression = expression

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_print_stmt(self)


class Return(Stmt):

	def __init__(self, keyword, value) -> None:
		self.keyword = keyword
		self.value = value

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_return_stmt(self)


class While(Stmt):

	def __init__(self, condition, body) -> None:
		self.condition = condition
		self.body = body

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_while_stmt(self)


class Var(Stmt):

	def __init__(self, name, initializer) -> None:
		self.name = name
		self.initializer = initializer

	def accept(self, visitor: StmtVisitor) -> object:
		return visitor.visit_var_stmt(self)

