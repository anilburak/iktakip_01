from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


CONFIG_PATH = app_dir() / "config.json"


DEFAULT_CONFIG: dict[str, Any] = {
    "program": {
        "name": "Personel Sistemi",
        "window_width": 1220,
        "window_height": 740,
    },
    "logo": {
        "text": "HS",
        "font": "Segoe UI Semibold",
        "h_color": "#001F5B",
        "s_color": "#000000",
    },
    "theme": {
        "name": "Toz Pembe",
        "primary_color": "#E8B4B8",
        "secondary_color": "#F6D6D8",
        "background_color": "#FFF1F2",
        "text_color": "#2B2B2B",
        "button_color": "#E8B4B8",
        "button_text_color": "#000000",
        "input_background_color": "#FFF1F2",
        "table_background_color": "#FFF1F2",
        "card_background_color": "#FFFDFD",
        "chart_background_color": "#FFFFFF",
        "accent_color": "#001F5B",
        "zebra_color": "#FBE3E5",
    },
    "work_hours": {
        "weekday_start": "09:00",
        "weekday_end": "18:00",
        "saturday_start": "09:00",
        "saturday_end": "14:30",
        "saturday_enabled": True,
        "sunday_enabled": False,
        "sunday_start": "09:00",
        "sunday_end": "18:00",
    },
    "date_settings": {
        "display_format": "dd.MM.yyyy",
        "default_today_on_start": True,
        "use_calendar_picker": True,
    },
    "performance": {
        "page_size": 1000,
        "csv_progress_interval": 50000,
    },
    "breaks": [
        {
            "name": "Hafta İçi Öğle Molası",
            "start": "12:00",
            "end": "13:00",
            "applies_to": ["weekday"],
        },
        {
            "name": "Cumartesi Öğle Molası",
            "start": "12:00",
            "end": "12:30",
            "applies_to": ["saturday"],
        }
    ],
    "holidays": {
        "full_days": [
            "01.01.2026",
            "23.04.2026",
            "01.05.2026",
            "19.05.2026",
            "15.07.2026",
            "30.08.2026",
            "29.10.2026",
        ],
        "half_days": [
            {
                "date": "28.10.2026",
                "start": "13:00",
                "end": "18:00",
            }
        ],
    },
    "tabs": ["Personel Kayıtları", "Personel KPI", "Personel Ayarları", "Genel Ayarlar"],
    "kpi_settings": {
        "monthly_required_work_hours": 270,
    },
    "labels": {
        "new_record": "Yeni kayıt",
        "add": "Ekle",
        "delete_selected": "Seçileni Sil",
        "open_csv": "CSV Aç",
        "save_csv": "CSV Kaydet",
        "example_row": "Örnek Satır",
        "clear_filters": "Filtreleri Temizle",
        "totals": "Toplamlar",
        "holiday_add": "Tatil ekle",
        "holiday_kind": "Tür",
        "holiday_date": "Tarih",
        "holiday_start": "Başlangıç",
        "holiday_end": "Bitiş",
        "holiday_add_button": "Tatil Ekle",
    },
    "search_fields": [
        "İsim",
        "Departman",
        "Tür",
        "Başlangıç Tarihi",
        "Bitiş Tarihi",
        "Açıklama",
    ],
    "select_options": {
        "İsim": [],
        "Departman": ["Üretim", "Lojistik", "Kalite", "Bakım"],
        "Tür": ["İzin", "Fazla Mesai", "Rapor", "Resmi Tatil Mesai"],
        "Açıklama": [
            "Normal mesai",
            "Fazla mesai",
            "Yıllık izin",
            "Raporlu",
            "Resmi tatil çalışması",
        ],
        "Tatil Türü": ["Tam Gün", "Yarım Gün"],
    },
    "defaults": {
        "İsim": "",
        "Departman": "Üretim",
        "Tür": "İzin",
        "Açıklama": "Normal mesai",
        "example_name": "",
        "example_department": "Üretim",
        "example_type": "İzin",
        "example_description": "Normal mesai",
    },
    "columns": [
        "İsim",
        "Departman",
        "Tür",
        "Başlangıç Tarihi",
        "Başlangıç Saati",
        "Bitiş Tarihi",
        "Bitiş Saati",
        "Haftaiçi Saat",
        "Cumartesi Saat",
        "Resmi Tatil Saat",
        "Toplam Saat",
        "Açıklama",
    ],
    "input_columns": [
        "İsim",
        "Departman",
        "Tür",
        "Başlangıç Tarihi",
        "Başlangıç Saati",
        "Bitiş Tarihi",
        "Bitiş Saati",
        "Açıklama",
    ],
    "summary_fields": {
        "izin": "Toplam İzin",
        "mesai": "Toplam Mesai",
        "rapor": "Toplam Rapor",
        "resmi": "Resmi Tatil Mesaisi",
    },
}


class ConfigError(Exception):
    pass


def deep_merge(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return deepcopy(DEFAULT_CONFIG)

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            user_config = json.load(file)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config.json okunamadı. JSON hatası: satır {exc.lineno}, kolon {exc.colno}.") from exc
    except OSError as exc:
        raise ConfigError(f"config.json açılamadı: {exc}") from exc

    if not isinstance(user_config, dict):
        raise ConfigError("config.json ana yapısı bir JSON nesnesi olmalı.")

    config = deep_merge(DEFAULT_CONFIG, user_config)
    validate_config(config)
    return config


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def validate_config(config: dict[str, Any]) -> None:
    required_sections = ["program", "logo", "theme", "work_hours", "date_settings", "performance", "breaks", "holidays", "tabs", "search_fields", "select_options", "columns", "input_columns", "kpi_settings"]
    missing = [section for section in required_sections if section not in config]
    if missing:
        raise ConfigError("config.json eksik bölüm içeriyor: " + ", ".join(missing))

    if not isinstance(config["columns"], list) or not config["columns"]:
        raise ConfigError("config.json içindeki columns dolu bir liste olmalı.")
    if not isinstance(config["input_columns"], list) or not config["input_columns"]:
        raise ConfigError("config.json içindeki input_columns dolu bir liste olmalı.")
    if "Tür" not in config["select_options"] or not config["select_options"]["Tür"]:
        raise ConfigError("config.json içinde select_options.Tür en az bir değer içermeli.")
