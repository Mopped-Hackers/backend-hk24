from fastapi import APIRouter, Depends, HTTPException
from app.components.llms import prompts
from app.components.llms import engine 
router = APIRouter()

@router.get("/items")
async def read_items():
    return {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/test_summary")
async def test_summary():

    function_code = """
    def calculate_area(radius):
    pi = 3.14
    return pi * (radius ** 2)
    """
    user_text, system_text = prompts.create_prompt_for_summary(function_code)
    summary = engine.call_ollama("zephyr", system_text, user_text)

    user_text_with_comments, system_text_with_comments = prompts.create_prompt_for_commenting(function_code)
    code_with_comments = engine.call_ollama("zephyr", system_text_with_comments, user_text_with_comments)

    return {"summary": summary, "code_with_comments": code_with_comments}
