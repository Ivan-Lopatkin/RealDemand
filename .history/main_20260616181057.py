from __future__ import annotations

from dataclasses import dataclass
from html import escape

import pydeck as pdk
import streamlit as st


@dataclass(frozen=True)
class RegionSignal:
    demand: int
    competition: int
    confidence: int
    district: str
    demand_growth: int
    social_growth: int
    note: str


@dataclass(frozen=True)
class SectorSignal:
    base: int
    label: str
    weak_spot: str


REGIONS: dict[str, RegionSignal] = {
    "Казань": RegionSignal(
        demand=78,
        competition=56,
        confidence=84,
        district="Ново-Савиновский",
        demand_growth=24,
        social_growth=31,
        note="Начать с Ново-Савиновского, Советский добавить вторым, центр оставить на второй этап.",
    ),
    "Екатеринбург": RegionSignal(
        demand=72,
        competition=64,
        confidence=79,
        district="Академический",
        demand_growth=19,
        social_growth=26,
        note="Спрос устойчивый, но нужен аккуратный выбор ниши и позиционирования.",
    ),
    "Новосибирск": RegionSignal(
        demand=69,
        competition=48,
        confidence=76,
        district="Заельцовский",
        demand_growth=17,
        social_growth=22,
        note="Есть пространство для теста в районах с растущей жилой застройкой.",
    ),
    "Нижний Новгород": RegionSignal(
        demand=65,
        competition=52,
        confidence=73,
        district="Советский",
        demand_growth=14,
        social_growth=18,
        note="Рынок подходит для осторожного запуска с контролем стоимости заявки.",
    ),
}

SECTORS: dict[str, SectorSignal] = {
    "Домашние сервисы": SectorSignal(
        base=8,
        label="B2C / регулярный спрос",
        weak_spot="Скорость отклика и работа вечером",
    ),
    "Кофейня у дома": SectorSignal(
        base=2,
        label="HoReCa / локальная точка",
        weak_spot="Высокая арендная нагрузка в центре",
    ),
    "Фитнес-студия": SectorSignal(
        base=4,
        label="Wellness / подписка",
        weak_spot="Сезонность и цена привлечения",
    ),
    "Детские кружки": SectorSignal(
        base=6,
        label="EdTech offline / семейный спрос",
        weak_spot="Доверие родителей и расписание",
    ),
}

COMPETITOR_EXAMPLES: dict[str, list[tuple[str, str, str]]] = {
    "Домашние сервисы": [
        ("Клининг 116", "много отзывов", "сильная выдача в центре"),
        ("Чистый дом", "быстрый отклик", "слабее вечерние слоты"),
        ("Мастер чистоты", "низкий чек", "меньше доверия в отзывах"),
    ],
    "Кофейня у дома": [
        ("Coffee Point", "пешеходный трафик", "высокая аренда"),
        ("Булочная рядом", "утренний спрос", "узкий ассортимент"),
        ("Local Beans", "лояльная аудитория", "мало точек"),
    ],
    "Фитнес-студия": [
        ("FitRoom", "сильная подписка", "высокий CAC"),
        ("Stretch Lab", "нишевый спрос", "ограниченная емкость"),
        ("Форма", "районная узнаваемость", "сезонность"),
    ],
    "Детские кружки": [
        ("Умный ребенок", "доверие родителей", "плотное расписание"),
        ("Арт-класс", "сильные отзывы", "узкая программа"),
        ("Лего-школа", "понятный формат", "высокий чек"),
    ],
}

REGION_MAP_POINTS: dict[str, list[dict[str, object]]] = {
    "Казань": [
        {
            "district": "Ново-Савиновский",
            "lat": 55.8307,
            "lon": 49.1338,
            "demand": 86,
            "competition": 58,
            "status": "старт пилота",
            "radius": 850,
            "color": [18, 185, 129, 210],
        },
        {
            "district": "Советский",
            "lat": 55.7942,
            "lon": 49.2045,
            "demand": 74,
            "competition": 52,
            "status": "второй район",
            "radius": 740,
            "color": [37, 99, 235, 205],
        },
        {
            "district": "Вахитовский центр",
            "lat": 55.7908,
            "lon": 49.1233,
            "demand": 82,
            "competition": 78,
            "status": "дорогой вход",
            "radius": 690,
            "color": [255, 107, 74, 220],
        },
        {
            "district": "Приволжский",
            "lat": 55.7357,
            "lon": 49.1888,
            "demand": 66,
            "competition": 49,
            "status": "зона роста",
            "radius": 620,
            "color": [250, 204, 21, 220],
        },
    ],
    "Екатеринбург": [
        {
            "district": "Академический",
            "lat": 56.7887,
            "lon": 60.5201,
            "demand": 81,
            "competition": 56,
            "status": "старт пилота",
            "radius": 820,
            "color": [18, 185, 129, 210],
        },
        {
            "district": "ВИЗ",
            "lat": 56.8443,
            "lon": 60.5539,
            "demand": 71,
            "competition": 62,
            "status": "зона роста",
            "radius": 700,
            "color": [37, 99, 235, 205],
        },
        {
            "district": "Центр",
            "lat": 56.8389,
            "lon": 60.6057,
            "demand": 78,
            "competition": 77,
            "status": "дорогой вход",
            "radius": 670,
            "color": [255, 107, 74, 220],
        },
        {
            "district": "Уралмаш",
            "lat": 56.8956,
            "lon": 60.5962,
            "demand": 65,
            "competition": 57,
            "status": "второй этап",
            "radius": 620,
            "color": [250, 204, 21, 220],
        },
    ],
    "Новосибирск": [
        {
            "district": "Заельцовский",
            "lat": 55.0647,
            "lon": 82.9061,
            "demand": 78,
            "competition": 49,
            "status": "старт пилота",
            "radius": 800,
            "color": [18, 185, 129, 210],
        },
        {
            "district": "Калининский",
            "lat": 55.0833,
            "lon": 82.9687,
            "demand": 70,
            "competition": 47,
            "status": "второй район",
            "radius": 710,
            "color": [37, 99, 235, 205],
        },
        {
            "district": "Центр",
            "lat": 55.0302,
            "lon": 82.9204,
            "demand": 73,
            "competition": 70,
            "status": "дорогой вход",
            "radius": 640,
            "color": [255, 107, 74, 220],
        },
        {
            "district": "Октябрьский",
            "lat": 55.0187,
            "lon": 82.9582,
            "demand": 67,
            "competition": 51,
            "status": "зона роста",
            "radius": 610,
            "color": [250, 204, 21, 220],
        },
    ],
    "Нижний Новгород": [
        {
            "district": "Советский",
            "lat": 56.2969,
            "lon": 44.0305,
            "demand": 74,
            "competition": 51,
            "status": "старт пилота",
            "radius": 760,
            "color": [18, 185, 129, 210],
        },
        {
            "district": "Нижегородский",
            "lat": 56.3267,
            "lon": 44.0059,
            "demand": 71,
            "competition": 72,
            "status": "дорогой вход",
            "radius": 670,
            "color": [255, 107, 74, 220],
        },
        {
            "district": "Канавинский",
            "lat": 56.3207,
            "lon": 43.9441,
            "demand": 64,
            "competition": 54,
            "status": "зона роста",
            "radius": 620,
            "color": [37, 99, 235, 205],
        },
        {
            "district": "Автозаводский",
            "lat": 56.2478,
            "lon": 43.8689,
            "demand": 68,
            "competition": 48,
            "status": "второй район",
            "radius": 680,
            "color": [250, 204, 21, 220],
        },
    ],
}

CITY_MAP_ZOOM: dict[str, float] = {
    "Казань": 10.45,
    "Екатеринбург": 10.35,
    "Новосибирск": 10.25,
    "Нижний Новгород": 10.15,
}


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, round(value)))


def recommendation(score: int) -> tuple[str, str]:
    if score >= 78:
        return "Запускать пилот", "Спрос и конкурентная плотность дают пространство для управляемого теста."
    if score >= 62:
        return "Тестировать осторожно", "Сценарий выглядит рабочим, но лучше ограничить бюджет и район запуска."
    return "Уточнить сценарий", "Сигналы подсказывают сменить район, сегмент или формат предложения."


def render_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --rd-bg: #f5f7fb;
            --rd-ink: #101828;
            --rd-muted: #667085;
            --rd-soft: #eef2f7;
            --rd-line: #d9e0ea;
            --rd-card: #ffffff;
            --rd-blue: #2563eb;
            --rd-blue-soft: #dbeafe;
            --rd-green: #12b981;
            --rd-green-soft: #d1fae5;
            --rd-amber: #facc15;
            --rd-amber-soft: #fef3c7;
            --rd-coral: #ff6b4a;
            --rd-coral-soft: #ffe4dc;
            --rd-radius: 8px;
            --rd-shadow: 0 18px 44px rgba(16, 24, 40, 0.10);
            --rd-font: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, Helvetica, sans-serif;
            --rd-section-title: clamp(32px, 3vw, 44px);
            --rd-section-title-weight: 820;
            --rd-subtitle: 22px;
            --rd-card-title: 18px;
        }

        html {
            scroll-behavior: smooth;
        }

        .stApp {
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.90), rgba(245, 247, 251, 0.94) 18rem),
                var(--rd-bg);
            color: var(--rd-ink);
            font-family: var(--rd-font);
        }

        .stApp * {
            font-family: var(--rd-font);
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
        }

        .block-container {
            max-width: 1180px;
            padding: 0 20px 52px;
        }

        .rd-nowrap {
            white-space: nowrap;
        }

        .stMarkdown {
            margin: 0;
        }

        .stMarkdown a.anchor-link {
            display: none !important;
        }

        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }

        .rd-nav {
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            min-height: 58px;
            margin: 0 -20px 16px;
            padding: 8px 20px;
            border-bottom: 1px solid rgba(16, 24, 40, 0.10);
            background: rgba(245, 247, 251, 0.94);
            backdrop-filter: blur(16px);
        }

        .rd-brand {
            display: inline-flex;
            align-items: center;
            gap: 9px;
            color: var(--rd-ink) !important;
            text-decoration: none !important;
            font-size: 19px;
            font-weight: 900;
            letter-spacing: 0;
        }

        .rd-mark {
            width: 28px;
            height: 28px;
            display: inline-grid;
            place-items: center;
            border-radius: var(--rd-radius);
            background: conic-gradient(from 210deg, var(--rd-blue), var(--rd-green), var(--rd-amber), var(--rd-coral), var(--rd-blue));
            box-shadow: 0 10px 28px rgba(37, 99, 235, 0.22);
        }

        .rd-mark::after {
            content: "";
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #fff;
        }

        .rd-nav-links {
            display: flex;
            align-items: center;
            gap: 14px;
            color: var(--rd-muted);
            font-size: 13px;
            font-weight: 750;
        }

        .rd-nav-links a {
            color: inherit !important;
            text-decoration: none !important;
        }

        .rd-nav-links a:hover {
            color: var(--rd-ink) !important;
        }

        .rd-btn,
        .rd-btn:visited {
            min-height: 38px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 0 14px;
            border: 1px solid transparent;
            border-radius: var(--rd-radius);
            background: var(--rd-ink);
            color: #fff !important;
            font-size: 13px;
            font-weight: 850;
            text-decoration: none !important;
            box-shadow: 0 10px 24px rgba(16, 24, 40, 0.16);
            transition: transform .16s ease, box-shadow .16s ease;
            white-space: nowrap;
        }

        .rd-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 30px rgba(16, 24, 40, 0.20);
        }

        .rd-btn.secondary {
            background: #fff;
            color: var(--rd-ink) !important;
            border-color: var(--rd-line);
            box-shadow: none;
        }

        .rd-section {
            padding: 38px 0;
            border-top: 1px solid rgba(16, 24, 40, 0.08);
        }

        .rd-section:first-of-type {
            border-top: 0;
        }

        .rd-hero {
            display: grid;
            grid-template-columns: minmax(0, .96fr) minmax(420px, 1.04fr);
            gap: 28px;
            align-items: start;
            min-height: auto;
            padding: 42px 0 46px;
            overflow: visible;
        }

        .rd-hero > div:first-child {
            min-width: 0;
            max-width: 820px;
            padding: 0;
        }

        .rd-hero > div:nth-child(2) {
            min-width: 0;
        }

        .rd-hero .rd-dashboard {
            grid-template-columns: 172px minmax(0, 1fr);
            min-height: 468px;
        }

        .rd-hero .rd-sidebar {
            padding: 16px 12px;
        }

        .rd-hero .rd-side-item {
            min-height: 32px;
            padding: 0 8px;
            font-size: 12px;
        }

        .rd-hero .rd-dashboard-title {
            align-items: flex-start;
            flex-direction: column;
            gap: 12px;
        }

        .rd-hero .rd-health {
            width: 100%;
            min-width: 0;
        }

        .rd-hero .rd-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .rd-hero .rd-overview-panel .rd-overview-line:nth-child(4) {
            display: none;
        }

        .rd-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            min-height: 30px;
            margin-bottom: 18px;
            padding: 0 10px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            color: var(--rd-muted);
            font-size: 12px;
            font-weight: 850;
        }

        .rd-eyebrow::before {
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--rd-green);
        }

        .rd-section .rd-eyebrow,
        .rd-faq-grid .rd-eyebrow {
            min-height: 38px;
            margin-bottom: 18px;
            padding: 0 14px;
            font-size: 15px;
            letter-spacing: 0.02em;
        }

        .rd-section .rd-eyebrow::before,
        .rd-faq-grid .rd-eyebrow::before {
            width: 10px;
            height: 10px;
        }

        .rd-title-xl {
            max-width: 760px;
            margin: 0 0 18px;
            color: var(--rd-ink);
            font-size: clamp(46px, 5.2vw, 72px);
            line-height: 1;
            font-weight: 860;
            font-variation-settings: "wght" 860;
            letter-spacing: 0;
        }

        .rd-lead {
            max-width: 560px;
            margin: 0 0 18px;
            color: #344054;
            font-size: 21px;
            line-height: 1.42;
        }

        .rd-note {
            max-width: 620px;
            margin: 0 0 26px;
            color: var(--rd-muted);
            font-size: 16px;
            line-height: 1.58;
        }

        .rd-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 0 0 24px;
        }

        .rd-proof-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }

        .rd-proof {
            min-height: 104px;
            padding: 13px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: rgba(255, 255, 255, 0.74);
        }

        .rd-proof strong {
            display: block;
            margin-bottom: 7px;
            color: var(--rd-ink);
            font-size: 18px;
            line-height: 1.1;
            font-weight: 900;
        }

        .rd-proof span {
            color: var(--rd-muted);
            font-size: 13px;
            line-height: 1.35;
        }

        .rd-overview-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 0 0 20px;
        }

        .rd-overview-strip span {
            display: inline-flex;
            align-items: center;
            min-height: 30px;
            padding: 0 10px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: rgba(255, 255, 255, 0.78);
            color: #344054;
            font-size: 12px;
            font-weight: 820;
        }

        .rd-overview-panel {
            display: grid;
            gap: 9px;
            margin-top: 18px;
        }

        .rd-overview-line {
            display: grid;
            grid-template-columns: 112px minmax(0, 1fr);
            gap: 12px;
            min-height: 42px;
            align-items: center;
            padding: 9px 11px;
            border: 1px solid #d8e0eb;
            border-radius: var(--rd-radius);
            background: #fff;
            color: #344054;
            font-size: 13px;
            line-height: 1.34;
        }

        .rd-overview-line strong {
            color: var(--rd-ink);
            font-size: 12px;
            font-weight: 900;
        }

        .rd-metric-grid,
        .rd-audience-grid,
        .rd-competitor-grid,
        .rd-economy-grid,
        .rd-evidence-grid,
        .rd-investor-grid {
            display: grid;
            gap: 12px;
        }

        .rd-metric-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }

        .rd-audience-grid,
        .rd-investor-grid {
            grid-template-columns: minmax(280px, .9fr) minmax(0, 1.1fr);
            align-items: start;
        }

        .rd-stacked-cards {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }

        .rd-investor-left {
            display: grid;
            gap: 12px;
        }

        .rd-competitor-grid {
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }

        .rd-economy-grid,
        .rd-evidence-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .rd-metric,
        .rd-audience-card,
        .rd-competitor-card,
        .rd-economy-card,
        .rd-evidence-card,
        .rd-investor-card {
            min-height: 142px;
            padding: 16px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: 0 12px 28px rgba(16, 24, 40, 0.05);
        }

        .rd-metric > span,
        .rd-audience-card > span,
        .rd-competitor-card > span,
        .rd-economy-card > span,
        .rd-evidence-card > span,
        .rd-investor-card > span {
            display: block;
            margin-bottom: 10px;
            color: var(--rd-muted);
            font-size: 12px;
            font-weight: 850;
        }

        .rd-metric strong {
            display: block;
            margin-bottom: 8px;
            color: var(--rd-ink);
            font-size: clamp(24px, 2.5vw, 34px);
            line-height: 1;
            font-weight: 930;
        }

        .rd-audience-card h3,
        .rd-competitor-card h3,
        .rd-economy-card h3,
        .rd-evidence-card h3,
        .rd-investor-card h3 {
            margin: 0 0 9px;
            min-height: 0;
            padding: 0;
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.13;
            font-weight: 900;
            overflow-wrap: normal;
            word-break: normal;
            text-wrap: auto;
        }

        .rd-metric p,
        .rd-audience-card p,
        .rd-competitor-card p,
        .rd-economy-card p,
        .rd-evidence-card p,
        .rd-investor-card p {
            margin: 0;
            color: #475467;
            font-size: 14px;
            line-height: 1.48;
        }

        .rd-audience-card.featured,
        .rd-investor-card.featured {
            background: #101828;
            color: #fff;
        }

        .rd-audience-card.featured > span,
        .rd-investor-card.featured > span {
            color: #d0d5dd;
        }

        .rd-audience-card.featured h3,
        .rd-investor-card.featured h3 {
            color: #fff;
        }

        .rd-audience-card.featured p,
        .rd-investor-card.featured p {
            color: #d0d5dd;
        }

        .rd-audience-grid .rd-stacked-cards,
        .rd-investor-grid .rd-stacked-cards {
            grid-template-columns: 1fr;
        }

        .rd-audience-grid .rd-audience-card,
        .rd-investor-grid .rd-investor-card {
            min-height: 118px;
        }

        .rd-table {
            overflow: hidden;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
        }

        .rd-table-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1.15fr 1.15fr;
            border-bottom: 1px solid var(--rd-line);
        }

        .rd-table-row:last-child {
            border-bottom: 0;
        }

        .rd-table-row.header {
            background: #f8fafc;
            color: var(--rd-ink);
            font-size: 12px;
            font-weight: 900;
        }

        .rd-table-cell {
            min-height: 54px;
            padding: 13px 14px;
            border-right: 1px solid var(--rd-line);
            color: #475467;
            font-size: 13px;
            line-height: 1.38;
        }

        .rd-table-cell:last-child {
            border-right: 0;
        }

        .rd-table-cell strong {
            display: block;
            margin-bottom: 4px;
            color: var(--rd-ink);
            font-size: 13px;
            font-weight: 900;
        }

        .rd-unit-model {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-top: 12px;
        }

        .rd-unit-model div {
            min-height: 86px;
            padding: 13px;
            border: 1px solid #d8e0eb;
            border-radius: var(--rd-radius);
            background: #f8fafc;
        }

        .rd-unit-model span {
            display: block;
            margin-bottom: 7px;
            color: var(--rd-muted);
            font-size: 11px;
            font-weight: 850;
        }

        .rd-unit-model strong {
            display: block;
            color: var(--rd-ink);
            font-size: 18px;
            line-height: 1.12;
            font-weight: 930;
        }

        .rd-window-bar {
            min-height: 48px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            padding: 0 14px;
            border-bottom: 1px solid #dfe6f0;
            background: rgba(255, 255, 255, 0.90);
        }

        .rd-dots {
            display: flex;
            gap: 7px;
        }

        .rd-dots span {
            width: 11px;
            height: 11px;
            border-radius: 50%;
            background: #ff5f57;
        }

        .rd-dots span:nth-child(2) {
            background: #ffbd2e;
        }

        .rd-dots span:nth-child(3) {
            background: #28c840;
        }

        .rd-window-title {
            color: #475467;
            font-size: 12px;
            font-weight: 850;
        }

        .rd-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .rd-chip {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 0 9px;
            border: 1px solid #d8e0eb;
            border-radius: var(--rd-radius);
            background: #fff;
            color: #344054;
            font-size: 12px;
            font-weight: 760;
        }

        .rd-chip.dark {
            background: var(--rd-ink);
            color: #fff;
            border-color: var(--rd-ink);
        }

        .rd-dashboard {
            display: grid;
            grid-template-columns: 214px 1fr;
            min-height: 560px;
        }

        .rd-sidebar {
            padding: 18px 14px;
            background: #111827;
            color: #d0d5dd;
        }

        .rd-side-brand {
            display: flex;
            align-items: center;
            gap: 9px;
            margin-bottom: 22px;
            color: #fff;
            font-size: 16px;
            font-weight: 900;
        }

        .rd-side-dot {
            width: 22px;
            height: 22px;
            border-radius: 6px;
            background: linear-gradient(135deg, var(--rd-blue), var(--rd-green));
        }

        .rd-side-label {
            margin: 18px 0 8px;
            color: #98a2b3;
            font-size: 11px;
            font-weight: 850;
        }

        .rd-side-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: 36px;
            margin-bottom: 5px;
            padding: 0 10px;
            border-radius: var(--rd-radius);
            color: #d0d5dd;
            font-size: 13px;
            font-weight: 720;
        }

        .rd-side-item.active {
            background: rgba(255, 255, 255, 0.10);
            color: #fff;
        }

        .rd-main {
            min-width: 0;
            padding: 18px;
        }

        .rd-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            margin-bottom: 16px;
        }

        .rd-breadcrumbs {
            color: #667085;
            font-size: 13px;
            font-weight: 720;
        }

        .rd-mini-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .rd-mini-button {
            min-height: 34px;
            display: inline-flex;
            align-items: center;
            padding: 0 10px;
            border: 1px solid #d8e0eb;
            border-radius: var(--rd-radius);
            background: #fff;
            color: #344054;
            font-size: 12px;
            font-weight: 800;
        }

        .rd-mini-button.primary {
            background: var(--rd-blue);
            color: #fff;
            border-color: var(--rd-blue);
        }

        .rd-dashboard-title {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-end;
            margin-bottom: 16px;
        }

        .rd-dashboard-title h2 {
            margin: 0 0 6px;
            color: var(--rd-ink);
            font-size: var(--rd-subtitle);
            line-height: 1.1;
            font-weight: 930;
            letter-spacing: 0;
        }

        .rd-dashboard-title p {
            max-width: 670px;
            margin: 0;
            color: var(--rd-muted);
            font-size: 13px;
            line-height: 1.45;
        }

        .rd-health {
            min-width: 190px;
            padding: 10px;
            border: 1px solid #d8e0eb;
            border-radius: var(--rd-radius);
            background: #fff;
        }

        .rd-health-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            color: #667085;
            font-size: 11px;
            font-weight: 850;
        }

        .rd-health-bar {
            height: 8px;
            overflow: hidden;
            border-radius: 999px;
            background: #edf1f6;
        }

        .rd-health-bar span {
            display: block;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--rd-green), var(--rd-amber));
        }

        .rd-kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 12px;
        }

        .rd-kpi,
        .rd-panel,
        .rd-price,
        .rd-card,
        .rd-scenario {
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: 0 10px 26px rgba(16, 24, 40, 0.05);
        }

        .rd-kpi {
            padding: 14px;
        }

        .rd-kpi-label {
            margin-bottom: 8px;
            color: #667085;
            font-size: 11px;
            font-weight: 850;
        }

        .rd-kpi-value {
            color: var(--rd-ink);
            font-size: 29px;
            line-height: 1;
            font-weight: 930;
        }

        .rd-kpi-value.small {
            font-size: 21px;
            line-height: 1.08;
        }

        .rd-kpi-note {
            margin-top: 7px;
            color: #0f8f59;
            font-size: 12px;
            font-weight: 760;
        }

        .rd-grid-2 {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
            gap: 12px;
            margin-bottom: 12px;
        }

        .rd-grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }

        .rd-panel {
            min-width: 0;
            padding: 14px;
        }

        .rd-panel-title {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 12px;
            color: var(--rd-ink);
            font-size: 13px;
            font-weight: 900;
        }

        .rd-panel-title span {
            color: var(--rd-muted);
            font-size: 12px;
            font-weight: 720;
        }

        .rd-line-chart {
            position: relative;
            height: 210px;
            overflow: hidden;
            border: 1px solid #e3e9f2;
            border-radius: var(--rd-radius);
            background:
                linear-gradient(to bottom, transparent 24%, rgba(16,24,40,0.06) 25%, transparent 26%, transparent 49%, rgba(16,24,40,0.06) 50%, transparent 51%, transparent 74%, rgba(16,24,40,0.06) 75%, transparent 76%),
                linear-gradient(to right, transparent 19%, rgba(16,24,40,0.04) 20%, transparent 21%, transparent 39%, rgba(16,24,40,0.04) 40%, transparent 41%, transparent 59%, rgba(16,24,40,0.04) 60%, transparent 61%, transparent 79%, rgba(16,24,40,0.04) 80%, transparent 81%),
                #fbfcff;
        }

        .rd-line-chart::before,
        .rd-line-chart::after {
            content: "";
            position: absolute;
            left: 20px;
            right: 20px;
            height: 86px;
            border-top: 4px solid var(--rd-blue);
            border-radius: 55% 45% 0 0;
        }

        .rd-line-chart::before {
            bottom: 54px;
            transform: rotate(-3deg);
        }

        .rd-line-chart::after {
            bottom: 30px;
            border-top-color: var(--rd-coral);
            transform: rotate(1.5deg);
        }

        .rd-axis {
            position: absolute;
            left: 16px;
            right: 16px;
            bottom: 9px;
            display: flex;
            justify-content: space-between;
            color: #98a2b3;
            font-size: 10px;
            font-weight: 760;
        }

        .rd-summary {
            padding: 13px;
            border: 1px solid #f3d46c;
            border-radius: var(--rd-radius);
            background: #fff8d6;
        }

        .rd-summary strong {
            display: block;
            margin-bottom: 7px;
            color: var(--rd-ink);
            font-size: 13px;
            font-weight: 900;
        }

        .rd-summary p {
            margin: 0;
            color: #475467;
            font-size: 13px;
            line-height: 1.45;
        }

        .rd-tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }

        .rd-tag-row span {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 0 9px;
            border: 1px solid #d8e0eb;
            border-radius: var(--rd-radius);
            background: #fff;
            color: #344054;
            font-size: 11px;
            font-weight: 790;
        }

        .rd-source-list {
            display: grid;
            gap: 8px;
        }

        .rd-source-item {
            display: grid;
            grid-template-columns: minmax(120px, .8fr) minmax(0, 1.2fr);
            gap: 12px;
            min-height: 40px;
            align-items: center;
            padding: 8px 10px;
            border: 1px solid #e3e9f2;
            border-radius: var(--rd-radius);
            background: #fff;
            color: #344054;
            font-size: 12px;
            font-weight: 780;
        }

        .rd-source-item span {
            min-width: 0;
            overflow-wrap: anywhere;
        }

        .rd-source-item span:last-child {
            color: #0f8f59;
            text-align: right;
        }

        .rd-map-helper {
            margin: 0 0 10px;
            color: var(--rd-muted);
            font-size: 13px;
            line-height: 1.45;
        }

        .rd-map-head {
            margin-bottom: 12px;
        }

        .rd-demo-results-gap {
            height: 16px;
        }

        .st-key-rd_demo_input_panel,
        .st-key-rd_map_panel,
        .st-key-rd_summary_panel {
            margin-top: 0 !important;
        }

        .st-key-rd_demo_input_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-rd_map_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-rd_summary_panel [data-testid="stVerticalBlockBorderWrapper"] {
            height: auto !important;
            min-height: 0 !important;
            overflow: visible !important;
            padding: 18px 18px 30px !important;
            border: 1px solid var(--rd-line) !important;
            border-radius: var(--rd-radius) !important;
            background: #fff !important;
            box-shadow: var(--rd-shadow) !important;
        }

        .st-key-rd_demo_input_panel [data-testid="stVerticalBlock"],
        .st-key-rd_map_panel [data-testid="stVerticalBlock"],
        .st-key-rd_summary_panel [data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }

        .st-key-rd_demo_input_panel {
            margin-bottom: 0 !important;
        }

        .st-key-rd_demo_input_panel .rd-decision-grid {
            margin-top: 4px;
        }

        .st-key-rd_map_panel .rd-map-legend,
        .st-key-rd_summary_panel .rd-source-list {
            margin-bottom: 0;
        }

        .rd-map-legend {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 2px;
        }

        .rd-map-legend-row {
            display: grid;
            grid-template-columns: 12px minmax(0, 1fr) auto;
            gap: 9px;
            align-items: center;
            min-height: 36px;
            padding: 7px 9px;
            border: 1px solid #e3e9f2;
            border-radius: var(--rd-radius);
            background: #fff;
            color: #344054;
            font-size: 12px;
            font-weight: 780;
        }

        .rd-map-legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            box-shadow: 0 0 0 2px rgba(255, 255, 255, .9);
        }

        .rd-map-legend-row strong {
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: var(--rd-ink);
            font-size: 12px;
        }

        .rd-map-legend-row span:last-child {
            color: #0f8f59;
            white-space: nowrap;
        }

        .rd-map {
            position: relative;
            min-height: 300px;
            overflow: hidden;
            border: 1px solid #e3e9f2;
            border-radius: var(--rd-radius);
            background:
                radial-gradient(circle at 22% 30%, rgba(18, 185, 129, .95) 0 22px, transparent 23px),
                radial-gradient(circle at 52% 54%, rgba(255, 107, 74, .92) 0 25px, transparent 26px),
                radial-gradient(circle at 73% 34%, rgba(250, 204, 21, .95) 0 19px, transparent 20px),
                radial-gradient(circle at 63% 75%, rgba(37, 99, 235, .72) 0 17px, transparent 18px),
                linear-gradient(135deg, #ecf4ff, #fbfcff);
        }

        .rd-map::before {
            content: "";
            position: absolute;
            inset: 18px;
            border: 1px dashed rgba(16, 24, 40, 0.18);
            border-radius: var(--rd-radius);
        }

        .rd-map-card {
            position: absolute;
            top: 16px;
            right: 16px;
            width: min(220px, calc(100% - 32px));
            padding: 12px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: rgba(255, 255, 255, .94);
            box-shadow: 0 16px 34px rgba(16, 24, 40, 0.12);
        }

        .rd-map-card strong {
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
        }

        .rd-map-card p {
            margin: 0;
            color: var(--rd-muted);
            font-size: 12px;
            line-height: 1.38;
        }

        .rd-section-head {
            display: grid;
            grid-template-columns: minmax(440px, 1.18fr) minmax(280px, .82fr);
            column-gap: 28px;
            row-gap: 12px;
            align-items: end;
            margin-bottom: 18px;
        }

        .rd-section-title,
        .rd-section-head h2,
        .rd-problem-title,
        .rd-final h2 {
            margin: 0;
            color: var(--rd-ink);
            font-family: var(--rd-font) !important;
            font-size: var(--rd-section-title) !important;
            line-height: 1.1 !important;
            font-weight: var(--rd-section-title-weight) !important;
            font-variation-settings: "wght" var(--rd-section-title-weight);
            letter-spacing: 0 !important;
        }

        .rd-section-head p {
            align-self: end;
            justify-self: end;
            max-width: 500px;
            margin: 0;
            padding-bottom: 4px;
            color: var(--rd-muted);
            font-size: 16px;
            line-height: 1.5;
        }

        #demo {
            padding-bottom: 12px;
        }

        .rd-card-grid-3,
        .rd-card-grid-4,
        .rd-price-grid {
            display: grid;
            gap: 12px;
        }

        .rd-card-grid-3 {
            grid-template-columns: repeat(3, 1fr);
        }

        .rd-card-grid-4 {
            grid-template-columns: repeat(4, 1fr);
        }

        .rd-card {
            min-height: 156px;
            padding: 16px;
        }

        .rd-card.blue {
            background: var(--rd-blue-soft);
        }

        .rd-card.green {
            background: var(--rd-green-soft);
        }

        .rd-card.amber {
            background: var(--rd-amber-soft);
        }

        .rd-card.coral {
            background: var(--rd-coral-soft);
        }

        .rd-card .num {
            margin-bottom: 11px;
            color: var(--rd-muted);
            font-size: 12px;
            font-weight: 850;
        }

        .rd-card h3 {
            margin: 0 0 9px;
            min-height: 0;
            padding: 0;
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
            overflow-wrap: normal;
            word-break: normal;
            text-wrap: auto;
        }

        .rd-card p {
            margin: 0;
            color: #475467;
            font-size: 14px;
            line-height: 1.46;
        }

        .rd-problem-section {
            padding-top: 38px;
        }

        .rd-problem-layout {
            display: grid;
            grid-template-columns: minmax(440px, 1.18fr) minmax(280px, .82fr);
            gap: 28px;
            align-items: start;
            margin-bottom: 18px;
        }

        .rd-problem-title {
            margin: 0;
            max-width: 760px;
        }

        .rd-problem-lead {
            max-width: 820px;
            margin: 0;
            color: var(--rd-muted);
            font-size: 17px;
            line-height: 1.55;
        }

        .rd-manual-flow {
            display: grid;
            gap: 8px;
            padding: 14px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: 0 14px 34px rgba(16, 24, 40, 0.08);
        }

        .rd-manual-flow-title {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: var(--rd-ink);
            font-size: 13px;
            font-weight: 900;
        }

        .rd-manual-flow-title span:last-child {
            color: #b42318;
            font-weight: 850;
        }

        .rd-manual-step {
            display: grid;
            grid-template-columns: 86px minmax(0, 1fr);
            gap: 12px;
            min-height: 38px;
            align-items: center;
            padding: 8px 10px;
            border: 1px solid #e3e9f2;
            border-radius: var(--rd-radius);
            background: #f8fafc;
            color: #344054;
            font-size: 12px;
            font-weight: 780;
        }

        .rd-manual-step strong {
            color: var(--rd-ink);
            font-size: 12px;
            font-weight: 900;
        }

        .rd-problem-list {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }

        .rd-problem-item {
            display: grid;
            grid-template-columns: 42px minmax(0, 1fr);
            gap: 12px;
            min-height: 150px;
            padding: 16px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: 0 14px 30px rgba(16, 24, 40, 0.06);
        }

        .rd-problem-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--rd-soft);
            color: var(--rd-ink);
            font-size: 13px;
            font-weight: 930;
        }

        .rd-problem-item h3 {
            margin: 0 0 8px;
            min-height: 0;
            padding: 0;
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
            overflow-wrap: normal;
            word-break: normal;
            text-wrap: auto;
        }

        .rd-problem-item p {
            margin: 0;
            color: #475467;
            font-size: 14px;
            line-height: 1.45;
        }

        .rd-demo-brief {
            display: grid;
            grid-template-columns: minmax(240px, .72fr) minmax(0, 1.28fr);
            gap: 12px;
            align-items: start;
            margin: 8px 0 10px;
        }

        .rd-demo-card,
        .rd-demo-note {
            padding: 14px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: 0 12px 30px rgba(16, 24, 40, 0.07);
        }

        .rd-demo-card h3,
        .rd-demo-note h3 {
            margin: 0 0 8px;
            min-height: 0;
            padding: 0;
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
            overflow-wrap: normal;
            word-break: normal;
            text-wrap: auto;
        }

        .rd-demo-card p,
        .rd-demo-note p {
            margin: 0;
            color: var(--rd-muted);
            font-size: 14px;
            line-height: 1.45;
        }

        .rd-demo-note {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
            box-shadow: none;
            background: #f8fafc;
        }

        .rd-demo-note span {
            display: block;
            color: var(--rd-muted);
            font-size: 11px;
            font-weight: 850;
        }

        .rd-demo-note strong {
            display: block;
            margin-top: 5px;
            color: var(--rd-ink);
            font-size: 14px;
            line-height: 1.25;
            font-weight: 900;
        }

        .rd-compact-grid .rd-card {
            min-height: 142px;
            box-shadow: none;
        }

        div[data-testid="stSelectbox"] label,
        div[data-testid="stSlider"] label {
            color: #344054 !important;
            font-size: 13px !important;
            font-weight: 800 !important;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--rd-green), var(--rd-amber));
        }

        .rd-decision-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin: 0 0 14px;
        }

        .rd-decision-card {
            min-height: 108px;
            padding: 13px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
        }

        .rd-decision-card span {
            display: block;
            margin-bottom: 8px;
            color: var(--rd-muted);
            font-size: 12px;
            font-weight: 850;
        }

        .rd-decision-card strong {
            display: block;
            color: var(--rd-ink);
            font-size: 26px;
            line-height: 1.04;
            font-weight: 930;
        }

        .rd-decision-card em {
            display: block;
            margin-top: 8px;
            color: #0f8f59;
            font-size: 12px;
            font-style: normal;
            font-weight: 760;
        }

        .rd-compare {
            overflow: hidden;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
        }

        .rd-compare-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            border-bottom: 1px solid var(--rd-line);
        }

        .rd-compare-row:last-child {
            border-bottom: 0;
        }

        .rd-compare-cell {
            padding: 16px 18px;
            color: #344054;
            font-size: 15px;
            line-height: 1.45;
        }

        .rd-compare-cell:first-child {
            border-right: 1px solid var(--rd-line);
            background: #f8fafc;
        }

        .rd-compare-cell strong {
            display: block;
            margin-bottom: 5px;
            color: var(--rd-ink);
            font-size: 12px;
            font-weight: 900;
        }

        .rd-price-grid {
            grid-template-columns: repeat(6, minmax(0, 1fr));
            align-items: stretch;
        }

        .rd-price {
            grid-column: span 2;
            min-height: 274px;
            display: flex;
            flex-direction: column;
            padding: 16px;
        }

        .rd-price:nth-child(4),
        .rd-price:nth-child(5) {
            grid-column: span 3;
            min-height: 236px;
        }

        .rd-price.featured {
            border-color: #f2c200;
            background: #fff8d6;
            box-shadow: 0 18px 42px rgba(250, 204, 21, 0.22);
        }

        .rd-badge {
            align-self: flex-start;
            margin-bottom: 10px;
            padding: 5px 8px;
            border-radius: var(--rd-radius);
            background: var(--rd-ink);
            color: #fff;
            font-size: 11px;
            font-weight: 850;
        }

        .rd-price h3 {
            margin: 0 0 8px;
            color: var(--rd-ink);
            font-size: var(--rd-subtitle);
            line-height: 1.1;
            font-weight: 900;
        }

        .rd-price-value {
            margin-bottom: 5px;
            color: var(--rd-ink);
            font-size: clamp(25px, 2.05vw, 29px);
            line-height: 1;
            font-weight: 930;
            white-space: nowrap;
        }

        .rd-price-sub {
            margin-bottom: 12px;
            color: var(--rd-muted);
            font-size: 13px;
            font-weight: 760;
        }

        .rd-price ul {
            flex: 1;
            margin: 0 0 14px;
            padding-left: 18px;
            color: #475467;
            font-size: 13px;
            line-height: 1.38;
        }

        .rd-price li {
            margin-bottom: 5px;
        }

        .rd-user-flow {
            margin-top: 16px;
        }

        .rd-user-flow-head {
            display: grid;
            grid-template-columns: minmax(420px, 1.12fr) minmax(280px, .88fr);
            gap: 20px;
            align-items: end;
            margin-bottom: 10px;
        }

        .rd-user-flow-head h3 {
            margin: 0;
            color: var(--rd-ink);
            font-size: var(--rd-subtitle);
            line-height: 1.08;
            font-weight: 930;
        }

        .rd-user-flow-head p {
            justify-self: end;
            max-width: 500px;
            margin: 0;
            color: var(--rd-muted);
            font-size: 15px;
            line-height: 1.5;
        }

        .rd-flow-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            overflow: hidden;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
        }

        .rd-flow-step {
            min-height: 142px;
            padding: 15px;
            border-right: 1px solid var(--rd-line);
            background: #fff;
        }

        .rd-flow-step:last-child {
            border-right: 0;
        }

        .rd-flow-step span {
            display: block;
            margin-bottom: 10px;
            color: var(--rd-muted);
            font-size: 12px;
            font-weight: 850;
        }

        .rd-flow-step strong {
            display: block;
            margin-bottom: 8px;
            min-height: 0;
            padding: 0;
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
            overflow-wrap: normal;
            word-break: normal;
            text-wrap: auto;
        }

        .rd-flow-step p {
            margin: 0;
            color: #475467;
            font-size: 13px;
            line-height: 1.45;
        }

        .rd-faq-grid {
            display: grid;
            grid-template-columns: .9fr 1.1fr;
            gap: 26px;
            align-items: start;
        }

        .rd-faq-list {
            display: grid;
            gap: 10px;
        }

        details.rd-faq {
            overflow: hidden;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
        }

        details.rd-faq summary {
            cursor: pointer;
            padding: 16px;
            color: var(--rd-ink);
            font-size: 15px;
            font-weight: 900;
            list-style: none;
        }

        details.rd-faq summary::-webkit-details-marker {
            display: none;
        }

        details.rd-faq p {
            margin: 0;
            padding: 0 16px 16px;
            color: var(--rd-muted);
            font-size: 14px;
            line-height: 1.5;
        }

        .rd-final {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 24px;
            align-items: end;
            margin-top: 18px;
            padding: 28px;
            border-radius: var(--rd-radius);
            background: #101828;
            color: #fff;
        }

        .rd-final h2 {
            margin: 0 0 10px;
            color: #fff;
        }

        .rd-final p {
            max-width: 760px;
            margin: 0;
            color: #d0d5dd;
            font-size: 17px;
            line-height: 1.5;
        }

        .rd-footer-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            min-height: 58px;
            margin-top: 24px;
            padding: 8px 0 0;
            border-top: 1px solid rgba(16, 24, 40, 0.10);
        }

        .rd-footer-links {
            display: flex;
            align-items: center;
            gap: 14px;
            color: var(--rd-muted);
            font-size: 13px;
            font-weight: 750;
        }

        .rd-footer-links a {
            color: inherit !important;
            text-decoration: none !important;
        }

        .rd-footer-links a:hover {
            color: var(--rd-ink) !important;
        }

        @media (max-width: 1120px) {
            .rd-section-head,
            .rd-problem-layout,
            .rd-demo-brief,
            .rd-user-flow-head,
            .rd-faq-grid,
            .rd-final {
                grid-template-columns: 1fr;
            }

            .rd-price-grid,
            .rd-card-grid-4,
            .rd-metric-grid,
            .rd-competitor-grid,
            .rd-economy-grid,
            .rd-evidence-grid,
            .rd-unit-model {
                grid-template-columns: repeat(2, 1fr);
            }

            .rd-audience-grid,
            .rd-investor-grid {
                grid-template-columns: 1fr;
            }

            .rd-flow-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .rd-dashboard {
                grid-template-columns: 1fr;
            }

            .rd-sidebar {
                display: none;
            }

            .rd-kpi-grid,
            .rd-grid-3,
            .rd-problem-list,
            .rd-decision-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .rd-price,
            .rd-price:nth-child(4),
            .rd-price:nth-child(5) {
                grid-column: auto;
            }

            .rd-hero {
                grid-template-columns: 1fr;
                padding: 34px 0 52px;
            }

            .rd-hero > div:first-child {
                max-width: none;
            }

            .rd-section-head p,
            .rd-user-flow-head p {
                justify-self: start;
                max-width: 660px;
                padding-bottom: 0;
            }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 14px;
                padding-right: 14px;
            }

            .rd-section {
                padding: 32px 0;
            }

            .rd-section-head {
                margin-bottom: 14px;
            }

            .rd-section-head p {
                font-size: 15px;
                line-height: 1.45;
            }

            .rd-nav {
                margin-left: -14px;
                margin-right: -14px;
            }

            .rd-nav-links,
            .rd-footer-links {
                display: none;
            }

            .rd-footer-nav {
                align-items: flex-start;
                flex-direction: column;
            }

            .rd-title-xl {
                font-size: 40px;
                line-height: 1.06;
            }

            .rd-hero {
                padding: 28px 0 34px;
            }

            .rd-note {
                margin-top: 14px;
            }

            .rd-proof {
                min-height: 0;
                padding: 12px;
            }

            .rd-proof-grid,
            .rd-card-grid-3,
            .rd-card-grid-4,
            .rd-price-grid,
            .rd-stacked-cards,
            .rd-metric-grid,
            .rd-audience-grid,
            .rd-competitor-grid,
            .rd-economy-grid,
            .rd-evidence-grid,
            .rd-investor-grid,
            .rd-unit-model,
            .rd-map-legend,
            .rd-demo-note,
            .rd-kpi-grid,
            .rd-grid-2,
            .rd-grid-3,
            .rd-problem-list,
            .rd-decision-grid,
            .rd-flow-grid,
            .rd-compare-row {
                grid-template-columns: 1fr;
            }

            .rd-demo-note {
                grid-template-columns: repeat(2, minmax(0, 1fr));
                padding: 12px;
            }

            .rd-demo-note strong {
                font-size: 13px;
            }

            .rd-demo-card {
                padding: 13px;
            }

            .rd-compare-cell:first-child {
                border-right: 0;
                border-bottom: 1px solid var(--rd-line);
            }

            .rd-table-row,
            .rd-overview-line {
                grid-template-columns: 1fr;
            }

            .rd-table-cell {
                border-right: 0;
                border-bottom: 1px solid var(--rd-line);
            }

            .rd-table-cell:last-child {
                border-bottom: 0;
            }

            .rd-window-bar,
            .rd-topline,
            .rd-dashboard-title {
                align-items: flex-start;
                flex-direction: column;
            }

            .rd-demo-results-gap {
                height: 14px;
            }

            .st-key-rd_demo_input_panel [data-testid="stVerticalBlockBorderWrapper"],
            .st-key-rd_map_panel [data-testid="stVerticalBlockBorderWrapper"],
            .st-key-rd_summary_panel [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 14px 14px 22px !important;
            }

            .rd-decision-card {
                min-height: 0;
                padding: 12px;
            }

            .rd-decision-card strong {
                font-size: 24px;
            }

            .rd-map {
                min-height: 250px;
            }

            .rd-source-item {
                grid-template-columns: 1fr;
                gap: 4px;
                align-items: start;
            }

            .rd-source-item span:last-child {
                text-align: left;
            }

            .rd-price,
            .rd-price:nth-child(4),
            .rd-price:nth-child(5) {
                min-height: 0;
                padding: 15px;
            }

            .rd-price ul {
                flex: none;
            }

            .rd-chip-row,
            .rd-mini-actions {
                width: 100%;
            }

            .rd-health {
                width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def render_region_map(region_name: str) -> None:
    points = REGION_MAP_POINTS[region_name]
    center_lat = sum(float(point["lat"]) for point in points) / len(points)
    center_lon = sum(float(point["lon"]) for point in points) / len(points)

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 235],
        line_width_min_pixels=2,
        pickable=True,
        radius_min_pixels=9,
        radius_max_pixels=34,
        opacity=0.9,
    )
    label_layer = pdk.Layer(
        "TextLayer",
        data=points,
        get_position="[lon, lat]",
        get_text="district",
        get_size=13,
        get_color=[16, 24, 40, 230],
        get_pixel_offset=[0, -28],
        get_text_anchor="'middle'",
        get_alignment_baseline="'bottom'",
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=CITY_MAP_ZOOM.get(region_name, 10.2),
                pitch=0,
            ),
            layers=[point_layer, label_layer],
            tooltip={
                "html": (
                    "<b>{district}</b><br/>"
                    "Спрос: {demand}/100<br/>"
                    "Конкуренция: {competition}/100<br/>"
                    "Решение: {status}"
                ),
                "style": {
                    "backgroundColor": "white",
                    "color": "#101828",
                    "fontFamily": "Inter, Arial, sans-serif",
                    "fontSize": "12px",
                    "border": "1px solid #d9e0ea",
                    "borderRadius": "8px",
                    "boxShadow": "0 14px 32px rgba(16, 24, 40, 0.16)",
                },
            },
        ),
        height=330,
        width="stretch",
    )


def render_map_legend(region_name: str) -> None:
    rows = []
    for point in REGION_MAP_POINTS[region_name]:
        color = point["color"]
        rows.append(
            '<div class="rd-map-legend-row">'
            f'<span class="rd-map-legend-dot" style="background:rgba({color[0]}, {color[1]}, {color[2]}, .9);"></span>'
            f'<strong>{escape(str(point["district"]))}</strong>'
            f'<span>{escape(str(point["status"]))}</span>'
            "</div>"
        )
    html_block(f'<div class="rd-map-legend">{"".join(rows)}</div>')


def render_nav() -> None:
    html_block(
        """
        <nav class="rd-nav">
            <a class="rd-brand" href="#top"><span class="rd-mark"></span><span>RealDemand</span></a>
            <div class="rd-nav-links">
                <a href="#market">Рынок</a>
                <a href="#audience">Аудитория</a>
                <a href="#problem">Проблема</a>
                <a href="#solution">Решение</a>
                <a href="#competition">Конкуренты</a>
                <a href="#economics">Экономика</a>
                <a href="#investment">Бизнес-логика</a>
            </div>
            <a class="rd-btn" href="#investment">Логика проекта</a>
        </nav>
        """
    )


def render_hero() -> None:
    html_block(
        """
        <section class="rd-hero" id="top">
            <div>
                <div class="rd-eyebrow">Обзор продукта</div>
                <h1 class="rd-title-xl">RealDemand выбирает, где запускать пилот</h1>
                <p class="rd-lead">Сервис показывает район старта, конкурентов, спрос, риски бюджета и источники для решения о запуске.</p>
                <p class="rd-note">Клиент покупает быстрый ответ перед расходами на рекламу и операцию: разовый отчет от 19 900 ₽ или подписку для регулярных запусков.</p>
                <div class="rd-actions">
                    <a class="rd-btn" href="#market">Смотреть обзор</a>
                    <a class="rd-btn secondary" href="#demo">Открыть прототип</a>
                </div>
                <div class="rd-proof-grid">
                    <div class="rd-proof"><strong>Пользователь</strong><span>Владелец, маркетинг или команда роста перед запуском в новой локации.</span></div>
                    <div class="rd-proof"><strong>Результат</strong><span>Район старта, список конкурентов, причины рекомендации и план контроля.</span></div>
                    <div class="rd-proof"><strong>Бизнес</strong><span>Разовый отчет ведет в подписку для команд с повторными запусками.</span></div>
                </div>
            </div>
            <div>
                <div class="rd-panel rd-hero-result">
                    <div class="rd-panel-title">Пример ответа сервиса <span>для пользователя</span></div>
                    <div class="rd-summary"><strong>Тестировать осторожно</strong><p>Казань, домашние сервисы, бюджет 350&nbsp;тыс.&nbsp;₽. Начать с Ново-Савиновского района, центр не брать в первый пилот.</p></div>
                    <div class="rd-source-list" style="margin-top:14px;">
                        <div class="rd-source-item"><span>Район старта</span><span>Ново-Савиновский</span></div>
                        <div class="rd-source-item"><span>Конкуренты</span><span>Клининг 116, Чистый дом, Мастер чистоты</span></div>
                        <div class="rd-source-item"><span>Спрос</span><span>+24% по запросам и отзывам</span></div>
                        <div class="rd-source-item"><span>Контроль</span><span>скорость отклика и вечерние слоты</span></div>
                        <div class="rd-source-item"><span>Экспорт</span><span>отчет с источниками</span></div>
                    </div>
                </div>
            </div>
        </section>
        """
    )


def render_market_and_audience() -> None:
    html_block(
        """
        <section class="rd-section" id="market">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Рынок</div>
                    <h2 class="rd-section-title">Клиент платит перед запуском в новой локации</h2>
                </div>
                <p>Задача повторяется каждый раз, когда бизнес выбирает новый город, район или нишу.</p>
            </div>
            <div class="rd-metric-grid">
                <div class="rd-metric"><span>Кто платит</span><strong>локальные услуги</strong><p>Клининг, ремонт, фитнес, кружки, кофейни, франчайзи.</p></div>
                <div class="rd-metric"><span>Когда платит</span><strong>до запуска</strong><p>До рекламы, аренды, найма и операционной подготовки.</p></div>
                <div class="rd-metric"><span>Что получает</span><strong>район старта</strong><p>Плюс конкуренты, спрос, риски бюджета и источники.</p></div>
                <div class="rd-metric"><span>Почему повторяет</span><strong>новые точки</strong><p>Каждая новая локация требует такого же решения.</p></div>
            </div>
        </section>
        <section class="rd-section" id="audience">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Целевая аудитория</div>
                    <h2 class="rd-section-title">Пользователь хочет не аналитику, а решение</h2>
                </div>
                <p>Вопрос пользователя: запускаться здесь, выбрать другой район или ограничить пилот.</p>
            </div>
            <div class="rd-audience-grid">
                <div class="rd-audience-card featured">
                    <span>Основной сегмент</span>
                    <h3>Малый и средний бизнес с локальными услугами</h3>
                    <p>Клининг, ремонт, детские кружки, фитнес-студии, кофейни у дома и франчайзи.</p>
                </div>
                <div class="rd-stacked-cards">
                    <div class="rd-audience-card"><span>Пользователь</span><h3>Маркетолог или аналитик</h3><p>Готовит решение по району, конкурентам и бюджету.</p></div>
                    <div class="rd-audience-card"><span>Покупатель</span><h3>Владелец или руководитель</h3><p>Утверждает первый бюджет и формат пилота.</p></div>
                    <div class="rd-audience-card"><span>Команда роста</span><h3>Продукт и рост</h3><p>Сравнивает новые города, ниши и офферы.</p></div>
                </div>
            </div>
        </section>
        """
    )


def render_problem() -> None:
    html_block(
        """
        <section class="rd-section rd-problem-section" id="problem">
            <div class="rd-problem-layout">
                <div>
                    <div class="rd-eyebrow">Проблема</div>
                    <h2 class="rd-section-title rd-problem-title">Решение о запуске часто собирают из несвязанных источников</h2>
                </div>
                <div class="rd-manual-flow">
                    <div class="rd-manual-flow-title"><span>Как это обычно выглядит</span><span>3-8 часов</span></div>
                    <div class="rd-manual-step"><strong>Статистика</strong><span>город, доходы, районы роста</span></div>
                    <div class="rd-manual-step"><strong>Спрос</strong><span>поисковые запросы и сезонность</span></div>
                    <div class="rd-manual-step"><strong>Конкуренты</strong><span>карты, сайты, отзывы, акции</span></div>
                    <div class="rd-manual-step"><strong>Решение</strong><span>район пилота и риск бюджета</span></div>
                </div>
            </div>
            <p class="rd-problem-lead">Даже когда данные собраны, команде нужно понять, где тестировать предложение и какой риск у первого бюджета.</p>
            <div class="rd-problem-list" style="margin-top:16px;">
                <div class="rd-problem-item"><div class="rd-problem-num">01</div><div><h3>Нет одной картины</h3><p>Росстат, карты, выдача, сайты игроков и отзывы приходится сводить вручную.</p></div></div>
                <div class="rd-problem-item"><div class="rd-problem-num">02</div><div><h3>Сложно выбрать район</h3><p>В центре может быть много спроса, но аренда, реклама и конкуренты быстро съедают бюджет.</p></div></div>
                <div class="rd-problem-item"><div class="rd-problem-num">03</div><div><h3>Ошибки видны поздно</h3><p>Если пилот запущен не там, команда узнает это уже после расходов на рекламу и операцию.</p></div></div>
            </div>
        </section>
        """
    )


def render_solution_logic() -> None:
    html_block(
        """
        <section class="rd-section" id="solution">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Решение</div>
                    <h2 class="rd-section-title">Сервис превращает вводные в решение о пилоте</h2>
                </div>
                <p>На входе город, сфера и бюджет. На выходе район старта, конкуренты, риски и отчет.</p>
            </div>
            <div class="rd-flow-grid">
                <div class="rd-flow-step"><span>Шаг 01</span><strong>Пользователь задает вводные</strong><p>Город, сфера, бюджет, цель пилота и горизонт теста.</p></div>
                <div class="rd-flow-step"><span>Шаг 02</span><strong>Сервис собирает рынок</strong><p>Спрос, конкуренты, отзывы, районы и источники.</p></div>
                <div class="rd-flow-step"><span>Шаг 03</span><strong>Сервис считает сценарий</strong><p>Индекс, район старта, риск бюджета и причины вывода.</p></div>
                <div class="rd-flow-step"><span>Шаг 04</span><strong>Команда получает отчет</strong><p>Решение, список конкурентов, карта районов и план контроля.</p></div>
            </div>
            <div class="rd-compare" style="margin-top:12px;">
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Клиентская польза</strong>Быстрее принять решение о запуске и снизить риск первого бюджета</div><div class="rd-compare-cell"><strong>Бизнес-логика</strong>Та же задача повторяется у разных команд, городов и вертикалей</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Продуктовый результат</strong>Индекс, карта районов, риски, источники и короткий отчет</div><div class="rd-compare-cell"><strong>Монетизация</strong>Разовый отчет для входа, подписка для регулярных проверок, API и внедрение для сетей</div></div>
            </div>
        </section>
        """
    )


def render_interactive_demo() -> None:
    html_block(
        """
        <section class="rd-section" id="demo">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Прототип</div>
                    <h2 class="rd-section-title">Демо: клининг в Казани, бюджет 350 тыс.&nbsp;₽</h2>
                </div>
                <p>Здесь видно, что получает пользователь: район старта, конкуренты, причины решения и отчет.</p>
            </div>
            <div class="rd-demo-brief">
                <div class="rd-demo-card">
                    <h3>Юзкейс пользователя</h3>
                    <p>Команда выбирает район для первого пилота и смотрит, какие конкуренты уже забирают спрос.</p>
                </div>
                <div class="rd-demo-note">
                    <div><span>1. Вводные</span><strong>город, сфера, бюджет</strong></div>
                    <div><span>2. Рынок</span><strong>спрос и конкуренты</strong></div>
                    <div><span>3. Решение</span><strong>район старта</strong></div>
                    <div><span>4. Отчет</span><strong>источники и контроль</strong></div>
                </div>
            </div>
        </section>
        """
    )

    with st.container(border=True, key="rd_demo_input_panel"):
        controls = st.columns([1, 1, 1], gap="medium")
        with controls[0]:
            region_name = st.selectbox("Регион", list(REGIONS), index=0)
        with controls[1]:
            sector_name = st.selectbox("Сфера", list(SECTORS), index=0)
        with controls[2]:
            budget = st.slider("Бюджет пилота, тыс. ₽", min_value=100, max_value=900, value=350, step=50)

        region = REGIONS[region_name]
        sector = SECTORS[sector_name]
        budget_bonus = min(8, max(-8, (budget - 300) / 70))
        score = clamp(region.demand * 0.36 + (100 - region.competition) * 0.22 + region.confidence * 0.24 + sector.base + budget_bonus)
        launch_label, launch_note = recommendation(score)
        competition_label = "Низкая" if region.competition < 45 else "Средняя" if region.competition < 68 else "Высокая"
        competitors = COMPETITOR_EXAMPLES[sector_name]
        competitor_rows = "".join(
            '<div class="rd-source-item">'
            f'<span>{escape(name)}</span>'
            f'<span>{escape(signal)} / {escape(note)}</span>'
            "</div>"
            for name, signal, note in competitors
        )

        st.progress(score / 100, text=f"Индекс привлекательности: {score}/100")

        html_block(
            f"""
                <div class="rd-decision-grid">
                    <div class="rd-decision-card"><span>Итог сервиса</span><strong>{escape(launch_label)}</strong><em>{escape(sector.label)}</em></div>
                    <div class="rd-decision-card"><span>Первый район</span><strong>{escape(region.district)}</strong><em>по карте спроса</em></div>
                    <div class="rd-decision-card"><span>Спрос</span><strong>+{region.demand_growth}%</strong><em>по запросам и отзывам</em></div>
                    <div class="rd-decision-card"><span>Конкуренция</span><strong>{escape(competition_label)}</strong><em>{len(competitors)} игрока в расчете</em></div>
                </div>
            """
        )

    html_block("""<div class="rd-demo-results-gap"></div>""")

    map_col, summary_col = st.columns([1.08, 0.92], gap="medium")
    with map_col:
        with st.container(border=True, key="rd_map_panel"):
            html_block(
                f"""
                    <div class="rd-map-head">
                        <div class="rd-panel-title">Карта районов <span>{escape(region_name)}</span></div>
                        <p class="rd-map-helper">Карта отвечает на вопрос “где начать”: зеленый район идет в первый пилот, синий можно добавить вторым, красный дорогой для входа.</p>
                    </div>
                """
            )
            render_region_map(region_name)
            render_map_legend(region_name)

    with summary_col:
        with st.container(border=True, key="rd_summary_panel"):
            html_block(
                f"""
                    <div class="rd-panel-title">Для пользователя <span>результат расчета</span></div>
                    <div class="rd-summary"><strong>{escape(launch_label)}</strong><p>Первый район: {escape(region.district)}. Учитываем спрос, конкурентов и ограничение бюджета: {escape(sector.weak_spot.lower())}.</p></div>
                    <div class="rd-tag-row">
                        <span>Отзывы и обсуждения +{region.social_growth}%</span>
                        <span>Бюджет {budget} тыс. ₽</span>
                        <span>{escape(region.district)}</span>
                        <span>{escape(sector_name)}</span>
                    </div>
                    <div class="rd-panel-title" style="margin-top:14px;">Конкуренты в расчете <span>демо-слой</span></div>
                    <div class="rd-source-list">{competitor_rows}</div>
                    <div class="rd-panel-title" style="margin-top:14px;">Сигналы решения <span>почему так</span></div>
                    <div class="rd-source-list">
                        <div class="rd-source-item"><span>Район старта</span><span>{escape(region.district)}</span></div>
                        <div class="rd-source-item"><span>Сигнал спроса</span><span>+{region.demand_growth}%</span></div>
                        <div class="rd-source-item"><span>Плотность конкурентов</span><span>{escape(competition_label.lower())}</span></div>
                        <div class="rd-source-item"><span>Фокус контроля</span><span>{escape(sector.weak_spot.lower())}</span></div>
                    </div>
                """
            )

    html_block(
        """
        <div class="rd-user-flow">
            <div class="rd-user-flow-head">
                <h3>Какие задачи закрывает прототип</h3>
                <p>Один расчет показывает пользователю, где стартовать, кого учитывать и что контролировать в первые недели пилота.</p>
            </div>
            <div class="rd-flow-grid">
                <div class="rd-flow-step"><span>Задача 01</span><strong>Оценить спрос</strong><p>Понять, хватает ли спроса для пилота в выбранном городе и сфере.</p></div>
                <div class="rd-flow-step"><span>Задача 02</span><strong>Выбрать район старта</strong><p>Сравнить районы и не тратить первый бюджет на слишком дорогую точку входа.</p></div>
                <div class="rd-flow-step"><span>Задача 03</span><strong>Увидеть конкурентов</strong><p>Понять, кто уже забирает спрос и чем эти игроки сильны.</p></div>
                <div class="rd-flow-step"><span>Задача 04</span><strong>Собрать отчет</strong><p>Получить короткий вывод с районом, рисками, источниками и планом контроля.</p></div>
            </div>
        </div>
        """
    )


def render_sources_and_cases() -> None:
    html_block(
        """
        <section class="rd-section" id="sources">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Данные</div>
                    <h2 class="rd-section-title">Какие данные попадают в расчет</h2>
                </div>
                <p>Источники нужны не для витрины, а чтобы объяснить рекомендацию и собрать отчет.</p>
            </div>
            <div class="rd-card-grid-4 rd-compact-grid">
                <div class="rd-card"><div class="num">Статистика</div><h3>Емкость района</h3><p>Население, доходы, занятость и районы роста.</p></div>
                <div class="rd-card blue"><div class="num">Спрос</div><h3>Запросы</h3><p>Динамика поиска, сезонность и регулярность потребности.</p></div>
                <div class="rd-card amber"><div class="num">Отзывы</div><h3>Боли клиентов</h3><p>Скорость, цена, график, качество и частые жалобы.</p></div>
                <div class="rd-card green"><div class="num">Конкуренты</div><h3>Игроки рынка</h3><p>Карты, выдача, сайты, акции и частота отзывов.</p></div>
            </div>
        </section>
        <section class="rd-section" id="cases">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">MVP и запуск</div>
                    <h2 class="rd-section-title">Что продается в MVP</h2>
                </div>
                <p>Покупка начинается с отчета по одной локации и растет в регулярный кабинет.</p>
            </div>
            <div class="rd-evidence-grid">
                <div class="rd-evidence-card"><span>Отчет</span><h3>Одна локация</h3><p>Район старта, конкуренты, спрос, риски и источники.</p></div>
                <div class="rd-evidence-card"><span>Кабинет</span><h3>Повторные расчеты</h3><p>Новые районы, города, ниши и сравнение сценариев.</p></div>
                <div class="rd-evidence-card"><span>Мониторинг</span><h3>Конкуренты и отзывы</h3><p>Еженедельные изменения рынка для команд роста.</p></div>
                <div class="rd-evidence-card"><span>Экспорт</span><h3>Отчет для команды</h3><p>Короткий документ для обсуждения бюджета пилота.</p></div>
                <div class="rd-evidence-card"><span>Цена</span><h3>1&nbsp;900&nbsp;₽ → 29&nbsp;900&nbsp;₽</h3><p>Разовый вход и подписка для регулярных запусков.</p></div>
                <div class="rd-evidence-card"><span>Покупатель</span><h3>Владелец / рост / маркетинг</h3><p>Тот, кто отвечает за первый бюджет запуска.</p></div>
            </div>
        </section>
        """
    )


def render_result() -> None:
    html_block(
        """
        <section class="rd-section" id="result">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Результат</div>
                    <h2 class="rd-section-title">На выходе — план пилота с рисками и ограничениями</h2>
                </div>
                <p>Команда сохраняет контроль над решением, а сервис показывает, какие сигналы поддерживают сценарий и что важно контролировать в первые недели.</p>
            </div>
            <div class="rd-compare">
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>3-8 часов на ручной сбор ссылок и таблиц</div><div class="rd-compare-cell"><strong>Стало</strong>15-30 минут до первой версии решения</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>“в Казани есть спрос”</div><div class="rd-compare-cell"><strong>Стало</strong>“начать с Ново-Савиновского района, центр отложить”</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>спор о том, каким источникам верить</div><div class="rd-compare-cell"><strong>Стало</strong>видно, где данные сходятся и что добавить в ручной контроль</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>решение без понятного критерия успеха</div><div class="rd-compare-cell"><strong>Стало</strong>пилот на 6-8 недель с метриками спроса и стоимости заявки</div></div>
            </div>
        </section>
        """
    )


def render_competition() -> None:
    html_block(
        """
        <section class="rd-section" id="competition">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Конкуренты</div>
                    <h2 class="rd-section-title">Основной конкурент — ручная аналитика, а не другой дашборд</h2>
                </div>
                <p>Покупатель уже решает задачу через Excel, карты, агентства или внутреннего аналитика. Продукт должен выигрывать скоростью, повторяемостью и конкретным выводом.</p>
            </div>
            <div class="rd-table">
                <div class="rd-table-row header">
                    <div class="rd-table-cell">Альтернатива</div>
                    <div class="rd-table-cell">Что дает</div>
                    <div class="rd-table-cell">Ограничение</div>
                    <div class="rd-table-cell">Как отличается RealDemand</div>
                </div>
                <div class="rd-table-row">
                    <div class="rd-table-cell"><strong>Ручная аналитика</strong>Excel, Wordstat, 2GIS, карты, отзывы</div>
                    <div class="rd-table-cell">Низкий порог доступа к источникам</div>
                    <div class="rd-table-cell">Долго, трудно стандартизировать, нет единой логики вывода</div>
                    <div class="rd-table-cell">Собирает сигналы в индекс, карту районов и отчет с рисками</div>
                </div>
                <div class="rd-table-row">
                    <div class="rd-table-cell"><strong>Исследовательские агентства</strong>Кастомный отчет под задачу</div>
                    <div class="rd-table-cell">Глубокая экспертиза и интервью</div>
                    <div class="rd-table-cell">Дорого и медленно для регулярных быстрых проверок</div>
                    <div class="rd-table-cell">Дает первичный вывод за меньший чек и подходит для повторных сценариев</div>
                </div>
                <div class="rd-table-row">
                    <div class="rd-table-cell"><strong>BI и рыночные базы</strong>Дашборды и наборы данных</div>
                    <div class="rd-table-cell">Много данных и визуализаций</div>
                    <div class="rd-table-cell">Не всегда доводят до решения “где запускать пилот”</div>
                    <div class="rd-table-cell">Фокусируется на сценарии запуска: район, бюджет, риск, источники</div>
                </div>
                <div class="rd-table-row">
                    <div class="rd-table-cell"><strong>Внутренний аналитик</strong>Сбор данных внутри компании</div>
                    <div class="rd-table-cell">Знает бизнес и контекст компании</div>
                    <div class="rd-table-cell">Не масштабируется на много городов и ниш без процессов</div>
                    <div class="rd-table-cell">Стандартизирует процесс и ускоряет подготовку решения</div>
                </div>
            </div>
        </section>
        """
    )


def render_pricing() -> None:
    html_block(
        """
        <section class="rd-section" id="economics">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Монетизация и экономика</div>
                    <h2 class="rd-section-title">Экономика строится через отчет и повторную подписку</h2>
                </div>
                <p>Разовый отчет запускает продажу без длинного внедрения. Подписка подходит командам, которые регулярно выбирают новые районы, города или отслеживают конкурентов.</p>
            </div>
            <div class="rd-price-grid">
                <div class="rd-price"><h3>Разовый отчет</h3><div class="rd-price-value">&nbsp;₽</div><div class="rd-price-sub">за 1 исследование</div><ul><li>Один город, район или категория</li><li>Короткий отчет с источниками и рисками</li><li>Низкий вход для первого платного пилота</li></ul><div class="rd-badge">Вход в продукт</div></div>
                <div class="rd-price"><h3>SaaS Start</h3><div class="rd-price-value">14&nbsp;900&nbsp;₽</div><div class="rd-price-sub">в месяц</div><ul><li>10 анализов в месяц</li><li>1 пользователь</li><li>Базовый индекс сферы</li><li>Экспорт отчета</li></ul><div class="rd-badge">Малые команды</div></div>
                <div class="rd-price featured"><div class="rd-badge">Основная модель</div><h3>SaaS Growth</h3><div class="rd-price-value">29&nbsp;900&nbsp;₽</div><div class="rd-price-sub">в месяц</div><ul><li>30 анализов в месяц</li><li>3 пользователя</li><li>Карта спроса и конкурентов</li><li>Еженедельный мониторинг отзывов</li></ul><div class="rd-badge">Повторяемая выручка</div></div>
                <div class="rd-price"><h3>API / Поток данных</h3><div class="rd-price-value">от&nbsp;49&nbsp;900&nbsp;₽</div><div class="rd-price-sub">в месяц</div><ul><li>Интеграция с BI/CRM</li><li>Доступ к индексам и данным</li><li>Еженедельное обновление данных</li></ul><div class="rd-badge">Для зрелых команд</div></div>
                <div class="rd-price"><h3>Внедрение</h3><div class="rd-price-value">от&nbsp;249&nbsp;900&nbsp;₽</div><div class="rd-price-sub">настройка + поддержка</div><ul><li>Внутренний контур</li><li>Источники под компанию</li><li>Роли, доступы и безопасность</li></ul><div class="rd-badge">Для сетей</div></div>
            </div>
            <div class="rd-unit-model">
                <div><span>Старт продаж</span><strong>2-3 оплаченных отчета</strong></div>
                <div><span>Переход в MRR</span><strong>3-5 команд на подписке</strong></div>
                <div><span>Метрики</span><strong>CAC, маржа и повтор</strong></div>
                <div><span>Качество роста</span><strong>повторные запросы и маржа</strong></div>
            </div>
        </section>
        """
    )


def render_faq_and_final() -> None:
    html_block(
        """
        <section class="rd-section" id="investment">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Бизнес-логика</div>
                    <h2 class="rd-section-title">Путь от разового отчета к регулярной выручке</h2>
                </div>
                <p>У продукта есть прикладная B2B-задача, понятный покупатель, цена входа и сценарий расширения: новые города, районы, вертикали и мониторинг конкурентов.</p>
            </div>
            <div class="rd-investor-grid">
                <div class="rd-investor-left">
                    <div class="rd-investor-card featured">
                        <span>Ключевая логика</span>
                        <h3>Разовый отчет снижает барьер покупки, подписка монетизирует повторные запуски</h3>
                        <p>Сначала клиент покупает решение по одной локации, затем использует сервис для новых рынков и регулярного мониторинга.</p>
                    </div>
                    <div class="rd-investor-card">
                        <span>Первые продажи</span>
                        <h3>2-3 отчета без скидки</h3>
                        <p>Первые сделки показывают спрос на платный вход и помогают настроить пакет, источники и аргументы для подписки.</p>
                    </div>
                </div>
                <div class="rd-stacked-cards">
                    <div class="rd-investor-card"><span>Механика роста</span><h3>Платный вход и повторная задача</h3><p>Клиент оплачивает отчет, использует вывод в решении и возвращается с новой локацией.</p></div>
                    <div class="rd-investor-card"><span>Переход в подписку</span><h3>Отчет становится входом в SaaS</h3><p>Регулярные команды получают больше расчетов, мониторинг конкурентов и общий кабинет для команды.</p></div>
                    <div class="rd-investor-card"><span>Контроль качества</span><h3>Автоматизация расчета и прозрачные источники</h3><p>Стабильный расчет и понятные источники поддерживают маржу и доверие клиента.</p></div>
                </div>
            </div>
        </section>
        <section class="rd-section" id="faq">
            <div class="rd-faq-grid">
                <div>
                    <div class="rd-eyebrow">Ключевые вопросы</div>
                    <div class="rd-section-head" style="display:block; margin-bottom:0;">
                        <h2 class="rd-section-title">Ключевые вопросы по проекту</h2>
                    </div>
                </div>
                <div class="rd-faq-list">
                    <details class="rd-faq" open><summary>Кто целевая аудитория?</summary><p>Команды, которые отвечают за запуск в новом городе, районе или нише: владельцы МСБ, франчайзи, продуктовые команды, команды роста и маркетинг локальных сервисов.</p></details>
                    <details class="rd-faq"><summary>В чем отличие продукта?</summary><p>RealDemand связывает данные с решением: индекс пилота, район старта, риск бюджета, источники и ограничения.</p></details>
                    <details class="rd-faq"><summary>Кто конкуренты?</summary><p>Ручная аналитика, исследовательские агентства, BI/рыночные базы и внутренние аналитики. Отличие - фокус на быстром сценарии запуска.</p></details>
                    <details class="rd-faq"><summary>Как зарабатывает продукт?</summary><p>Разовый отчет за &nbsp;₽, SaaS-подписки 14&nbsp;900/29&nbsp;900&nbsp;₽ в месяц, API от 49&nbsp;900&nbsp;₽ и внедрение от 249&nbsp;900&nbsp;₽.</p></details>
                    <details class="rd-faq"><summary>Какие метрики показывают прогресс?</summary><p>Оплаченные отчеты, повторные запросы, переход в подписку, маржа отчета и стоимость привлечения клиента.</p></details>
                    <details class="rd-faq"><summary>Какая ближайшая цель продаж?</summary><p>2-3 оплаченных отчета и 1-2 повторных запроса от тех же или похожих клиентов.</p></details>
                    <details class="rd-faq"><summary>Какой MVP?</summary><p>Веб-кабинет на 1-2 вертикалях и 3-5 городах: вводные, индекс, карта районов, объяснение факторов и экспорт короткого отчета.</p></details>
                </div>
            </div>
            <div class="rd-final">
                <div>
                    <div class="rd-eyebrow" style="background:#fff;">Финальный вывод</div>
                    <h2 class="rd-section-title">RealDemand упакован как B2B-продукт с платным входом</h2>
                    <p>Следующий шаг — первые отчеты, сбор обратной связи и перевод регулярных сценариев в подписку.</p>
                </div>
                <a class="rd-btn" href="#top">Вернуться к началу</a>
            </div>
            <div class="rd-footer-nav">
                <a class="rd-brand" href="#top"><span class="rd-mark"></span><span>RealDemand</span></a>
                <div class="rd-footer-links">
                    <a href="#market">Рынок</a>
                    <a href="#audience">Аудитория</a>
                    <a href="#problem">Проблема</a>
                    <a href="#solution">Решение</a>
                    <a href="#competition">Конкуренты</a>
                    <a href="#economics">Экономика</a>
                </div>
                <a class="rd-btn secondary" href="#investment">Бизнес-логика</a>
            </div>
        </section>
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="RealDemand - обзор продукта",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    render_css()
    render_nav()
    render_hero()
    render_market_and_audience()
    render_problem()
    render_solution_logic()
    render_interactive_demo()
    render_sources_and_cases()
    render_competition()
    render_pricing()
    render_faq_and_final()


if __name__ == "__main__":
    main()
