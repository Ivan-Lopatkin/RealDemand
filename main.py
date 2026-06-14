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
            "status": "проверить спрос",
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
            "status": "проверить спрос",
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
            "status": "проверить спрос",
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
            "status": "проверить спрос",
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
        return "Тестировать осторожно", "Гипотеза выглядит рабочей, но нужно ограничить бюджет и район запуска."
    return "Доработать гипотезу", "Сигналы пока неоднозначные: стоит сменить район, сегмент или формат предложения."


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

        .stMarkdown {
            margin: 0;
        }

        .stMarkdown a.anchor-link {
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
            padding: 54px 0;
            border-top: 1px solid rgba(16, 24, 40, 0.08);
        }

        .rd-section:first-of-type {
            border-top: 0;
        }

        .rd-hero {
            position: relative;
            min-height: min(760px, calc(100vh - 108px));
            padding: 48px 0 70px;
            overflow: hidden;
        }

        .rd-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            z-index: 2;
            pointer-events: none;
            background:
                linear-gradient(90deg, rgba(245, 247, 251, 1) 0%, rgba(245, 247, 251, 0.98) 44%, rgba(245, 247, 251, 0.84) 61%, rgba(245, 247, 251, 0.22) 100%),
                linear-gradient(0deg, rgba(245, 247, 251, 1) 0%, rgba(245, 247, 251, 0) 16%);
        }

        .rd-hero > div:first-child {
            position: relative;
            z-index: 3;
            max-width: 800px;
            padding: 28px 0;
        }

        .rd-hero > div:nth-child(2) {
            position: absolute;
            top: 26px;
            right: -210px;
            bottom: 34px;
            left: 54%;
            z-index: 1;
            display: flex;
            align-items: center;
            pointer-events: none;
        }

        .rd-hero > div:nth-child(2) .rd-product-shell {
            width: 100%;
            opacity: .82;
            transform: perspective(1100px) rotateY(-7deg) rotateX(2deg) scale(.96);
            transform-origin: center right;
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
            min-height: 112px;
            padding: 14px;
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

        .rd-product-shell {
            overflow: hidden;
            border: 1px solid #cfd8e6;
            border-radius: var(--rd-radius);
            background: #f8fafc;
            box-shadow: var(--rd-shadow);
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
            display: flex;
            justify-content: space-between;
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

        .rd-source-item span:last-child {
            color: #0f8f59;
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
            height: 40px;
        }

        .st-key-rd_map_panel,
        .st-key-rd_summary_panel {
            margin-top: 0 !important;
        }

        .st-key-rd_map_panel [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-rd_summary_panel [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 18px 18px 24px !important;
            border: 1px solid var(--rd-line) !important;
            border-radius: var(--rd-radius) !important;
            background: #fff !important;
            box-shadow: var(--rd-shadow) !important;
        }

        .st-key-rd_map_panel [data-testid="stVerticalBlock"],
        .st-key-rd_summary_panel [data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }

        .st-key-rd_map_panel .rd-map-legend,
        .st-key-rd_summary_panel .rd-source-list {
            margin-bottom: 12px;
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
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
        }

        .rd-card p {
            margin: 0;
            color: #475467;
            font-size: 14px;
            line-height: 1.46;
        }

        .rd-problem-section {
            padding-top: 48px;
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
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
        }

        .rd-problem-item p {
            margin: 0;
            color: #475467;
            font-size: 14px;
            line-height: 1.45;
        }

        .rd-native-panel {
            margin: 10px 0 0;
            padding: 18px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: var(--rd-shadow);
        }

        .rd-native-panel h3 {
            margin: 0 0 8px;
            color: var(--rd-ink);
            font-size: var(--rd-subtitle);
            line-height: 1.1;
            font-weight: 900;
        }

        .rd-native-panel p {
            margin: 0 0 18px;
            color: var(--rd-muted);
            font-size: 15px;
            line-height: 1.5;
        }

        .rd-demo-brief {
            display: grid;
            grid-template-columns: minmax(240px, .72fr) minmax(0, 1.28fr);
            gap: 12px;
            align-items: stretch;
            margin: 8px 0 18px;
        }

        .rd-demo-card,
        .rd-demo-note {
            padding: 16px;
            border: 1px solid var(--rd-line);
            border-radius: var(--rd-radius);
            background: #fff;
            box-shadow: 0 12px 30px rgba(16, 24, 40, 0.07);
        }

        .rd-demo-card h3,
        .rd-demo-note h3 {
            margin: 0 0 8px;
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
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
            gap: 10px;
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
            min-height: 116px;
            padding: 14px;
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
            font-size: 28px;
            line-height: 1;
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
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .rd-price {
            min-height: 335px;
            display: flex;
            flex-direction: column;
            padding: 17px;
        }

        .rd-price.featured {
            border-color: #f2c200;
            background: #fff8d6;
            box-shadow: 0 18px 42px rgba(250, 204, 21, 0.22);
        }

        .rd-badge {
            align-self: flex-start;
            margin-bottom: 11px;
            padding: 5px 8px;
            border-radius: var(--rd-radius);
            background: var(--rd-ink);
            color: #fff;
            font-size: 11px;
            font-weight: 850;
        }

        .rd-price h3 {
            margin: 0 0 9px;
            color: var(--rd-ink);
            font-size: var(--rd-subtitle);
            line-height: 1.1;
            font-weight: 900;
        }

        .rd-price-value {
            margin-bottom: 5px;
            color: var(--rd-ink);
            font-size: clamp(26px, 2.3vw, 31px);
            line-height: 1;
            font-weight: 930;
            white-space: nowrap;
        }

        .rd-price-sub {
            margin-bottom: 14px;
            color: var(--rd-muted);
            font-size: 13px;
            font-weight: 760;
        }

        .rd-price ul {
            flex: 1;
            margin: 0 0 16px;
            padding-left: 18px;
            color: #475467;
            font-size: 13px;
            line-height: 1.45;
        }

        .rd-price li {
            margin-bottom: 7px;
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
            color: var(--rd-ink);
            font-size: var(--rd-card-title);
            line-height: 1.12;
            font-weight: 900;
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
            .rd-card-grid-4 {
                grid-template-columns: repeat(2, 1fr);
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
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 14px;
                padding-right: 14px;
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
                font-size: 42px;
                line-height: 1.06;
            }

            .rd-hero {
                min-height: auto;
                padding: 30px 0 42px;
            }

            .rd-hero::before {
                background: linear-gradient(180deg, rgba(245, 247, 251, 0.98), rgba(245, 247, 251, 0.82));
            }

            .rd-hero > div:first-child {
                padding: 0;
            }

            .rd-hero > div:nth-child(2) {
                position: relative;
                inset: auto;
                z-index: 3;
                margin-top: 24px;
                pointer-events: auto;
            }

            .rd-hero > div:nth-child(2) .rd-product-shell {
                opacity: 1;
                transform: none;
            }

            .rd-proof-grid,
            .rd-card-grid-3,
            .rd-card-grid-4,
            .rd-price-grid,
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

            .rd-compare-cell:first-child {
                border-right: 0;
                border-bottom: 1px solid var(--rd-line);
            }

            .rd-window-bar,
            .rd-topline,
            .rd-dashboard-title {
                align-items: flex-start;
                flex-direction: column;
            }

            .rd-demo-results-gap {
                height: 24px;
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
                <a href="#problem">Проблема</a>
                <a href="#demo">Демо</a>
                <a href="#product">Продукт</a>
                <a href="#pricing">Форматы</a>
                <a href="#faq">FAQ</a>
            </div>
            <a class="rd-btn" href="mailto:demo@realdemand.ai?subject=Запрос демо RealDemand">Запросить демо</a>
        </nav>
        """
    )


def render_hero() -> None:
    html_block(
        """
        <section class="rd-hero" id="top">
            <div>
                <div class="rd-eyebrow">Проверка рынка перед запуском</div>
                <h1 class="rd-title-xl">Проверка рынка перед запуском в новом городе или районе</h1>
                <p class="rd-lead">RealDemand помогает решить прикладной вопрос: стоит ли запускать пилот клининга в Казани и с какого района начинать.</p>
                <p class="rd-note">Пользователь задает город, сферу и бюджет. Сервис считает спрос, конкурентов, отзывы и уверенность данных, а затем отдает рабочий вывод: первый район, ограничения бюджета, риски и источники для проверки.</p>
                <div class="rd-actions">
                    <a class="rd-btn" href="#demo">Посчитать сценарий</a>
                    <a class="rd-btn secondary" href="#product">Посмотреть интерфейс</a>
                </div>
                <div class="rd-proof-grid">
                    <div class="rd-proof"><strong>Вводные</strong><span>Казань, домашние сервисы, бюджет 350 тыс. ₽ и цель пилота.</span></div>
                    <div class="rd-proof"><strong>Расчет</strong><span>Спрос, конкуренты, отзывы, районы и уверенность источников.</span></div>
                    <div class="rd-proof"><strong>Вывод</strong><span>Ново-Савиновский для старта, риски бюджета и отчет для команды.</span></div>
                </div>
            </div>
            <div>
                <div class="rd-product-shell">
                    <div class="rd-window-bar">
                        <div class="rd-chip-row">
                            <div class="rd-dots"><span></span><span></span><span></span></div>
                            <div class="rd-window-title">RealDemand / Обзор рынка</div>
                        </div>
                        <div class="rd-chip-row">
                            <span class="rd-chip">Казань</span>
                            <span class="rd-chip">Домашние сервисы</span>
                            <span class="rd-chip dark">Пилот</span>
                        </div>
                    </div>
                    <div class="rd-dashboard">
                        <aside class="rd-sidebar">
                            <div class="rd-side-brand"><span class="rd-side-dot"></span>RealDemand</div>
                            <div class="rd-side-label">Рабочая область</div>
                            <div class="rd-side-item active"><span>Обзор рынка</span><span>01</span></div>
                            <div class="rd-side-item"><span>География спроса</span><span>02</span></div>
                            <div class="rd-side-item"><span>Конкуренты</span><span>03</span></div>
                            <div class="rd-side-item"><span>Сценарии</span><span>04</span></div>
                            <div class="rd-side-label">Источники</div>
                            <div class="rd-side-item active"><span>Статистика</span></div>
                            <div class="rd-side-item active"><span>Поиск</span></div>
                            <div class="rd-side-item active"><span>Сеть</span></div>
                        </aside>
                        <main class="rd-main">
                            <div class="rd-topline">
                                <div class="rd-breadcrumbs">Проекты / Домашние сервисы / Казань</div>
                                <div class="rd-mini-actions">
                                    <span class="rd-mini-button">Сравнить</span>
                                    <span class="rd-mini-button">Источники</span>
                                    <span class="rd-mini-button primary">Отчет</span>
                                </div>
                            </div>
                            <div class="rd-dashboard-title">
                                <div>
                                    <h2>Пилот клининга в Казани</h2>
                                    <p>Дефолтный сценарий лендинга: домашние сервисы, бюджет 350 тыс. ₽, выбор первого района на 6-8 недель.</p>
                                </div>
                                <div class="rd-health">
                                    <div class="rd-health-label"><span>Уверенность</span><span>84%</span></div>
                                    <div class="rd-health-bar"><span style="width:84%"></span></div>
                                </div>
                            </div>
                            <div class="rd-kpi-grid">
                                <div class="rd-kpi"><div class="rd-kpi-label">Индекс пилота</div><div class="rd-kpi-value">67</div><div class="rd-kpi-note">Тестировать осторожно</div></div>
                                <div class="rd-kpi"><div class="rd-kpi-label">Спрос</div><div class="rd-kpi-value">+24%</div><div class="rd-kpi-note">6 месяцев</div></div>
                                <div class="rd-kpi"><div class="rd-kpi-label">Конкуренция</div><div class="rd-kpi-value">Средняя</div><div class="rd-kpi-note">56/100 по плотности</div></div>
                                <div class="rd-kpi"><div class="rd-kpi-label">Отзывы и обсуждения</div><div class="rd-kpi-value">+31%</div><div class="rd-kpi-note">Обсуждения растут</div></div>
                            </div>
                            <div class="rd-grid-2">
                                <div class="rd-panel">
                                    <div class="rd-panel-title">Динамика спроса <span>12 месяцев</span></div>
                                    <div class="rd-line-chart"><div class="rd-axis"><span>Янв</span><span>Мар</span><span>Май</span><span>Июл</span><span>Сен</span><span>Дек</span></div></div>
                                </div>
                                <div class="rd-panel">
                                    <div class="rd-panel-title">Краткий вывод <span>для команды</span></div>
                                    <div class="rd-summary"><strong>Тестировать осторожно</strong><p>Начать с Ново-Савиновского района, Советский добавить вторым. Центр города не брать в первый пилот из-за стоимости входа.</p></div>
                                    <div class="rd-tag-row"><span>Ново-Савиновский старт</span><span>350 тыс. ₽</span><span>6-8 недель</span><span>Центр дорогой</span></div>
                                </div>
                            </div>
                        </main>
                    </div>
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


def render_interactive_demo() -> None:
    html_block(
        """
        <section class="rd-section" id="demo">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Демо-сценарий</div>
                    <h2 class="rd-section-title">Проверьте тот же сценарий на своих вводных</h2>
                </div>
                <p>Ниже тот же расчет, что на экране продукта: город, сфера и бюджет превращаются в индекс, район старта, риски и список проверяемых источников.</p>
            </div>
            <div class="rd-demo-brief">
                <div class="rd-demo-card">
                    <h3>Сценарий: запуск клининга</h3>
                    <p>Базовый пример: Казань, домашние сервисы, 350 тыс. ₽. Меняйте вводные и смотрите, как сервис пересобирает решение.</p>
                </div>
                <div class="rd-demo-note">
                    <div><span>1. Вводные</span><strong>город, сфера, бюджет</strong></div>
                    <div><span>2. Расчет</span><strong>спрос, конкуренты, отзывы</strong></div>
                    <div><span>3. География</span><strong>район старта и второй этап</strong></div>
                    <div><span>4. Вывод</span><strong>риск, ограничение, отчет</strong></div>
                </div>
            </div>
        </section>
        """
    )

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

    st.progress(score / 100, text=f"Индекс привлекательности: {score}/100")

    html_block(
        f"""
            <div class="rd-native-panel">
                <div class="rd-decision-grid">
                    <div class="rd-decision-card"><span>Итог сервиса</span><strong>{escape(launch_label)}</strong><em>{escape(sector.label)}</em></div>
                    <div class="rd-decision-card"><span>Первый район</span><strong>{escape(region.district)}</strong><em>по карте спроса</em></div>
                    <div class="rd-decision-card"><span>Спрос</span><strong>+{region.demand_growth}%</strong><em>по запросам и отзывам</em></div>
                    <div class="rd-decision-card"><span>Главный риск</span><strong>{escape(competition_label)}</strong><em>{escape(sector.weak_spot.lower())}</em></div>
                </div>
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
                    <div class="rd-panel-title">Вывод для команды <span>демо-расчет</span></div>
                    <div class="rd-summary"><strong>{escape(launch_label)}</strong><p>Первый тест: {escape(region.district)} район. {escape(launch_note)} Слабое место рынка: {escape(sector.weak_spot.lower())}.</p></div>
                    <div class="rd-tag-row">
                        <span>Отзывы и обсуждения +{region.social_growth}%</span>
                        <span>Бюджет {budget} тыс. ₽</span>
                        <span>{escape(region.district)}</span>
                        <span>{escape(sector_name)}</span>
                    </div>
                    <div class="rd-source-list" style="margin-top:14px;">
                        <div class="rd-source-item"><span>Район старта</span><span>{escape(region.district)}</span></div>
                        <div class="rd-source-item"><span>Сигнал спроса</span><span>+{region.demand_growth}%</span></div>
                        <div class="rd-source-item"><span>Плотность конкурентов</span><span>{escape(competition_label.lower())}</span></div>
                        <div class="rd-source-item"><span>Что проверить руками</span><span>{escape(sector.weak_spot.lower())}</span></div>
                    </div>
                """
            )


def render_product() -> None:
    html_block(
        """
        <section class="rd-section" id="product">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Продукт</div>
                    <h2 class="rd-section-title">Что делает сервис в этом сценарии</h2>
                </div>
                <p>Скрин ниже показывает тот же сценарий, что демо: сервис принимает вводные, считает факторы, выбирает район для пилота и собирает аргументы для решения команды.</p>
            </div>
            <div class="rd-product-shell">
                <div class="rd-window-bar">
                    <div class="rd-chip-row">
                        <div class="rd-dots"><span></span><span></span><span></span></div>
                        <div class="rd-window-title">RealDemand / Сценарий пилота</div>
                    </div>
                    <div class="rd-chip-row">
                        <span class="rd-chip">Казань</span>
                        <span class="rd-chip">Домашние сервисы</span>
                        <span class="rd-chip dark">350 тыс. ₽</span>
                    </div>
                </div>
                <div class="rd-dashboard">
                    <aside class="rd-sidebar">
                        <div class="rd-side-brand"><span class="rd-side-dot"></span>RealDemand</div>
                        <div class="rd-side-label">Рабочая область</div>
                        <div class="rd-side-item active"><span>Сценарий пилота</span><span>01</span></div>
                        <div class="rd-side-item active"><span>Карта районов</span><span>02</span></div>
                        <div class="rd-side-item"><span>Конкуренты</span><span>03</span></div>
                        <div class="rd-side-item"><span>Отчет</span><span>04</span></div>
                        <div class="rd-side-label">Источники</div>
                        <div class="rd-side-item active"><span>Статистика</span></div>
                        <div class="rd-side-item active"><span>Поиск</span></div>
                        <div class="rd-side-item active"><span>Отзывы</span></div>
                    </aside>
                    <main class="rd-main">
                        <div class="rd-topline">
                            <div class="rd-breadcrumbs">Проекты / Домашние сервисы / Казань</div>
                            <div class="rd-mini-actions">
                                <span class="rd-mini-button">Источники</span>
                                <span class="rd-mini-button">Карта</span>
                                <span class="rd-mini-button primary">Отчет</span>
                            </div>
                        </div>
                        <div class="rd-dashboard-title">
                            <div>
                                <h2>Пилот клининга в Казани</h2>
                                <p>Задача: понять, стоит ли запускать предложение и какой район взять первым при бюджете 350 тыс. ₽.</p>
                            </div>
                            <div class="rd-health">
                                <div class="rd-health-label"><span>Уверенность данных</span><span>84%</span></div>
                                <div class="rd-health-bar"><span style="width:84%"></span></div>
                            </div>
                        </div>
                        <div class="rd-kpi-grid">
                            <div class="rd-kpi"><div class="rd-kpi-label">Индекс пилота</div><div class="rd-kpi-value">67</div><div class="rd-kpi-note">Тестировать осторожно</div></div>
                            <div class="rd-kpi"><div class="rd-kpi-label">Спрос</div><div class="rd-kpi-value">+24%</div><div class="rd-kpi-note">запросы и отзывы</div></div>
                            <div class="rd-kpi"><div class="rd-kpi-label">Конкуренция</div><div class="rd-kpi-value">Средняя</div><div class="rd-kpi-note">56/100 по плотности</div></div>
                            <div class="rd-kpi"><div class="rd-kpi-label">Первый район</div><div class="rd-kpi-value small">Ново-Савиновский</div><div class="rd-kpi-note">старт пилота</div></div>
                        </div>
                        <div class="rd-grid-2">
                            <div class="rd-panel">
                                <div class="rd-panel-title">Вводные пользователя <span>что выбрано</span></div>
                                <div class="rd-source-list">
                                    <div class="rd-source-item"><span>Город</span><span>Казань</span></div>
                                    <div class="rd-source-item"><span>Сфера</span><span>Домашние сервисы</span></div>
                                    <div class="rd-source-item"><span>Бюджет пилота</span><span>350 тыс. ₽</span></div>
                                    <div class="rd-source-item"><span>Задача</span><span>выбрать район старта</span></div>
                                </div>
                            </div>
                            <div class="rd-panel">
                                <div class="rd-panel-title">Вывод сервиса <span>для обсуждения</span></div>
                                <div class="rd-summary"><strong>Тестировать осторожно</strong><p>Начать с Ново-Савиновского района. Советский оставить вторым, центр не брать в первый пилот из-за дорогого входа.</p></div>
                                <div class="rd-tag-row"><span>Ново-Савиновский старт</span><span>Советский вторым</span><span>центр дорогой</span><span>6-8 недель</span></div>
                            </div>
                        </div>
                        <div class="rd-grid-3">
                            <div class="rd-panel"><div class="rd-panel-title">География</div><div class="rd-source-list"><div class="rd-source-item"><span>Ново-Савиновский</span><span>старт</span></div><div class="rd-source-item"><span>Советский</span><span>второй район</span></div><div class="rd-source-item"><span>Вахитовский центр</span><span>дорого</span></div></div></div>
                            <div class="rd-panel"><div class="rd-panel-title">Почему так</div><div class="rd-source-list"><div class="rd-source-item"><span>Поисковый спрос</span><span>+24%</span></div><div class="rd-source-item"><span>Отзывы и обсуждения</span><span>+31%</span></div><div class="rd-source-item"><span>Плотность конкурентов</span><span>56/100</span></div></div></div>
                            <div class="rd-panel"><div class="rd-panel-title">Что получает команда</div><div class="rd-source-list"><div class="rd-source-item"><span>Риск бюджета</span><span>ограничить район</span></div><div class="rd-source-item"><span>Проверка руками</span><span>скорость отклика</span></div><div class="rd-source-item"><span>Экспорт</span><span>отчет с источниками</span></div></div></div>
                        </div>
                    </main>
                </div>
            </div>
            <div class="rd-user-flow">
                <div class="rd-user-flow-head">
                    <h3>Какие задачи закрывает сервис</h3>
                    <p>Один расчет нужен не ради красивого индекса. Он помогает команде быстрее договориться, где запускать пилот, что проверить руками и какие ограничения поставить бюджету.</p>
	                </div>
	                <div class="rd-flow-grid">
                    <div class="rd-flow-step"><span>Задача 01</span><strong>Проверить гипотезу</strong><p>Понять, хватает ли спроса для пилота в выбранном городе и сфере.</p></div>
                    <div class="rd-flow-step"><span>Задача 02</span><strong>Выбрать район старта</strong><p>Сравнить районы и не тратить первый бюджет на слишком дорогую точку входа.</p></div>
                    <div class="rd-flow-step"><span>Задача 03</span><strong>Ограничить риск бюджета</strong><p>Увидеть конкуренцию, слабые места рынка и условия, которые нужно проверить руками.</p></div>
                    <div class="rd-flow-step"><span>Задача 04</span><strong>Собрать решение</strong><p>Получить короткий вывод с источниками, рисками, районом и следующим шагом.</p></div>
	                </div>
            </div>
        </section>
        """
    )


def render_sources_and_cases() -> None:
    html_block(
        """
        <section class="rd-section" id="sources">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Данные</div>
                    <h2 class="rd-section-title">Каким данным можно доверять</h2>
                </div>
                <p>Для одного рынка хватает статистики и карт, для другого нужны отзывы и поисковая динамика. Если источников мало или они спорят между собой, это показывается как риск.</p>
            </div>
            <div class="rd-card-grid-4 rd-compact-grid">
                <div class="rd-card"><div class="num">Статистика</div><h3>Размер рынка</h3><p>Население, доходы, занятость, районы роста и количество компаний в категории.</p></div>
                <div class="rd-card blue"><div class="num">Спрос</div><h3>Что ищут люди</h3><p>Запросы, сезонность, темы в отзывах и признаки регулярной потребности.</p></div>
                <div class="rd-card amber"><div class="num">Отзывы</div><h3>Где болит</h3><p>Жалобы на скорость, график, цену и качество помогают найти незакрытый сценарий.</p></div>
                <div class="rd-card green"><div class="num">Конкуренты</div><h3>Кто мешает входу</h3><p>Карты, сайты, выдача, акции и частота отзывов показывают плотность игроков.</p></div>
            </div>
        </section>
        <section class="rd-section" id="cases">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Сценарии</div>
                    <h2 class="rd-section-title">Для каких решений использовать</h2>
                </div>
                <p>Лендинг показывает один пример, но продукт полезен в нескольких повторяющихся задачах: новый город, новая ниша, мониторинг и отчет для обсуждения.</p>
            </div>
            <div class="rd-card-grid-4 rd-compact-grid">
                <div class="rd-card"><div class="num">Сценарий 01</div><h3>Новый город</h3><p>Сравнить 3-5 городов и выбрать, где начинать пилот дешевле и понятнее.</p></div>
                <div class="rd-card"><div class="num">Сценарий 02</div><h3>Новая ниша</h3><p>Проверить соседние категории: клининг, ремонт, детские кружки, фитнес-студии.</p></div>
                <div class="rd-card"><div class="num">Сценарий 03</div><h3>Мониторинг</h3><p>Раз в неделю видеть новые отзывы, акции конкурентов и всплески поискового спроса.</p></div>
                <div class="rd-card"><div class="num">Сценарий 04</div><h3>Отчет</h3><p>Собрать короткий документ: вводные, источники, риски, рекомендация и следующий шаг.</p></div>
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
                    <h2 class="rd-section-title">На выходе не обещание успеха, а план безопасного пилота</h2>
                </div>
                <p>RealDemand не заменяет решение команды. Он помогает быстро увидеть, где гипотеза выглядит сильной, где источники слабые и что нужно проверить в первые недели.</p>
            </div>
            <div class="rd-compare">
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>3-8 часов на ручной сбор ссылок и таблиц</div><div class="rd-compare-cell"><strong>Стало</strong>15-30 минут до первой версии гипотезы</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>“в Казани вроде есть спрос”</div><div class="rd-compare-cell"><strong>Стало</strong>“начать с Савиновского района, центр отложить”</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>спор о том, каким источникам верить</div><div class="rd-compare-cell"><strong>Стало</strong>видно, где данные сходятся, а где нужен ручной звонок или проверка</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>решение без понятного критерия успеха</div><div class="rd-compare-cell"><strong>Стало</strong>пилот на 6-8 недель с метриками спроса и стоимости заявки</div></div>
            </div>
        </section>
        """
    )


def render_pricing() -> None:
    html_block(
        """
        <section class="rd-section" id="pricing">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Форматы</div>
                    <h2 class="rd-section-title">Можно купить один отчет или подключить регулярную проверку рынков</h2>
                </div>
                <p>Если нужно проверить одну идею, подойдет отчет. Если команда постоянно выбирает регионы, ниши и конкурентов, выгоднее подписка или API.</p>
            </div>
            <div class="rd-price-grid">
                <div class="rd-price"><h3>Разовый отчет</h3><div class="rd-price-value">19 900 ₽</div><div class="rd-price-sub">за 1 исследование</div><ul><li>Один город, район или категория</li><li>PDF/Word с источниками и рисками</li><li>Подходит для защиты пилота</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=Разовый отчет">Заказать</a></div>
                <div class="rd-price"><h3>SaaS Start</h3><div class="rd-price-value">14 900 ₽</div><div class="rd-price-sub">в месяц</div><ul><li>10 анализов в месяц</li><li>1 пользователь</li><li>Базовый индекс сферы</li><li>Экспорт отчета</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=SaaS Start">Начать</a></div>
                <div class="rd-price featured"><div class="rd-badge">Популярно</div><h3>SaaS Growth</h3><div class="rd-price-value">29 900 ₽</div><div class="rd-price-sub">в месяц</div><ul><li>30 анализов в месяц</li><li>3 пользователя</li><li>Карта спроса и конкурентов</li><li>Еженедельный мониторинг отзывов</li></ul><a class="rd-btn" href="mailto:demo@realdemand.ai?subject=SaaS Growth">Запросить демо</a></div>
                <div class="rd-price"><h3>API / Поток данных</h3><div class="rd-price-value">от 49 900 ₽</div><div class="rd-price-sub">в месяц</div><ul><li>Интеграция с BI/CRM</li><li>Доступ к индексам и данным</li><li>Еженедельное обновление данных</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=API">Обсудить API</a></div>
                <div class="rd-price"><h3>Коробка</h3><div class="rd-price-value">от 249 900 ₽</div><div class="rd-price-sub">внедрение + поддержка</div><ul><li>Внутренний контур</li><li>Источники под компанию</li><li>Роли, доступы и безопасность</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=Коробка">Условия</a></div>
            </div>
        </section>
        """
    )


def render_faq_and_final() -> None:
    html_block(
        """
        <section class="rd-section" id="faq">
            <div class="rd-faq-grid">
                <div>
                    <div class="rd-eyebrow">FAQ</div>
                    <div class="rd-section-head" style="display:block; margin-bottom:0;">
                        <h2 class="rd-section-title">Ответы на частые вопросы</h2>
                    </div>
                </div>
                <div class="rd-faq-list">
                    <details class="rd-faq" open><summary>Откуда берутся данные?</summary><p>Из открытых источников под задачу: статистика региона, поисковая динамика, карты, сайты конкурентов, отзывы, соцсети и медиа.</p></details>
                    <details class="rd-faq"><summary>Как сервис не превращается в «магический ответ»?</summary><p>Каждый вывод связан с источниками и весами факторов. Если данных мало, отчет не делает вид, что все ясно, а показывает слабое место.</p></details>
                    <details class="rd-faq"><summary>Зачем смотреть отзывы и обсуждения?</summary><p>Там раньше видно бытовые проблемы: долго отвечают, нет вечернего выезда, дорого после ремонта, сложно записаться. Это помогает найти сценарий для пилота.</p></details>
                    <details class="rd-faq"><summary>Какие есть форматы доступа?</summary><p>Доступны разовый отчет, SaaS-подписка, API с потоком данных и коробочная поставка.</p></details>
                </div>
            </div>
            <div class="rd-final">
                <div>
                    <div class="rd-eyebrow" style="background:#fff;">Следующий шаг</div>
                    <h2 class="rd-section-title">Разберите один реальный запуск до расходов на рекламу и аренду</h2>
                    <p>На демо можно взять ваш город, сферу и бюджет пилота. Покажем, какие источники нужны и где решение пока держится на слабых данных.</p>
                </div>
                <a class="rd-btn" href="mailto:demo@realdemand.ai?subject=Запрос демо RealDemand">Получить демо</a>
            </div>
            <div class="rd-footer-nav">
                <a class="rd-brand" href="#top"><span class="rd-mark"></span><span>RealDemand</span></a>
                <div class="rd-footer-links">
                    <a href="#problem">Проблема</a>
                    <a href="#demo">Демо</a>
                    <a href="#product">Продукт</a>
                    <a href="#pricing">Форматы</a>
                    <a href="#faq">FAQ</a>
                </div>
                <a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=Запрос демо RealDemand">Запросить демо</a>
            </div>
        </section>
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="RealDemand - рынок не ждет",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    render_css()
    render_nav()
    render_hero()
    render_problem()
    render_interactive_demo()
    render_product()
    render_sources_and_cases()
    render_result()
    render_pricing()
    render_faq_and_final()


if __name__ == "__main__":
    main()
