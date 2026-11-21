from dataclasses import dataclass


@dataclass
class PaymentIntent:
    provider_payment_id: str
    confirmation_url: str
    status: str


class PaymentProvider:
    def create_payment(self, amount: int, description: str, return_url: str,
                       idempotency_key: str) -> PaymentIntent:
        raise NotImplementedError