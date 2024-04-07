import ast
import glob
import os
import json
import find_routes


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

def merge_readme_contents(start_directory):
    """
    Finds all README files in the specified directory and its subdirectories,
    then merges their contents into a single string and returns it.
    
    :param start_directory: Directory to start searching for README files.
    :return: A string containing the merged contents of all README files.
    """
    # Use glob to find all README files (case-insensitive search)
    readme_files = glob.glob(os.path.join(start_directory, '**', '[Rr][Ee][Aa][Dd][Mm][Ee]*'), recursive=True)
    
    merged_content = ""  # Initialize an empty string to store the merged content
    
    for readme_file in readme_files:
        with open(readme_file, 'r', encoding='utf-8') as infile:
            merged_content += infile.read() + '\n\n'  # Read each file and append its content followed by two newlines
    
    return merged_content

def extract_functions(file_path):
    """Extract function names and their source code from the AST."""
    parsed_code, source_code = read_file(file_path)
    functions_with_code = []
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.FunctionDef):
            function_code = ast.get_source_segment(source_code, node)
            functions_with_code.append((node.name, function_code))
    return functions_with_code

def get_function_names(filename, first_items):
    """
    Gets the names of specific functions defined in a Python file.

    Parameters:
    - filename (str): The path to the Python file.
    - first_items (list): A list of function names to include.

    Returns:
    - List of function names.
    """
    function_names = []
    with open(filename, "r") as file:
        node = ast.parse(file.read(), filename=filename)
        for item in node.body:
            if (isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef)) and item.name in first_items:
                function_names.append(item.name)
    return function_names

def print_directory_structure(startpath):
    startpath = 'C:\\Users\\Peter\\Desktop\\full-stack-fastapi-template\\backend'
    """
    Returns the directory structure of a given path and lists function names for Python files.

    Parameters:
    - startpath (str): The root directory path from which to start listing the structure.

    Returns:
    - Dict: The structure of the directory and function names.
    """
    functions = find_routes.main(startpath)
    structure = {}
    for root, dirs, files in os.walk(startpath, topdown=True):
        path_key = root.replace(startpath, '').strip(os.sep)
        if not path_key:  # If path_key is empty, meaning it's the root
            path_key = "root"
        structure[path_key] = {"dirs": {}, "files": {}}
        for dir_name in dirs:
            structure[path_key]['dirs'][dir_name] = {}
        for f in files:
            file_path = os.path.join(root, f)
            if f.endswith('.py'):
                first_items = [item.split('.')[-1] for _, endpoints in functions.items() for _, functions in endpoints.items() for item in functions]

                structure[path_key]['files'][f] = get_function_names(file_path, first_items)
    structure = json.dumps(structure)
    return structure

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
            function_call_name = None

            # Check if the call is a simple function call (e.g., function_name())
            if isinstance(node.func, ast.Name):
                function_call_name = node.func.id
            
            # Check if the call is a method call on any object (e.g., object.method() or self.method())
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                # This will now include method calls on any object, not just 'self'
                function_call_name = f"{node.func.value.id}.{node.func.attr}"
            
            if function_call_name:
                outer_function_code = ast.get_source_segment(self.source_code, self.current_function_node)
                self.function_calls_within_functions[function_call_name] = outer_function_code
                
        self.generic_visit(node)


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

class ClassVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.classes = {}

    def visit_ClassDef(self, node):
        class_name = node.name
        attributes = {}
        methods = {}
        # Capture the entire class code from the source
        class_code = ast.unparse(node) if hasattr(ast, 'unparse') else 'Class code unavailable'

        for n in node.body:
            if isinstance(n, ast.Assign):
                # Handle simple assignments (without explicit type annotations)
                for target in n.targets:
                    if isinstance(target, ast.Name):
                        attributes[target.id] = target.id
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Capture method names
                methods[n.name] = ast.unparse(n) if hasattr(ast, 'unparse') else f'{n.name} method code unavailable'

        self.classes[class_name] = class_code
        self.generic_visit(node)

def find_attributes_models(file_path):
    py_files = glob.glob(f"{file_path}/**/*.py", recursive=True)
    visitor = ClassVisitor()
    for py_file in py_files:
        parsed_code, source_code = read_file(py_file)
        visitor.visit(parsed_code)
        classes_and_attributes = visitor.classes
    return classes_and_attributes


if __name__ == "__main__":
    # Assuming 'file_path' is defined and points to a valid Python file.
    file_path = "C:\\Users\\Peter\\Desktop\\hk\\find_functions.py"

    # Extract functions and class attributes
    functions = extract_functions(file_path)
    class_attrs = extract_class_attributes(file_path)

    func_inside_func = find_py_files_recursively("C:\\Users\\Peter\\Desktop\\hk")
