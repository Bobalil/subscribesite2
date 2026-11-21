import os
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from .db import Base, engine, get_db
from . import models
from .catalog import seed_services
from .auth import get_current_user

from .auth.router import router as auth_router
from .cards.router import router as cards_router
from .consent import router as legal_router
from .currency import router as currency_router
from .routers.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)
try:
    seed_services()
except Exception as e:
    print(f"DB Seed Error: {e}")

app = FastAPI(title="Сайт подписок")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(cards_router)
app.include_router(legal_router)
app.include_router(currency_router)
app.include_router(dashboard_router) # Подключаем главную страницу и подписки