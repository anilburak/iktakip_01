from copy import deepcopy

from ayarlar import DEFAULT_CONFIG
from ik_takip_hesaplama import calculate_row, rules_from_config


def make_rules():
    config = deepcopy(DEFAULT_CONFIG)
    config["holidays"] = {
        "full_days": ["2026-10-29"],
        "half_days": [{"date": "2026-10-28", "start": "13:00", "end": "18:00"}],
    }
    return rules_from_config(config)


RULES = make_rules()


def row(kind, start_date, start_time, end_date, end_time):
    return {
        "İsim": "Test",
        "Departman": "Test",
        "Tür": kind,
        "Başlangıç Tarihi": start_date,
        "Başlangıç Saati": start_time,
        "Bitiş Tarihi": end_date,
        "Bitiş Saati": end_time,
        "Açıklama": "",
    }


def test_weekday_overtime_after_work():
    result = calculate_row(row("Mesai", "2026-06-18", "17:00", "2026-06-18", "20:00"), RULES)
    assert result["mesai_dk"] == 120
    assert result["resmi_tatil_mesai_dk"] == 0


def test_weekday_lunch_is_ignored():
    result = calculate_row(row("Mesai", "2026-06-18", "12:00", "2026-06-18", "13:00"), RULES)
    assert result["mesai_dk"] == 0
    assert result["resmi_tatil_mesai_dk"] == 0


def test_saturday_overtime_only_after_configured_end():
    result = calculate_row(row("Mesai", "2026-06-20", "09:00", "2026-06-20", "16:00"), RULES)
    assert result["mesai_dk"] == 120


def test_full_holiday_work_is_official_overtime():
    result = calculate_row(row("Mesai", "2026-10-29", "09:00", "2026-10-29", "18:00"), RULES)
    assert result["mesai_dk"] == 0
    assert result["resmi_tatil_mesai_dk"] == 540


def test_half_holiday_auto_split():
    result = calculate_row(row("Mesai", "2026-10-28", "11:00", "2026-10-28", "16:00"), RULES)
    assert result["mesai_dk"] == 0
    assert result["resmi_tatil_mesai_dk"] == 180


def test_leave_counts_only_working_hours_inside_wide_range():
    result = calculate_row(row("İzin", "2026-06-18", "08:00", "2026-06-18", "20:00"), RULES)
    assert result["izin_dk"] == 480


def test_leave_excludes_half_holiday_window():
    result = calculate_row(row("İzin", "2026-10-28", "09:00", "2026-10-28", "18:00"), RULES)
    assert result["izin_dk"] == 180
