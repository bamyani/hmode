from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, time as time_type, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_CLOCK_RE = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?\s*([ap]m)?\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class PrimerPlan:
    timezone_label: str
    wake_at: datetime
    primer_at: datetime
    resets: list[datetime]
    primer_offset_hours: float
    window_hours: float


def parse_clock(value: str) -> time_type:
    match = _CLOCK_RE.match(value)
    if match is None:
        raise ValueError(f"Invalid time format: {value}")

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    suffix = (match.group(3) or "").lower()

    if minute < 0 or minute > 59:
        raise ValueError(f"Invalid minute value: {value}")

    if suffix:
        if hour < 1 or hour > 12:
            raise ValueError(f"Invalid 12-hour time: {value}")
        if hour == 12:
            hour = 0
        if suffix == "pm":
            hour += 12
    elif hour > 23:
        raise ValueError(f"Invalid 24-hour time: {value}")

    return time_type(hour=hour, minute=minute)


def resolve_timezone(name: str | None) -> tuple[tzinfo, str]:
    if name:
        try:
            return ZoneInfo(name), name
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {name}") from exc

    local_now = datetime.now().astimezone()
    tz = local_now.tzinfo or timezone.utc
    label = local_now.tzname() or "local time"
    return tz, label


def format_dt(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M %Z").strip()


def build_primer_plan(
    wake: str,
    timezone_name: str | None = None,
    primer_offset_hours: float = 2.5,
    window_hours: float = 5.0,
    resets: int = 3,
    now: datetime | None = None,
) -> PrimerPlan:
    if primer_offset_hours <= 0:
        raise ValueError("Primer offset must be greater than zero")
    if window_hours <= 0:
        raise ValueError("Window hours must be greater than zero")
    if resets <= 0:
        raise ValueError("Reset count must be greater than zero")

    tz, label = resolve_timezone(timezone_name)
    current = now or datetime.now(tz)
    if current.tzinfo is None:
        current = current.replace(tzinfo=tz)
    else:
        current = current.astimezone(tz)

    wake_clock = parse_clock(wake)
    wake_at = datetime.combine(current.date(), wake_clock, tzinfo=tz)
    if wake_at <= current:
        wake_at += timedelta(days=1)

    primer_at = wake_at - timedelta(hours=primer_offset_hours)
    reset_times = [primer_at + timedelta(hours=window_hours * index) for index in range(1, resets + 1)]

    return PrimerPlan(
        timezone_label=label,
        wake_at=wake_at,
        primer_at=primer_at,
        resets=reset_times,
        primer_offset_hours=primer_offset_hours,
        window_hours=window_hours,
    )


def format_primer_plan(plan: PrimerPlan) -> str:
    lines = [
        f"Primer plan for {plan.timezone_label}",
        f"Wake time: {format_dt(plan.wake_at)}",
        f"Primer time: {format_dt(plan.primer_at)}",
        f"Rolling window: {plan.window_hours:g} hours",
        "Resets:",
    ]
    for index, reset_at in enumerate(plan.resets, start=1):
        lines.append(f"- Reset {index}: {format_dt(reset_at)}")
    return "\n".join(lines)
