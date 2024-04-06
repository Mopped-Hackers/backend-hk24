import ast
import os


class EndpointVisitor(ast.NodeVisitor):
    def __init__(self):
        self.endpoints = {}
        self.all_functions = {}

    def visit_FunctionDef(self, node):
        # Collect calls for all functions
        self.all_functions[node.name] = {'functions': self.get_function_calls(node)}

        # Check for decorators that indicate an endpoint
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'attr') and decorator.func.attr in ['get',
                                                                                                               'post',
                                                                                                               'put',
                                                                                                               'delete']:
                endpoint_path = decorator.args[0].s if decorator.args else ''
                if node.name not in self.endpoints:
                    self.endpoints[node.name] = {'path': endpoint_path, 'functions': []}
                self.endpoints[node.name]['functions'].extend(self.get_function_calls(node))

        self.generic_visit(node)

    def get_function_calls(self, node):
        function_calls = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    function_calls.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    func_call_parts = []
                    current = n.func
                    while isinstance(current, ast.Attribute):
                        func_call_parts.append(current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        func_call_parts.append(current.id)
                    func_call_parts.reverse()
                    full_func_call = '.'.join(func_call_parts)
                    function_calls.append(full_func_call)
        return function_calls


def parse_file_to_ast(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        source_code = file.read()
    return ast.parse(source_code)


def is_python_file(file_name):
    return file_name.endswith('.py')


def process_file(file_path):
    ast_tree = parse_file_to_ast(file_path)
    visitor = EndpointVisitor()
    visitor.visit(ast_tree)
    return visitor.endpoints, visitor.all_functions


def find_functions_starting_with_def(directory_path):
    functions = []
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        for line in file:
                            stripped_line = line.strip()
                            if stripped_line.startswith('def '):
                                function_name = stripped_line.split('(')[0][4:]
                                file_name = file_name.replace('.py', '')
                                functions.append(f"{file_name}.{function_name}")
                                functions.append(function_name)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return functions


def append_dependencies_functions(functions, new_functions):
    for key, values in functions.items():
        for key1, values1 in new_functions.items():
            if key1 in values:
                for value in values1:
                    if value not in values:
                        functions[key].append(value)

    return functions


def make_output(functions):
    output = {}
    for key, values in functions.items():
        parsed_key = key.split(' ')[0]
        ep = key.split(' ')[1]
        if parsed_key not in output:
            output[parsed_key] = {}
        output[parsed_key][ep] = values

    return output


def remove_non_local_functions(functions, local_functions):
    for k, v in functions.items():
        router = v[0]
        functions[k] = [x for x in v if x in local_functions]
        functions[k].append(router)

    return functions


def main(directory_path):
    functions = {}
    new_functions = {}
    local_functions = find_functions_starting_with_def(directory_path)
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if is_python_file(file_name):
                file_path = os.path.join(root, file_name)
                try:
                    endpoints, all_functions = process_file(file_path)
                    for endpoint, details in endpoints.items():
                        ff = details['functions']
                        key = f"{file_name} {details['path']}"
                        functions[key] = ff

                    for func, details in all_functions.items():
                        ff = details['functions']
                        file_name = file_name.replace('py', '')
                        key = f"{file_name}{func}"
                        new_functions[key] = ff

                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

    functions = append_dependencies_functions(functions, new_functions)
    functions = remove_non_local_functions(functions, local_functions)
    output = make_output(functions)
    print(output)
    return output


if __name__ == "__main__":
    ABSOLUTE_PATH = os.path.abspath('backend')
    main(ABSOLUTE_PATH)