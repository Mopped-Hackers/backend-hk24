from jinja2 import Environment, FileSystemLoader


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

def create_prompt_for_readme_summary(readme_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("readme_user.txt")
    data = {"readme_text": readme_content}
    user_text = user_template.render(data)

    system_template = env.get_template("readme_system.txt")
    system_text = system_template.render()
    return user_text, system_text

def create_prompt_for_story_order(story_content: str):
    env = Environment(loader=FileSystemLoader("app/components/llms/agent_templates"))
    user_template = env.get_template("story_user.txt")
    data = {"story": story_content}
    user_text = user_template.render(data)

    system_template = env.get_template("story_system.txt")
    system_text = system_template.render()
    return user_text, system_text
