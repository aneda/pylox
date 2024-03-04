from abc import ABC, abstractmethod

class ExprVisitor(ABC):

	@abstractmethod
	def visit_literal_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_variable_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_logical_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_set_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_super_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_this_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_unary_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_binary_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_call_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_get_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_grouping_expr(self, expr) -> None:
		raise NotImplementedError

	@abstractmethod
	def visit_assign_expr(self, expr) -> None:
		raise NotImplementedError

class Expr(ABC):

	@abstractmethod
	def accept(self, visitor: ExprVisitor) -> None:
		raise NotImplementedError


class Literal(Expr):

	def __init__(self, value) -> None:
		self.value = value

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_literal_expr(self)


class Variable(Expr):

	def __init__(self, name) -> None:
		self.name = name

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_variable_expr(self)


class Logical(Expr):

	def __init__(self, left, operator, right) -> None:
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_logical_expr(self)


class Set(Expr):

	def __init__(self, object, name, value) -> None:
		self.object = object
		self.name = name
		self.value = value

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_set_expr(self)


class Super(Expr):

	def __init__(self, keyword, method) -> None:
		self.keyword = keyword
		self.method = method

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_super_expr(self)


class This(Expr):

	def __init__(self, keyword) -> None:
		self.keyword = keyword

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_this_expr(self)


class Unary(Expr):

	def __init__(self, operator, right) -> None:
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_unary_expr(self)


class Binary(Expr):

	def __init__(self, left, operator, right) -> None:
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_binary_expr(self)


class Call(Expr):

	def __init__(self, callee, paren, arguments) -> None:
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_call_expr(self)


class Get(Expr):

	def __init__(self, object, name) -> None:
		self.object = object
		self.name = name

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_get_expr(self)


class Grouping(Expr):

	def __init__(self, expression) -> None:
		self.expression = expression

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_grouping_expr(self)


class Assign(Expr):

	def __init__(self, name, value) -> None:
		self.name = name
		self.value = value

	def accept(self, visitor: ExprVisitor) -> object:
		return visitor.visit_assign_expr(self)

