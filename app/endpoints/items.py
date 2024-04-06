from fastapi import APIRouter, Depends, HTTPException
from app.components.llms import prompts
from app.components.llms import engine
from app.components.file_parser import functions

router = APIRouter()


@router.get("/items")
async def read_items():
    return {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/test_summary")
async def test_summary():

    project_repository_path = "/Users/williambrach/Developer/hackkosice/hk-2024/full-stack-fastapi-template/backend"
    test_path = project_repository_path + "/app/tests"

    # TODO readme check
    readme_text = ""

    root_dir = project_repository_path + "/"

    python_files = functions.find_py_files(root_dir)

    function_name_to_code = {}
    class_to_code = {}
    for file in python_files:
        project_functions = functions.extract_functions(file)
        python_classes = functions.extract_class_attributes(file)
        for function_name, function_code in project_functions:
            function_name_to_code[function_name] = function_code
        for class_name, attributes in python_classes:
            class_to_code[class_name] = attributes

    fuction_to_test = functions.find_py_files_recursively(test_path)
    return fuction_to_test

    # function_code = """
    # def calculate_area(radius):
    # pi = 3.14
    # return pi * (radius ** 2)
    # """
    # user_text, system_text = prompts.create_prompt_for_summary(function_code)
    # summary = engine.call_ollama("zephyr", system_text, user_text)

    # user_text_with_comments, system_text_with_comments = prompts.create_prompt_for_commenting(function_code)
    # code_with_comments = engine.call_ollama("zephyr", system_text_with_comments, user_text_with_comments)

    # return {"summary": summary, "code_with_comments": code_with_comments}
