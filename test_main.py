from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_index():
	response = client.get("/")

	assert response.status_code == 200

def test_error():
	response = client.get("/demo_error")

	assert response.status_code == 403