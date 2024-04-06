from fastapi import Response, Request, HTTPException, Header


def raise_http_exception(recipe, premium):

    raise HTTPException(
        403,
        "!!!!!!!",
    )
