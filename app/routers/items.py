from fastapi import APIRouter
from app.components.llms import prompts
from app.components.llms import engine
from app.components.file_parser import functions, find_routes
from app import models

router = APIRouter()


@router.get("/test_summary")
async def test_summary():

    result_dict = {}
    name = "FASTAPI TRIANGLE TEMPLETOS"
    url = "KAPPA"
    project_repository_path = "/Users/williambrach/Developer/hackkosice/hk-2024/full-stack-fastapi-template/backend"
    test_path = project_repository_path + "/app/tests"

    # TODO readme check
    readme_text = functions.merge_readme_contents(project_repository_path)

    if readme_text and readme_text != "":
        user_text, system_text = prompts.create_prompt_for_readme_summary(readme_text)
        readme_summary = engine.call_openai("gpt-4", system_text, user_text)


    print("README DONE")

    class_data_list = list()
    class_data_text = functions.find_attributes_models(project_repository_path)
    if class_data_text and class_data_text != "":
        user_text, system_text = prompts.create_promp_for_data_classes(class_data_text)
        class_data_summary = engine.call_ollama("zephyr", system_text, user_text)

        for key in class_data_text:

            user_text_comments, system_text_comments = (
                prompts.create_prompt_for_commenting_data_classes(class_data_text[key])
            )
            class_data_comments = engine.call_ollama(
                "zephyr", system_text_comments, user_text_comments
            )
            class_data_list.append({"name": key, "content": class_data_comments})

    print("CLASS DATA DONE")
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

    code_structure = functions.print_directory_structure(project_repository_path)

    result_dict[url] = {
        "name": name,
        "url": url,
        "function_to_code": function_name_to_code,
        "class_to_code": class_to_code,
        "function_to_test": fuction_to_test,
        "files": [],
        "readme": {"text": readme_text, "summary": readme_summary},
        "functions": [],
        "class_data": class_data_summary,
        "class_data_comments": class_data_list,
        "project_structure": code_structure,
        "business_stories": {},
    }
    try:
        import json

        json.dump(result_dict, open("data_2.json", "w"), indent=2)
    except Exception as e:
        print(e)

    return result_dict

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
                    "codellama", system_text_with_comments, user_text_with_comments
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
    print("functions done")
    # ds = models.convert_to_data_story(result_dict, url)
    # return ds

    story_summs = []
    result_dict[url]["business_stories"] = []
    for story_name in business_stories.keys():
        bs = {"name": story_name, "story": []}
        print(story_name)
        for story_route, story_functions in business_stories[story_name].items():
            print(story_route)

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

            story_user_prompt, story_system_prompt = (
                prompts.create_prompt_for_story_order(prompt)
            )
            story_summary = engine.call_openai(
                "gpt-4", story_system_prompt, story_user_prompt
            )
            story_summary = prompts.fix_analysis_response(story_summary)
            story_summs.append(story_summary)

            prompt = ""
            for s in story_summary:
                i = [s_i["name"] for s_i in s["items"]]
                for z in i:
                    for func in result_dict[url]["functions"]:
                        if z == func["name"]:
                            prompt += f"""function name : {f}, 
                            function summary :  {func['summary']},
                            function code : {func['code']}"""

            story_user_prompt, story_system_prompt = prompts.create_prompt_for_story(
                prompt
            )
            story = engine.call_openai("gpt-4", story_system_prompt, story_user_prompt)
            bs["story"].append(
                {
                    "route": story_route,
                    "functions": fix_story_functions,
                    "order_summary": story_summary,
                    "story": story,
                }
            )
        result_dict[url]["business_stories"].append(bs)

    print(result_dict)
    try:
        import json

        json.dump(result_dict, open("data.json", "w"), indent=2)
    except Exception as e:
        print(e)

    return result_dict


#             story_summary = """
#                         Based on the business story timeline, the categories can be grouped into "User Management", "Email Management", and "Security Management". Here is the JSON schema format:

# ```json
# {
#   "title": "AnalysisResponse",
#   "type": "object",
#   "required": ["groupings"],
#   "properties": {
#     "groupings": {
#       "type": "array",
#       "title": "Groupings",
#       "items": {
#         "$ref": "#/$defs/Grouping"
#       }
#     }
#   },
#   "$defs": {
#     "GroupItem": {
#       "type": "object",
#       "title": "GroupItem",
#       "required": ["name"],
#       "properties": {
#         "name": {
#           "type": "string",
#           "title": "Name"
#         }
#       }
#     },
#     "Grouping": {
#       "type": "object",
#       "title": "Grouping",
#       "required": ["group_name", "items"],
#       "properties": {
#         "group_name": {
#           "type": "string",
#           "title": "Group Name"
#         },
#         "items": {
#           "type": "array",
#           "title": "Items",
#           "items": {
#             "$ref": "#/$defs/GroupItem"
#           }
#         }
#       }
#     }
#   },
#   "groupings": [
#     {
#       "group_name": "User Management",
#       "items": [
#         {
#           "name": "get_user_by_email"
#         },
#         {
#           "name": "create_user"
#         }
#       ]
#     },
#     {
#       "group_name": "Email Management",
#       "items": [
#         {
#           "name": "generate_new_account_email"
#         },
#         {
#           "name": "send_email"
#         }
#       ]
#     },
#     {
#       "group_name": "Security Management",
#       "items": [
#         {
#           "name": "get_password_hash"
#         }
#       ]
#     }
#   ]
# }
# ```
#             """
