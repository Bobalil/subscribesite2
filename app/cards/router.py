from datetime import datetime
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..db import get_db
from ..models import User
from .schemas import RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register-form")
def register_form(request: Request, email: str = Form(...), phone: str = Form(...), password: str = Form(...), password_confirm: str = Form(...), accept_terms: str = Form(None), db: Session = Depends(get_db)):
    try:
        payload = RegisterIn(email=email, phone=phone, password=password, password_confirm=password_confirm, accept_terms=bool(accept_terms))
    except Exception as e:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": str(e)}, status_code=400)

    if db.query(User).filter((User.email == payload.email) | (User.phone == payload.phone)).first():
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Email или телефон уже заняты"}, status_code=400)

    user = User(email=payload.email, phone=payload.phone, password_hash=pwd_context.hash(payload.password), terms_accepted_at=datetime.utcnow())
    db.add(user)
    db.commit()

    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return resp

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login-form")
def login_form(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Неверный email или пароль"}, status_code=400)
    
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return resp

@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/auth/login", status_code=303)
    resp.delete_cookie("user_id")
    return resp