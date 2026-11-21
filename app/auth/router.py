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
def register_form(
    request: Request, 
    email: str = Form(...), 
    phone: str = Form(...), 
    password: str = Form(...), 
    password_confirm: str = Form(...), 
    accept_terms: str = Form(None), 
    db: Session = Depends(get_db)
):
    try:
        # Валидация данных через Pydantic
        payload = RegisterIn(
            email=email, 
            phone=phone, 
            password=password, 
            password_confirm=password_confirm, 
            accept_terms=bool(accept_terms)
        )
    except Exception as e:
        # Извлекаем понятный текст ошибки из Pydantic
        error_msg = str(e).split('Value error, ')[-1] if 'Value error, ' in str(e) else "Ошибка валидации данных"
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": error_msg}, status_code=400)

    # Проверка на существующего пользователя
    if db.query(User).filter((User.email == payload.email) | (User.phone == payload.phone)).first():
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Email или телефон уже заняты"}, status_code=400)

    # ХЕШИРОВАНИЕ ПАРОЛЯ (обрезка до 72 байт для bcrypt)
    safe_password = payload.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    user = User(
        email=payload.email, 
        phone=payload.phone, 
        password_hash=pwd_context.hash(safe_password), 
        terms_accepted_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return resp

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login-form")
def login_form(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    
    # Обрезка пароля при проверке (на случай, если пользователь ввел длинный пароль)
    safe_password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    if not user or not pwd_context.verify(safe_password, user.password_hash):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Неверный email или пароль"}, status_code=400)
    
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return resp

@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/auth/login", status_code=303)
    resp.delete_cookie("user_id")
    return resp
