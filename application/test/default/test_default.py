import requests
from fastapi.testclient import TestClient
from manage import app

client = TestClient(app)


def test_recipe_list():
    response = client.get("/")
    assert response.status_code == 200
