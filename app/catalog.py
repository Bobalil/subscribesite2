from sqlalchemy.orm import Session
from .models import Service, ExecutionMode
from .db import SessionLocal

def seed_services():
    db: Session = SessionLocal()
    try:
        if db.query(Service).count() > 0:
            return
        services = [
            Service(name="Яндекс Плюс", price=39900, icon="🎵", execution_mode=ExecutionMode.LINK),
            Service(name="Netflix", price=120000, icon="🎬", execution_mode=ExecutionMode.MANUAL),
            Service(name="Spotify", price=29900, icon="🎧", execution_mode=ExecutionMode.MANUAL),
            Service(name="ChatGPT Plus", price=199000, icon="🤖", execution_mode=ExecutionMode.MANUAL),
        ]
        db.add_all(services)
        db.commit()
    finally:
        db.close()