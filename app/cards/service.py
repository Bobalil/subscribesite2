from sqlalchemy.orm import Session
from ..models import Card, CardStatus

def get_card(db: Session, user_id: int) -> Card | None:
    return db.query(Card).filter(Card.user_id == user_id).first()

def issue_card_for_user(db: Session, user_id: int, holder: str) -> Card:
    existing = get_card(db, user_id)
    if existing and existing.status != CardStatus.CLOSED:
        return existing

    # Заглушка (в будущем тут будет вызов API банка)
    card = Card(
        user_id=user_id,
        pan_masked="**** **** **** 1234",
        exp_month=12,
        exp_year=2030,
        holder=holder.upper(),
        external_id=f"mock_{user_id}",
        status=CardStatus.ACTIVE,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

def block_card(db: Session, card: Card) -> Card:
    card.status = CardStatus.BLOCKED
    db.commit()
    db.refresh(card)
    return card

def unblock_card(db: Session, card: Card) -> Card:
    card.status = CardStatus.ACTIVE
    db.commit()
    db.refresh(card)
    return card