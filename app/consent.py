from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/legal", tags=["legal"])
templates = Jinja2Templates(directory="app/templates")

COOKIE_CONSENT_NAME = "cookie_consent"
COOKIE_TERMS_NAME = "terms_accepted"


@router.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    return templates.TemplateResponse("legal/terms.html", {"request": request})


@router.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse("legal/privacy.html", {"request": request})


@router.get("/cookies", response_class=HTMLResponse)
def cookies(request: Request):
    return templates.TemplateResponse("legal/cookies.html", {"request": request})


@router.post("/accept-cookies")
def accept_cookies(response: Response):
    response.set_cookie(
        COOKIE_CONSENT_NAME, "1",
        max_age=365*24*3600, httponly=False, samesite="lax", secure=False,  # secure=True в проде
    )
    return {"ok": True}