import json
import os
from pathlib import Path

from fastapi import FastAPI
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
    urls = [f"https://evangeler.com/affiliate/{d['slug']}" for d in affiliate_details]
    xml_parts = ["<?xml version='1.0' encoding='UTF-8'?>", "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    for url in urls:
        xml_parts.append("  <url><loc>%s</loc></url>" % url)
    xml_parts.append("</urlset>")
    return "\n".join(xml_parts)


@app.get("/robots.txt")
async def robots():
    return "User-agent: *\nAllow: /"


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
