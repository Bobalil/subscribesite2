import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")
os.environ["APP_SECRET"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402


def setup_module():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()


def test_full_flow():
    with TestClient(app) as client:
        r = client.post("/register", data={"email": "a@b.c", "password": "secret"}, follow_redirects=False)
        assert r.status_code == 303

        r = client.post("/wallet/topup", data={"amount": "1000"}, follow_redirects=False)
        assert r.status_code == 303
        location = r.headers["location"]

        r = client.post(f"{location}/confirm", follow_redirects=False)
        assert r.status_code == 303

        r = client.get("/")
        assert "1000.00 ₽" in r.text

        db = SessionLocal()
        user = db.query(User).filter(User.email == "a@b.c").first()
        user.is_admin = True
        db.commit()
        db.close()

        r = client.post("/subscriptions/toggle", data={"service_id": 1}, follow_redirects=False)
        assert r.status_code == 303

        r = client.post("/subscriptions/pay-all", follow_redirects=False)
        assert r.status_code == 303

        r = client.get("/")
        assert r.status_code == 200