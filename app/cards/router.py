from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..auth import get_current_user
from . import service

router = APIRouter(prefix="/cards", tags=["cards"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def cards_page(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = service.get_card(db, user.id)
    return templates.TemplateResponse("cards/list.html", {"request": request, "card": card, "user": user})

@router.post("/issue")
def issue_card(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    holder = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
    card = service.issue_card_for_user(db, user.id, holder)
    return {"status": "ok", "card_id": card.id}

@router.post("/{card_id}/block")
def block_card(card_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = service.get_card(db, user.id)
    if not card or card.id != card_id:
        raise HTTPException(404, "Card not found")
    return service.block_card(db, card)
