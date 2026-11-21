import uuid
import random
from .base import BankIssuingAdapter, IssuedCard


class MockBankAdapter(BankIssuingAdapter):
    """Mock-адаптер: работает без банка. Замените на реальный, когда появится партнёр."""

    def issue_card(self, user_id: int, holder: str) -> IssuedCard:
        last4 = f"{random.randint(0, 9999):04d}"
        return IssuedCard(
            external_id=f"mock_{uuid.uuid4().hex[:16]}",
            pan_masked=f"**** **** **** {last4}",
            exp_month=12,
            exp_year=2029,
            holder=holder.upper(),
        )

    def block_card(self, external_id: str) -> None:
        pass

    def unblock_card(self, external_id: str) -> None:
        pass

    def close_card(self, external_id: str) -> None:
        pass

    def top_up(self, external_id: str, amount_rub: float) -> None:
        pass

    def set_limits(self, external_id: str, monthly_rub: float, per_tx_rub: float) -> None:
        pass