from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IssuedCard:
    external_id: str
    pan_masked: str
    exp_month: int
    exp_year: int
    holder: str


class BankIssuingAdapter(ABC):
    """Интерфейс адаптера банка-эмитента. Реализации: MockBankAdapter, TinkoffAdapter, ..."""

    @abstractmethod
    def issue_card(self, user_id: int, holder: str) -> IssuedCard: ...

    @abstractmethod
    def block_card(self, external_id: str) -> None: ...

    @abstractmethod
    def unblock_card(self, external_id: str) -> None: ...

    @abstractmethod
    def close_card(self, external_id: str) -> None: ...

    @abstractmethod
    def top_up(self, external_id: str, amount_rub: float) -> None: ...

    @abstractmethod
    def set_limits(self, external_id: str, monthly_rub: float, per_tx_rub: float) -> None: ...