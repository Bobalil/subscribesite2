import time
import httpx
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

# Кэш курса: { "USD": {"rate": 92.5, "ts": 1234567890} }
_cache: dict[str, dict] = {}
CACHE_TTL = 3600  # 1 час

CBR_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


async def get_rate_usd_rub() -> float:
    """Курс USD->RUB по ЦБ РФ с кэшем на час. Fallback — фиксированный, если API недоступен."""
    now = time.time()
    cached = _cache.get("USD")
    if cached and now - cached["ts"] < CACHE_TTL:
        return cached["rate"]

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(CBR_URL)
            r.raise_for_status()
            data = r.json()
            rate = float(data["Valute"]["USD"]["Value"])
            _cache["USD"] = {"rate": rate, "ts": now}
            return rate
    except Exception:
        # Fallback: последний известный или фикс
        return cached["rate"] if cached else 90.0


def convert(amount: float, from_cur: str, to_cur: str, usd_rub: float) -> float:
    if from_cur == to_cur:
        return amount
    if from_cur == "RUB" and to_cur == "USD":
        return amount / usd_rub
    if from_cur == "USD" and to_cur == "RUB":
        return amount * usd_rub
    raise ValueError(f"Unsupported pair {from_cur}->{to_cur}")


router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/rate")
async def rate():
    usd_rub = await get_rate_usd_rub()
    return {"USD_RUB": usd_rub, "base": "RUB", "ts": int(time.time())}


@router.get("/convert")
async def convert_endpoint(amount: float, from_cur: str = "RUB", to_cur: str = "USD"):
    usd_rub = await get_rate_usd_rub()
    return {"amount": convert(amount, from_cur, to_cur, usd_rub), "rate": usd_rub, "from": from_cur, "to": to_cur}