from fastapi import FastAPI, status, Request, Response, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from queue import Queue
from fastapi.routing import APIRouter

from .routers import repository
from .components.database.mongo import Mongo
from .models import Log
from typing import List
from .routers import items
from .routers import repository
from .routers import logs
from .routers import stories
import asyncio
from typing import Dict
from .models import getDummyStory
from app.components.pdf import pdf
from .models import DataStory, Functions, Readme
import json
from app.components.llms import prompts
from app.components.llms import engine
from app.components.file_parser import functions, find_routes

from .components.github import GithubRepo

from starlette.requests import Request
import os

from dotenv import load_dotenv

load_dotenv()

MONGODB_URL: str = os.getenv("MONGO_URI")


app = FastAPI()
router = APIRouter()


app.state.database = Mongo(MONGODB_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repository.router)
app.include_router(items.router)
app.include_router(logs.router)
app.include_router(stories.router)


queue = Queue()
status_dict: Dict[str, str] = {}


@app.post("/process")
async def process_url(url: str, background_tasks: BackgroundTasks):
    queue.put(url)
    status_dict[url] = "pending"
    background_tasks.add_task(process_queue)
    return {"message": "URL added to the queue"}


async def get_report(repo_dir, url, repo_name):
    result_dict = {}
    name = repo_name
    url = url

    if "full-stack-fastapi-template" in repo_dir:
        project_repository_path = repo_dir + "/backend"
    else:
        project_repository_path = repo_dir

    test_path = project_repository_path + "/app/tests"

    print("SETUP RDY")
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
        "business_stories": []
    }
    # return result_dict

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
            print(len(story_user_prompt), len(story_system_prompt))
            story_summary = engine.call_openai(
                "gpt-4", story_system_prompt, story_user_prompt
            )
            print("story summary done...")
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
            print(len(story_user_prompt), len(story_system_prompt))
            story = engine.call_openai("gpt-4", story_system_prompt, story_user_prompt)
            print("story done...")
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

        json.dump(result_dict, open("data_3.json", "w"), indent=2)
    except Exception as e:
        print(e)

    return result_dict


async def process_queue():
    database: Mongo = app.state.database
    while not queue.empty():
        url = queue.get()

        # if await database.getStory(url):
        #     await database.removeStory(url)
        #     # status_dict[url] = "done"
        #     # return

        repo_dir = GithubRepo.download_repo(url)
        repo_name = url.split("/")[-1]
        report = await get_report(repo_dir, url, repo_name)
        story = DataStory(**report[url])
        await database.saveStory(story)
        status_dict[url] = "done"


@app.get("/status")
async def get_status(request: Request, url: str):
    database: Mongo = request.app.state.database

    # DEMO OVERRIDE
    # url = "my-example-refactor"

    status: str = status_dict.get(url, "not found")
    if status == "done":
        story = await database.getStory(url)

        if story is None:
            return {"url": url, "status": status, "output": None}
        filename = f"./structured_output_{story.url}_{story.id}.pdf"
        output = f"{request.url.scheme}://{request.headers['host']}/static/{filename}"
        
        if url != "my-example-refactor":
            GithubRepo.remove_repo(url)
        return {"url": url, "status": status, "output": output}
    else:
        return {"url": url, "status": status, "output": None}


# DEMO GENERATION
@app.get("/test-pdf")
async def asf(request: Request, url: str):
    database: Mongo = request.app.state.database

    exampleStory = await database.getStory(url)

    pdf.main_from_json(exampleStory)

    return exampleStory
