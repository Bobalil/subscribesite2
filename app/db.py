from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# По умолчанию SQLite, но на Fly.io лучше использовать файл в /tmp или подключить Postgres
# На Fly.io файловая система read-only, поэтому пишем в /tmp
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/wallet.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
