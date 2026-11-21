import uuid

from .base import PaymentIntent, PaymentProvider


class StubProvider(PaymentProvider):
    """Демо-провайдер: сразу возвращает succeeded и ссылку на локальный checkout."""

    def create_payment(self, amount: int, description: str, return_url: str,
                       idempotency_key: str) -> PaymentIntent:
        pid = f"stub_{uuid.uuid4().hex[:12]}"
        return PaymentIntent(
            provider_payment_id=pid,
            confirmation_url=f"/checkout/{pid}",
            status="pending",
        )