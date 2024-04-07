from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from typing import List, Optional
import json


def create_prompt_for_summary(function_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("summarisation_user.txt")
    data = {
        "function_code": function_content,
    }
    user_text = user_template.render(data)

    system_template = env.get_template("summarisation_system.txt")
    system_text = system_template.render()
    return user_text, system_text


def create_prompt_for_summary_with_test(function_content: str, test_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("summarisation_user.txt")
    data = {"function_code": function_content, "test_codes": test_content}
    user_text = user_template.render(data)

    system_template = env.get_template("summarisation_system_with_test.txt")
    system_text = system_template.render()
    return user_text, system_text


def create_prompt_for_commenting(function_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("comments_user.txt")
    data = {"function_code": function_content}
    user_text = user_template.render(data)

    system_template = env.get_template("comments_system.txt")
    system_text = system_template.render()
    return user_text, system_text

def create_prompt_for_commenting_data_classes(function_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("dataclasses_comments_user.txt")
    data = {"dataclass": function_content}
    user_text = user_template.render(data)

    system_template = env.get_template("dataclasses_comments_system.txt")
    system_text = system_template.render()
    return user_text, system_text


def create_prompt_for_readme_summary(readme_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("readme_user.txt")
    data = {"readme_text": readme_content}
    user_text = user_template.render(data)

    system_template = env.get_template("readme_system.txt")
    system_text = system_template.render()
    return user_text, system_text


class GroupItem(BaseModel):
    name: str


class Grouping(BaseModel):
    group_name: str
    items: List[GroupItem]


class AnalysisResponse(BaseModel):
    groupings: List[Grouping]


def get_analysis_response_json_schema():
    schema = AnalysisResponse.schema()
    schema_json = json.dumps(schema, indent=2)
    return schema_json


def create_prompt_for_story_order(story_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("story_order_user.txt")
    data = {"story": story_content, "json_schema": get_analysis_response_json_schema()}
    user_text = user_template.render(data)

    system_template = env.get_template("story_order_system.txt")
    system_text = system_template.render()
    return user_text, system_text


def create_prompt_for_story(story_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("story_user.txt")
    data = {"story": story_content}
    user_text = user_template.render(data)

    system_template = env.get_template("story_system.txt")
    system_text = system_template.render()
    return user_text, system_text


def create_promp_for_data_classes(data_classes_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("data_class_user.txt")
    data = {"data_prompt": data_classes_content}
    user_text = user_template.render(data)

    system_template = env.get_template("data_class_system.txt")
    system_text = system_template.render()
    return user_text, system_text


def fix_analysis_response(response: str):
    try:
        response = response.split("```")[1:2][0].replace("json", "")
        response = json.loads(response)["groupings"]
        return response
    except Exception as e:
        print(e)
        response = []

    try:
        response = json.loads(response)
        response = response["groupings"]
        return response
    except Exception as e:
        print(e)
        response = []

    try:
        response = json.loads(response.replace("```", "").replace("json", ""))
        response = response["groupings"]
        return response
    except Exception as e:
        print(e)
        response = []

    return response
