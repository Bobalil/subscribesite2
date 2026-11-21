from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, Service, UserSubscription, Wallet, LedgerEntry, TxType
from ..auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_wallet(db: Session, user_id: int) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = get_wallet(db, user.id)
    entries = db.query(LedgerEntry).filter(LedgerEntry.user_id == user.id).order_by(LedgerEntry.id.desc()).limit(20).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "wallet": wallet, "entries": entries})

@router.post("/wallet/topup")
def topup(amount: int = Form(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if amount <= 0:
        return RedirectResponse("/?error=amount", status_code=303)
    amount_kop = amount * 100
    wallet = get_wallet(db, user.id)
    wallet.balance += amount_kop
    db.add(LedgerEntry(user_id=user.id, entry_type=TxType.TOPUP, amount=amount_kop, description="Пополнение кошелька"))
    db.commit()
    return RedirectResponse("/", status_code=303)

@router.get("/subscriptions", response_class=HTMLResponse)
def subscriptions_page(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.is_active == True).all()
    mine = {s.service_id: s for s in db.query(UserSubscription).filter(UserSubscription.user_id == user.id).all()}
    return templates.TemplateResponse("subscriptions.html", {"request": request, "user": user, "services": services, "mine": mine})

@router.post("/subscriptions/toggle")
def toggle_sub(service_id: int = Form(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == user.id, UserSubscription.service_id == service_id).first()
    if sub:
        sub.is_active = not sub.is_active
    else:
        sub = UserSubscription(user_id=user.id, service_id=service_id, is_active=True, next_charge_at=datetime.utcnow() + timedelta(days=30))
        db.add(sub)
    db.commit()
    return RedirectResponse("/subscriptions", status_code=303)

@router.post("/subscriptions/pay-all")
def pay_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subs = db.query(UserSubscription).filter(UserSubscription.user_id == user.id, UserSubscription.is_active == True).all()
    if not subs:
        return RedirectResponse("/?error=empty", status_code=303)
    
    total = sum(s.service.price for s in subs)
    wallet = get_wallet(db, user.id)
    
    if wallet.balance < total:
        return RedirectResponse("/?error=funds", status_code=303)
    
    wallet.balance -= total
    db.add(LedgerEntry(user_id=user.id, entry_type=TxType.SUBSCRIPTION_PAYMENT, amount=-total, description=f"Оплата {len(subs)} подписок"))
    
    now = datetime.utcnow()
    for s in subs:
        s.next_charge_at = now + timedelta(days=30)
        
    db.commit()
    return RedirectResponse("/", status_code=303)