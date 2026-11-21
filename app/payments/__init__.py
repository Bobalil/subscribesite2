from ..config import settings
from .stub import StubProvider
from .yookassa import YooKassaProvider


def get_provider():
    if settings.payment_provider == "yookassa":
        return YooKassaProvider()
    return StubProvider()