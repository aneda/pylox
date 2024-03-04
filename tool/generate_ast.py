from pydoc import classname
import sys


expr = [
    "Literal  : value",
    "Variable : name",
    "Logical  : left, operator, right",
    "Set      : object, name, value",
    "Super    : keyword, method",
    "This     : keyword",
    "Unary    : operator, right",
    "Binary   : left, operator, right",
    "Call     : callee, paren, arguments",
    "Get      : object, name",
    "Grouping : expression",
    "Assign   : name, value",
]
statements = [
    "Block      : statements",
    "Class      : name, super_class, methods",
    "Expression : expression",
    "Function   : name, params, body",
    "If         : condition, then_branch, else_branch",
    "Print      : expression",
    "Return     : keyword, value",
    "While      : condition, body",
    "Var        : name, initializer",
]

def define_type(file, base_name, class_name, fields):
    file.write(f"class {class_name}({base_name}):\n\n")
    file.write(f"\tdef __init__(self, {fields}) -> None:\n")
    fields = fields.split(", ")
    for field in fields:
        name = field.split(" ")[0]
        file.write(f"\t\tself.{name} = {name}\n")
    file.write(f"\n\tdef accept(self, visitor: {base_name}Visitor) -> object:\n")
    file.write(f"\t\treturn visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n\n")

def define_visitor(file, base_name, types):
    file.write(f'\nclass {base_name}Visitor(ABC):\n\n')
    for expr_types in types:
        type_name = expr_types.split(":")[0].strip()
        file.write("\t@abstractmethod\n")
        file.write(f"\tdef visit_{type_name.lower()}_{base_name.lower()}(self, {base_name.lower()}) -> None:\n")
        file.write("\t\traise NotImplementedError\n\n")

def define_ast(output_dir, base_name, types):
    path = output_dir + base_name.lower() + ".py"
    file = open(path, 'w', encoding='utf-8')
    file.write("from abc import ABC, abstractmethod\n")

    define_visitor(file, base_name, types)

    file.write(f'class {base_name}(ABC):\n\n')
    file.write("\t@abstractmethod\n")
    file.write(f"\tdef accept(self, visitor: {base_name}Visitor) -> None:\n")
    file.write("\t\traise NotImplementedError\n\n")

    for expr_types in types:
        class_name = expr_types.split(":")[0].strip()
        fields =  expr_types.split(":")[1].strip()
        file.write("\n")
        define_type(file, base_name, class_name, fields)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print("Usage: generate_ast.py <output directory>")
        sys.exit(0)
    else:
        output_dir = args[0]
        define_ast(output_dir, "Expr", expr)
        define_ast(output_dir, "Stmt", statements)
