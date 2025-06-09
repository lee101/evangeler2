from fastapi.testclient import TestClient
import sys, os, json
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


def test_submit_form_get():
    response = client.get("/submit")
    assert response.status_code == 200
    assert "Submit a New Affiliate Program" in response.text


def test_submit_form_post(tmp_path, monkeypatch):
    submissions_file = tmp_path / "affiliate_submissions.json"

    # patch submission path in main
    monkeypatch.setattr("main.SUBMISSION_FILE", submissions_file)

    data = {
        "brand": "TestBrand",
        "description": "Desc",
        "website": "https://example.com",
        "keywords": "test",
        "commission": "5%",
        "email": "test@example.com",
    }
    response = client.post("/submit", data=data)
    assert response.status_code == 200
    saved = json.loads(submissions_file.read_text())
    assert saved[-1]["brand"] == "TestBrand"


def test_submit_invalid_url(tmp_path, monkeypatch):
    submissions_file = tmp_path / "affiliate_submissions.json"
    monkeypatch.setattr("main.SUBMISSION_FILE", submissions_file)

    data = {
        "brand": "Brand2",
        "description": "Desc",
        "website": "example.com",
    }
    response = client.post("/submit", data=data)
    assert response.status_code == 400
    assert "Invalid website URL." in response.text


def test_view_submissions(tmp_path, monkeypatch):
    submissions_file = tmp_path / "affiliate_submissions.json"
    monkeypatch.setattr("main.SUBMISSION_FILE", submissions_file)
    submissions_file.write_text(json.dumps([{"brand": "A", "website": "http://a"}]))
    response = client.get("/submissions")
    assert response.status_code == 200
    assert "A" in response.text


def test_honeypot_field(tmp_path, monkeypatch):
    submissions_file = tmp_path / "affiliate_submissions.json"
    monkeypatch.setattr("main.SUBMISSION_FILE", submissions_file)

    data = {
        "brand": "SpamBrand",
        "description": "Desc",
        "website": "https://spam.com",
        "nickname": "bot",
    }
    response = client.post("/submit", data=data)
    assert response.status_code == 200
    # file should remain empty
    assert not submissions_file.exists() or submissions_file.read_text() == "[]"
