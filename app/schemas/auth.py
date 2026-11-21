import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, model_validator

def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits[0] == "8":
        digits = "7" + digits[1:]
    if len(digits) == 10:
        digits = "7" + digits
    if len(digits) != 11 or digits[0] != "7":
        raise ValueError("Введите телефон в формате +7XXXXXXXXXX")
    return "+" + digits

class RegisterIn(BaseModel):
    email: EmailStr
    phone: str
    password: str
    password_confirm: str
    first_name: str | None = None
    last_name: str | None = None
    accept_terms: bool = False

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        return normalize_phone(v)

    @field_validator("password")
    @classmethod
    def _password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть не короче 8 символов")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать буквы и цифры")
        return v

    @model_validator(mode="after")
    def _passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")
        if not self.accept_terms:
            raise ValueError("Нужно принять пользовательское соглашение")
        return self

class RegisterOut(BaseModel):
    id: int
    email: str
    phone: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str