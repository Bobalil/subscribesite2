# Subscriptions Wallet (MVP)

Кошелёк + каталог подписок + «оплатить всё одной транзакцией» + админка.
Стек: FastAPI, SQLAlchemy, SQLite, Jinja2. Платёжный провайдер — заглушка или ЮKassa.

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py