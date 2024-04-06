from fastapi import APIRouter, Depends, HTTPException
from app.components.llms import prompts
from app.components.llms import engine
from app.components.file_parser import functions, find_routes

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
    print("-----------------")
    print(fuction_to_test.keys())
    business_stories = find_routes.main(project_repository_path)
    for story_name in business_stories.keys():
        for story_route, story_functions in business_stories[story_name].items():
            for function in story_functions:
                if "router" in function:
                    continue
                if "." in function:
                    function = function.split(".")[1]

                code = function_name_to_code.get(function, " ")
                test = fuction_to_test.get(function, " ")

                found_code = True if code != " " else False
                found_test = True if test != " " else False

    #         user_text, system_text = prompts.create_prompt_for_summary(function_code)
    #         summary = engine.call_ollama("zephyr", system_text, user_text)

    #         user_text_with_comments, system_text_with_comments = prompts.create_prompt_for_commenting(function_code)
    #         code_with_comments = engine.call_ollama("zephyr", system_text_with_comments, user_text_with_comments)

    return business_stories

    # function_code = """
    # def calculate_area(radius):
    # pi = 3.14
    # return pi * (radius ** 2)
    # """

    # return {"summary": summary, "code_with_comments": code_with_comments}
