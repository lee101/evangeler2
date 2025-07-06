import json
import os
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

templates = Jinja2Templates(directory=".")
app = FastAPI(
    openapi_url="/static/openapi.json",
    docs_url="/swagger-docs",
    redoc_url="/redoc",
    title="Evangeler affliate marketing",
    description="Evangeler",
    # root_path="https://api.text-generator.io",
    version="1",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# rollbar_add_to(app) # rollbar doesnt work anymore?
# JINJA_ENVIRONMENT = jinja2.Environment(
#     loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
#     # extensions=['jinja2.ext.autoescape'],
#     # autoescape=True
# )
current_dir = Path(__file__).parent
debug = (
        os.environ.get("SERVER_SOFTWARE", "").startswith("Development")
        or os.environ.get("IS_DEVELOP", "") == 1
        or Path(current_dir / "models/debug.env").exists()
)

static_url = "/static"
# load json
if not debug:
    static_url = "https://static.netwrck.com/static"

with open('affiliates.json') as f:
    affiliates = json.load(f)

with open('affiliate_details.json') as f:
    affiliate_details = json.load(f)

details_lookup = {d['slug']: d for d in affiliate_details}

SUBMISSION_FILE = Path('affiliate_submissions.json')

def load_submissions():
    if SUBMISSION_FILE.exists():
        try:
            return json.loads(SUBMISSION_FILE.read_text())
        except Exception:
            return []
    return []

def save_submission(entry: dict):
    submissions = load_submissions()
    submissions.append(entry)
    SUBMISSION_FILE.write_text(json.dumps(submissions, indent=2))

import re

for site in affiliates:
    slug = re.sub(r'[^a-z0-9]+', '-', site['brand'].lower()).strip('-')
    site['slug'] = slug



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("templates/index.jinja2",
                                      {"request": request, "affiliates": affiliates, "static_url": static_url})


@app.get("/affiliate/{slug}")
async def affiliate_detail(slug: str, request: Request):
    detail = details_lookup.get(slug)
    if not detail:
        return templates.TemplateResponse("templates/not_found.jinja2", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "templates/detail.jinja2",
        {"request": request, "detail": detail, "static_url": static_url},
    )


@app.get("/sitemap.xml")
async def sitemap():
    urls = ["https://evangeler.com/", "https://evangeler.com/sitemap"] + [
        f"https://evangeler.com/affiliate/{d['slug']}" for d in affiliate_details
    ]
    xml_parts = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>",
    ]
    for url in urls:
        xml_parts.append("  <url><loc>%s</loc></url>" % url)
    xml_parts.append("</urlset>")
    return Response("\n".join(xml_parts), media_type="application/xml")


@app.get("/sitemap")
async def sitemap_html(request: Request):
    return templates.TemplateResponse(
        "templates/sitemap.jinja2",
        {"request": request, "affiliates": affiliates, "static_url": static_url},
    )


@app.get("/robots.txt")
async def robots():
    return "User-agent: *\nAllow: /\nSitemap: https://evangeler.com/sitemap.xml"


@app.get("/search")
async def search(request: Request, query: str = ""):
    q = query.lower()
    results = []
    if q:
        for site in affiliates:
            if q in site['brand'].lower() or q in site['description'].lower() or q in site['keywords'].lower():
                results.append(site)
    return templates.TemplateResponse(
        "templates/search.jinja2",
        {"request": request, "results": results, "query": query, "static_url": static_url},
    )


@app.get("/submit")
async def submit_form(request: Request):
    return templates.TemplateResponse(
        "templates/submit.jinja2",
        {"request": request, "error": ""},
    )


@app.post("/submit")
async def submit_affiliate(
    request: Request,
    brand: str = Form(...),
    description: str = Form(...),
    website: str = Form(...),
    keywords: str = Form(""),
    commission: str = Form(""),
    email: str = Form(""),
    nickname: str = Form(""),
):
    if not website.startswith("http"):
        return templates.TemplateResponse(
            "templates/submit.jinja2",
            {"request": request, "error": "Invalid website URL."},
            status_code=400,
        )

    slug = re.sub(r"[^a-z0-9]+", "-", brand.lower()).strip("-")
    if nickname:
        # likely bot submission, ignore but pretend success
        return templates.TemplateResponse(
            "templates/submit_success.jinja2", {"request": request}
        )

    entry = {
        "brand": brand,
        "slug": slug,
        "description": description,
        "website": website,
        "keywords": keywords,
        "commission": commission,
        "email": email,
    }
    save_submission(entry)
    return templates.TemplateResponse(
        "templates/submit_success.jinja2",
        {"request": request},
    )


@app.get("/submissions")
async def view_submissions(request: Request):
    submissions = load_submissions()
    return templates.TemplateResponse(
        "templates/submissions.jinja2",
        {"request": request, "submissions": submissions},
    )
