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
    result_dict = {}
    url = "KAPPA"
    project_repository_path = "/Users/williambrach/Developer/hackkosice/hk-2024/full-stack-fastapi-template/backend"
    test_path = project_repository_path + "/app/tests"

    # TODO readme check
    readme_text = functions.merge_readme_contents(project_repository_path)

    if readme_text and readme_text != "":
        user_text, system_text = prompts.create_prompt_for_readme_summary(readme_text)
        # readme_summary = engine.call_openai("gpt-4", system_text, user_text)
        readme_summary = " "

    root_dir = project_repository_path + "/"

    python_files = functions.find_py_files(root_dir)

    function_name_to_code = {}
    class_to_code = {}
    function_name_to_path = {}
    for file in python_files:
        project_functions = functions.extract_functions(file)
        python_classes = functions.extract_class_attributes(file)
        for function_name, function_code in project_functions:
            function_name_to_code[function_name] = function_code
            function_name_to_path[function_name] = file
        for class_name, attributes in python_classes:
            class_to_code[class_name] = attributes

    fuction_to_test = functions.find_py_files_recursively(test_path)
    business_stories = find_routes.main(project_repository_path)

    result_dict[url] = {
        "function_to_code": function_name_to_code,
        "class_to_code": class_to_code,
        "function_to_test": fuction_to_test,
        "files": [],
        "readme": {"text": readme_text, "summary": readme_summary},
        "functions": [],
        "business_stories": {},
    }

    for story_name in business_stories.keys():
        for story_route, story_functions in business_stories[story_name].items():
            for function in story_functions:
                if "router" in function:
                    continue
                if "." in function:
                    function = function.split(".")[1]

                code = function_name_to_code.get(function, " ")
                test = fuction_to_test.get(function, " ")
                if code == " ":
                    continue

                found_test = True if test != " " else False
                if found_test:
                    user_text, system_text = (
                        prompts.create_prompt_for_summary_with_test(code, test)
                    )
                else:
                    user_text, system_text = prompts.create_prompt_for_summary(code)
                summary = engine.call_ollama("zephyr", system_text, user_text)
                # summary = " "

                user_text_with_comments, system_text_with_comments = (
                    prompts.create_prompt_for_commenting(code)
                )
                # code_with_comments = " "
                code_with_comments = engine.call_ollama(
                    "zephyr", system_text_with_comments, user_text_with_comments
                )
                result_dict[url]["functions"].append(
                    {
                        "name": function,
                        "path": function_name_to_path.get(function, " "),
                        "code": code,
                        "summary": summary,
                        "code_with_comments": code_with_comments,
                        "test": test,
                    }
                )

    story_summs = []
    for story_name in business_stories.keys():
        for story_route, story_functions in business_stories[story_name].items():
            fix_story_functions = []
            for function in story_functions:
                if "router" in function:
                    continue
                if "." in function:
                    function = function.split(".")[1]
                fix_story_functions.append(function)
            

            index = 1
            prompt = ""
            for f in fix_story_functions:
                for func in result_dict[url]["functions"]:
                    if f == func["name"]:
                        prompt += f"{index}. {f} -> {func['summary']}"
                        index += 1
                        break
                    
            story_user_prompt, story_system_prompt = prompts.create_prompt_for_story_order(prompt)
            story_summary = engine.call_openai("gpt-4", story_system_prompt, story_user_prompt)
            story_summs.append(story_summary)
    

    return {
        "prompts": story_summs
    }

    # function_code = """
    # def calculate_area(radius):
    # pi = 3.14
    # return pi * (radius ** 2)
    # """

    # return {"summary": summary, "code_with_comments": code_with_comments}
