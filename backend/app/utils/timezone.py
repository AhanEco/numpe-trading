"""Timezone and market hours utilities for Indian Standard Time (IST)."""

from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo
from typing import Tuple

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

# Standard NSE Market Timings
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Major Indian Market Holidays (standard fixed/observed dates)
INDIAN_MARKET_HOLIDAYS_2024_2026 = {
    datetime.date(2024, 1, 26),  # Republic Day
    datetime.date(2024, 3, 8),   # Mahashivratri
    datetime.date(2024, 3, 25),  # Holi
    datetime.date(2024, 3, 29),  # Good Friday
    datetime.date(2024, 4, 11),  # Id-Ul-Fitr
    datetime.date(2024, 4, 17),  # Ram Navami
    datetime.date(2024, 5, 1),   # Maharashtra Day
    datetime.date(2024, 6, 17),  # Bakri Id
    datetime.date(2024, 7, 17),  # Moharram
    datetime.date(2024, 8, 15),  # Independence Day
    datetime.date(2024, 10, 2),  # Mahatma Gandhi Jayanti
    datetime.date(2024, 11, 1),  # Diwali Laxmi Pujan
    datetime.date(2024, 11, 15), # Gurunanak Jayanti
    datetime.date(2024, 12, 25), # Christmas
    datetime.date(2025, 1, 26),
    datetime.date(2025, 3, 14),
    datetime.date(2025, 3, 31),
    datetime.date(2025, 4, 18),
    datetime.date(2025, 5, 1),
    datetime.date(2025, 8, 15),
    datetime.date(2025, 10, 2),
    datetime.date(2025, 10, 21),
    datetime.date(2025, 11, 5),
    datetime.date(2025, 12, 25),
    datetime.date(2026, 1, 26),
    datetime.date(2026, 3, 6),
    datetime.date(2026, 4, 3),
    datetime.date(2026, 5, 1),
    datetime.date(2026, 8, 15),
    datetime.date(2026, 10, 2),
    datetime.date(2026, 11, 10),
    datetime.date(2026, 12, 25),
}


def now_ist() -> datetime.datetime:
    """Return the current datetime in Indian Standard Time (IST)."""
    return datetime.datetime.now(IST)


def today_ist() -> datetime.date:
    """Return today's date in Indian Standard Time (IST)."""
    return now_ist().date()


def to_ist(dt: datetime.datetime) -> datetime.datetime:
    """Convert any aware or naive datetime to IST."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC).astimezone(IST)
    return dt.astimezone(IST)


def is_market_open() -> Tuple[bool, str]:
    """
    Check if the Indian stock market (NSE/BSE) is currently in open trading hours.
    Market hours: Mon-Fri 09:15 to 15:30 IST, excluding declared holidays.
    """
    current_time = now_ist()
    current_date = current_time.date()

    # Weekend check
    if current_time.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False, "Market is Closed (Weekend)"

    # Holiday check
    if current_date in INDIAN_MARKET_HOLIDAYS_2024_2026:
        return False, "Market is Closed (Trading Holiday)"

    # Time check
    open_time = current_time.replace(
        hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0
    )
    close_time = current_time.replace(
        hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0
    )

    if current_time < open_time:
        return False, "Pre-Market / Market Opens at 09:15 IST"
    elif current_time > close_time:
        return False, "Market Closed (Closes at 15:30 IST)"
    else:
        return True, "Market Open (Trading Active)"


def format_ist_timestamp(dt: datetime.datetime | None) -> str:
    """Format datetime as human-readable IST string."""
    if dt is None:
        return "N/A"
    ist_dt = to_ist(dt)
    return ist_dt.strftime("%d %b %Y, %I:%M:%S %p IST")

