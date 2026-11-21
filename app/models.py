import enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

# --- 1. ПЕРЕЧИСЛЕНИЯ ---
class ExecutionMode(str, enum.Enum):
    AGENT = "agent"
    LINK = "link"
    MANUAL = "manual"

class CardStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    CLOSED = "closed"

class TxType(str, enum.Enum):
    TOPUP = "topup"
    SUBSCRIPTION_PAYMENT = "subscription_payment"
    REFUND = "refund"
    PAYOUT = "payout"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

# --- 2. МОДЕЛИ ---
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    card = relationship("Card", back_populates="user", uselist=False)
    subscriptions = relationship("UserSubscription", back_populates="user")
    wallet = relationship("Wallet", back_populates="user", uselist=False)

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), default="🔹")
    price: Mapped[int] = mapped_column(Integer, default=0) # В копейках!
    execution_mode: Mapped[ExecutionMode] = mapped_column(Enum(ExecutionMode), default=ExecutionMode.MANUAL)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    next_charge_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="subscriptions")
    service = relationship("Service")

class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, unique=True)
    pan_masked: Mapped[str] = mapped_column(String(19))
    exp_month: Mapped[int] = mapped_column(Integer)
    exp_year: Mapped[int] = mapped_column(Integer)
    holder: Mapped[str] = mapped_column(String(64))
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="card")

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, unique=True)
    balance: Mapped[int] = mapped_column(Integer, default=0) # В копейках!
    
    user = relationship("User", back_populates="wallet")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    entry_type: Mapped[TxType] = mapped_column(Enum(TxType))
    amount: Mapped[int] = mapped_column(Integer) # В копейках (может быть отрицательным)!
    description: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)