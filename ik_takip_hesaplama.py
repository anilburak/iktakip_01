from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable
import unicodedata


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


@dataclass(frozen=True)
class HalfHoliday:
    date: date
    start: time
    end: time


@dataclass(frozen=True)
class WorkRules:
    date_format: str
    weekday_start: time
    weekday_end: time
    saturday_enabled: bool
    saturday_start: time
    saturday_end: time
    sunday_enabled: bool
    sunday_start: time
    sunday_end: time
    breaks: tuple[dict, ...]
    full_holidays: frozenset[date]
    half_holidays: tuple[HalfHoliday, ...]

    def full_holiday_on(self, day: date) -> bool:
        return day in self.full_holidays

    def half_holidays_on(self, day: date) -> tuple[HalfHoliday, ...]:
        return tuple(item for item in self.half_holidays if item.date == day)


def date_format_to_strptime(display_format: str) -> str:
    return (
        display_format
        .replace("yyyy", "%Y")
        .replace("YYYY", "%Y")
        .replace("dd", "%d")
        .replace("DD", "%d")
        .replace("MM", "%m")
    )


def parse_date(value: str, display_format: str | None = None) -> date:
    value = value.strip()
    formats = []
    if display_format:
        formats.append(date_format_to_strptime(display_format))
    formats.append(DATE_FORMAT)
    formats.append("%d.%m.%Y")
    for item in dict.fromkeys(formats):
        try:
            return datetime.strptime(value, item).date()
        except ValueError:
            continue
    raise ValueError(f"Tarih formatı geçersiz: {value}")


def parse_time(value: str) -> time:
    return datetime.strptime(value.strip(), TIME_FORMAT).time()


def parse_datetime(day_value: str, time_value: str, display_format: str | None = None) -> datetime:
    return datetime.combine(parse_date(day_value, display_format), parse_time(time_value))


def normalize_kind(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def rules_from_config(config: dict) -> WorkRules:
    work_hours = config["work_hours"]
    holidays = config["holidays"]
    date_format = config.get("date_settings", {}).get("display_format", "dd.MM.yyyy")
    return WorkRules(
        date_format=date_format,
        weekday_start=parse_time(work_hours["weekday_start"]),
        weekday_end=parse_time(work_hours["weekday_end"]),
        saturday_enabled=bool(work_hours.get("saturday_enabled", True)),
        saturday_start=parse_time(work_hours["saturday_start"]),
        saturday_end=parse_time(work_hours["saturday_end"]),
        sunday_enabled=bool(work_hours.get("sunday_enabled", False)),
        sunday_start=parse_time(work_hours.get("sunday_start", work_hours["weekday_start"])),
        sunday_end=parse_time(work_hours.get("sunday_end", work_hours["weekday_end"])),
        breaks=tuple(config.get("breaks", [])),
        full_holidays=frozenset(parse_date(item, date_format) for item in holidays.get("full_days", [])),
        half_holidays=tuple(
            HalfHoliday(
                date=parse_date(item["date"], date_format),
                start=parse_time(item["start"]),
                end=parse_time(item["end"]),
            )
            for item in holidays.get("half_days", [])
        ),
    )


def minutes_between(start: datetime, end: datetime) -> int:
    return max(0, int((end - start).total_seconds() // 60))


def overlap_minutes(start: datetime, end: datetime, period_start: datetime, period_end: datetime) -> int:
    return minutes_between(max(start, period_start), min(end, period_end))


def day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min)
    return start, start + timedelta(days=1)


def iter_days(start: datetime, end: datetime) -> Iterable[date]:
    day = start.date()
    while day <= end.date():
        yield day
        day += timedelta(days=1)


def interval_for(day: date, start_time: time, end_time: time) -> tuple[datetime, datetime]:
    return datetime.combine(day, start_time), datetime.combine(day, end_time)


def day_type(day: date) -> str:
    if day.weekday() == 5:
        return "saturday"
    if day.weekday() == 6:
        return "sunday"
    return "weekday"


def regular_periods(day: date, rules: WorkRules) -> list[tuple[datetime, datetime]]:
    current_type = day_type(day)
    if current_type == "weekday":
        return [interval_for(day, rules.weekday_start, rules.weekday_end)]
    if current_type == "saturday" and rules.saturday_enabled:
        return [interval_for(day, rules.saturday_start, rules.saturday_end)]
    if current_type == "sunday" and rules.sunday_enabled:
        return [interval_for(day, rules.sunday_start, rules.sunday_end)]
    return []


def break_periods(day: date, rules: WorkRules) -> list[tuple[datetime, datetime]]:
    current_type = day_type(day)
    periods: list[tuple[datetime, datetime]] = []
    for item in rules.breaks:
        applies_to = item.get("applies_to", ["weekday", "saturday", "sunday"])
        if current_type in applies_to:
            periods.append(interval_for(day, parse_time(item["start"]), parse_time(item["end"])))
    return periods


def subtract_intervals(
    base: list[tuple[datetime, datetime]],
    blockers: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    remaining = base[:]
    for block_start, block_end in blockers:
        next_remaining: list[tuple[datetime, datetime]] = []
        for item_start, item_end in remaining:
            if block_end <= item_start or block_start >= item_end:
                next_remaining.append((item_start, item_end))
                continue
            if item_start < block_start:
                next_remaining.append((item_start, min(block_start, item_end)))
            if block_end < item_end:
                next_remaining.append((max(block_end, item_start), item_end))
        remaining = next_remaining
    return [(item_start, item_end) for item_start, item_end in remaining if item_start < item_end]


def holiday_intervals(day: date, rules: WorkRules) -> list[tuple[datetime, datetime]]:
    if rules.full_holiday_on(day):
        return [day_bounds(day)]
    return [interval_for(day, item.start, item.end) for item in rules.half_holidays_on(day)]


def working_periods(day: date, rules: WorkRules) -> list[tuple[datetime, datetime]]:
    blockers = holiday_intervals(day, rules) + break_periods(day, rules)
    return subtract_intervals(regular_periods(day, rules), blockers)


def non_regular_periods(day: date, rules: WorkRules) -> list[tuple[datetime, datetime]]:
    return subtract_intervals([day_bounds(day)], regular_periods(day, rules) + break_periods(day, rules))


def sum_overlaps(start: datetime, end: datetime, periods: list[tuple[datetime, datetime]]) -> int:
    return sum(overlap_minutes(start, end, period_start, period_end) for period_start, period_end in periods)


def calculate_row(row: dict[str, str], rules: WorkRules) -> dict[str, int]:
    start = parse_datetime(row["Başlangıç Tarihi"], row["Başlangıç Saati"], rules.date_format)
    end = parse_datetime(row["Bitiş Tarihi"], row["Bitiş Saati"], rules.date_format)
    if end <= start:
        raise ValueError("Bitiş zamanı başlangıçtan sonra olmalı.")

    kind = normalize_kind(row["Tür"])
    result = {
        "izin_dk": 0,
        "mesai_dk": 0,
        "rapor_dk": 0,
        "resmi_tatil_mesai_dk": 0,
        "diger_dk": 0,
        "haftaici_dk": 0,
        "cumartesi_dk": 0,
        "toplam_dk": 0,
    }

    for day in iter_days(start, end):
        day_start, day_end = day_bounds(day)
        current_start = max(start, day_start)
        current_end = min(end, day_end)
        if current_start >= current_end:
            continue

        holiday_minutes = sum_overlaps(current_start, current_end, holiday_intervals(day, rules))
        current_day_type = day_type(day)

        if kind in {"mesai", "fazla mesai"}:
            normal_overtime = sum_overlaps(
                current_start,
                current_end,
                subtract_intervals(non_regular_periods(day, rules), holiday_intervals(day, rules)),
            )
            result["resmi_tatil_mesai_dk"] += holiday_minutes
            result["mesai_dk"] += normal_overtime
            if current_day_type == "saturday":
                result["cumartesi_dk"] += normal_overtime
            elif current_day_type == "weekday":
                result["haftaici_dk"] += normal_overtime
            continue

        if kind in {"resmi tatil mesai", "resmi tatilde mesai"}:
            result["resmi_tatil_mesai_dk"] += holiday_minutes
            continue

        if kind in {"izin", "raporlu", "rapor"}:
            counted_minutes = sum_overlaps(current_start, current_end, working_periods(day, rules))
            if kind == "izin":
                result["izin_dk"] += counted_minutes
            else:
                result["rapor_dk"] += counted_minutes
            if current_day_type == "saturday":
                result["cumartesi_dk"] += counted_minutes
            elif current_day_type == "weekday":
                result["haftaici_dk"] += counted_minutes
            continue

        counted_minutes = sum_overlaps(current_start, current_end, working_periods(day, rules))
        result["diger_dk"] += counted_minutes
        if current_day_type == "saturday":
            result["cumartesi_dk"] += counted_minutes
        elif current_day_type == "weekday":
            result["haftaici_dk"] += counted_minutes

    result["toplam_dk"] = result["izin_dk"] + result["mesai_dk"] + result["rapor_dk"] + result["resmi_tatil_mesai_dk"] + result["diger_dk"]
    return result


def calculate_totals(rows: list[dict[str, str]], rules: WorkRules) -> dict[str, int]:
    totals = {
        "izin_dk": 0,
        "mesai_dk": 0,
        "rapor_dk": 0,
        "resmi_tatil_mesai_dk": 0,
    }
    for row in rows:
        calculated = calculate_row(row, rules)
        for key in totals:
            totals[key] += calculated[key]
    return totals


def format_hours(minutes: int) -> str:
    hours = minutes // 60
    rest = minutes % 60
    return f"{hours}:{rest:02d}"
