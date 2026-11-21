import uuid

import httpx

from ..config import settings
from .base import PaymentIntent, PaymentProvider


class YooKassaProvider(PaymentProvider):
    """Реальная интеграция ЮKassa (СБП/карта). Включается через PAYMENT_PROVIDER=yookassa."""

    API = "https://api.yookassa.ru/v3/payments"

    def create_payment(self, amount: int, description: str, return_url: str,
                       idempotency_key: str) -> PaymentIntent:
        if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
            raise RuntimeError("YOOKASSA credentials are not configured")
        payload = {
            "amount": {"value": f"{amount / 100:.2f}", "currency": "RUB"},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": description[:128],
            "metadata": {"idempotency_key": idempotency_key},
        }
        headers = {"Idempotence-Key": idempotency_key or uuid.uuid4().hex}
        r = httpx.post(self.API, json=payload, headers=headers,
                       auth=(settings.yookassa_shop_id, settings.yookassa_secret_key), timeout=20)
        r.raise_for_status()
        data = r.json()
        return PaymentIntent(
            provider_payment_id=data["id"],
            confirmation_url=data["confirmation"]["confirmation_url"],
            status=data["status"],
        )