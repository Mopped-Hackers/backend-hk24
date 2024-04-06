import ast
import glob
import os


def find_py_files(root_directory):
    py_files = []
    for root, dirs, files in os.walk(root_directory):
        # Remove directories named 'test' or 'tests' from traversal
        dirs[:] = [
            d for d in dirs if "test" not in d
        ]  # This modifies the dirs list in place
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files


def read_file(file_path):
    """Read the source code from a file and parse it into an AST."""
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()
    return ast.parse(source_code), source_code


def extract_functions(file_path):
    """Extract function names and their source code from the AST."""
    parsed_code, source_code = read_file(file_path)
    functions_with_code = []
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.FunctionDef):
            function_code = ast.get_source_segment(source_code, node)
            functions_with_code.append((node.name, function_code))
    return functions_with_code


def extract_class_attributes(file_path):
    """Extract class names and attributes assigned to self in their __init__ method."""
    parsed_code, source_code = read_file(file_path)
    class_definitions_with_attributes = []
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            self_attributes = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if (
                                    isinstance(target, ast.Attribute)
                                    and isinstance(target.value, ast.Name)
                                    and target.value.id == "self"
                                ):
                                    self_attributes.append(target.attr)
            class_definitions_with_attributes.append((class_name, self_attributes))
    return class_definitions_with_attributes


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.function_calls_within_functions = {}
        self.current_function_node = None  # Initialize to None

    def visit_FunctionDef(self, node):
        # Save the current function node before visiting children
        previous_function_node = self.current_function_node
        self.current_function_node = node
        self.generic_visit(node)
        # Restore the previous function node after visiting children
        self.current_function_node = previous_function_node

    def visit_Call(self, node):
        if self.current_function_node:
            # Check if the call is a simple function call (e.g., function_name())
            if isinstance(node.func, ast.Name):
                function_call_name = node.func.id
            # Additionally, check if the call is a method call (e.g., self.method())
            elif (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"
            ):
                function_call_name = f"{node.func.value.id}.{node.func.attr}"
            else:
                self.generic_visit(node)
                return  # Exit the method if neither condition is met

            outer_function_code = ast.get_source_segment(
                self.source_code, self.current_function_node
            )
            self.function_calls_within_functions[function_call_name] = (
                outer_function_code
            )
        self.generic_visit(node)
        self.dog()

    def dog(self):
        pass


def extract_function_calls(file_path):
    parsed_code, source_code = read_file(file_path)
    visitor = FunctionCallVisitor(source_code)
    visitor.visit(parsed_code)
    return visitor.function_calls_within_functions


# Call this to get function_inside_func: content of function and name
def find_py_files_recursively(directory):
    """Find all Python files recursively in the specified directory and its subdirectories."""
    py_files = glob.glob(f"{directory}/**/*.py", recursive=True)

    all_function_calls = []
    for file_path in py_files:
        function_calls = extract_function_calls(file_path)

        all_function_calls.append(function_calls)

    flattened_dict = {}
    for d in all_function_calls:
        for key, value in d.items():

            # This will update the dictionary with the new key-value pair
            # If a key is repeated, its value will be overwritten with the last occurrence
            flattened_dict.setdefault(key, []).append(value)
    return flattened_dict


if __name__ == "__main__":
    # Assuming 'file_path' is defined and points to a valid Python file.
    file_path = "C:\\Users\\Peter\\Desktop\\hk\\find_functions.py"

    # Extract functions and class attributes
    functions = extract_functions(file_path)
    class_attrs = extract_class_attributes(file_path)

    func_inside_func = find_py_files_recursively("C:\\Users\\Peter\\Desktop\\hk")
