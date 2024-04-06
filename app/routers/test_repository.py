# test_repository.py
import pytest
from fastapi.testclient import TestClient
from app import main  # assuming the FastAPI application is defined in a file named main.py
from models import Log, DataStory  # assuming these models are defined in a file named models.py

@pytest.fixture
def client():
    return TestClient(main)


def test_save_story(client):
    log = Log(...)  # fill in with appropriate data
    response = client.post("/logs", json=log.dict())
    assert response.status_code == 200


def test_insert_data_story(client):
    data_story = DataStory(...)  # fill in with appropriate data
    response = client.post("/stories", json=data_story.dict())
    assert response.status_code == 200

def test_get_all_data_stories(client):
    response = client.get("/stories")
    assert response.status_code == 200


    ###################################

def test_get_logs(client):
    response = client.get("/logs")
    assert response.status_code == 200

def test_get_log_by_id(client):
    log_id = "some_id"  # replace with a valid log_id
    response = client.get(f"/logs/{log_id}")
    assert response.status_code == 200

def test_delete_log_by_id(client):
    log_id = "some_id"  # replace with a valid log_id
    response = client.delete(f"/logs/{log_id}")
    assert response.status_code == 200
