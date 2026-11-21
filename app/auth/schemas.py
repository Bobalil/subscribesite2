from datetime import datetime
from pydantic import BaseModel


class CardOut(BaseModel):
    id: int
    pan_masked: str
    exp_month: int
    exp_year: int
    holder: str
    status: str
    balance_rub: float
    monthly_limit_rub: float
    per_tx_limit_rub: float
    created_at: datetime

    class Config:
        from_attributes = True


class CardLimitsIn(BaseModel):
    monthly_limit_rub: float = 0
    per_tx_limit_rub: float = 0