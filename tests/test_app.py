from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import app, affiliates

client = TestClient(app)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert affiliates[0]["slug"] in response.text


def test_detail_page():
    slug = affiliates[0]["slug"]
    response = client.get(f"/affiliate/{slug}")
    assert response.status_code == 200
    assert affiliates[0]["brand"] in response.text


def test_detail_not_found():
    response = client.get("/affiliate/non-existent-slug")
    assert response.status_code == 404


def test_sitemap():
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert affiliates[0]["slug"] in response.text


def test_search():
    response = client.get(f"/search?query={affiliates[0]['brand']}")
    assert response.status_code == 200
    assert affiliates[0]["slug"] in response.text


def test_robots():
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "Allow: /" in response.text
