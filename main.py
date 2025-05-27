import json
import os
from pathlib import Path
import re

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

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

def slugify(name: str) -> str:
    """Simple slugify helper for brand names."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower())
    return slug.strip("-")

static_url = "/static"
# load json
if not debug:
    static_url = "https://static.netwrck.com/static"

with open('affiliates.json') as f:
    affiliates = json.load(f)

for site in affiliates:
    if 'slug' not in site:
        site['slug'] = slugify(site['brand'])


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("templates/index.jinja2",
                                      {"request": request, "affiliates": affiliates, "static_url": static_url})


@app.get("/affiliate/{slug}")
async def affiliate_detail(slug: str, request: Request):
    for site in affiliates:
        if site.get('slug') == slug:
            return templates.TemplateResponse(
                "templates/detail.jinja2",
                {
                    "request": request,
                    "site": site,
                    "static_url": static_url,
                },
            )
    return {"error": "Affiliate not found"}
