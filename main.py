from __future__ import annotations

from dataclasses import dataclass
from html import escape

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
        district="Савиновский",
        demand_growth=24,
        social_growth=31,
        note="Пилот лучше начинать с двух районов, центр оставить на второй этап.",
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
        }

        html {
            scroll-behavior: smooth;
        }

        .stApp {
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.90), rgba(245, 247, 251, 0.94) 18rem),
                var(--rd-bg);
            color: var(--rd-ink);
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

        .rd-nav {
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            min-height: 72px;
            margin: 0 -20px 22px;
            padding: 12px 20px;
            border-bottom: 1px solid rgba(16, 24, 40, 0.10);
            background: rgba(245, 247, 251, 0.92);
            backdrop-filter: blur(16px);
        }

        .rd-brand {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            color: var(--rd-ink) !important;
            text-decoration: none !important;
            font-size: 21px;
            font-weight: 900;
            letter-spacing: 0;
        }

        .rd-mark {
            width: 32px;
            height: 32px;
            display: inline-grid;
            place-items: center;
            border-radius: var(--rd-radius);
            background: conic-gradient(from 210deg, var(--rd-blue), var(--rd-green), var(--rd-amber), var(--rd-coral), var(--rd-blue));
            box-shadow: 0 10px 28px rgba(37, 99, 235, 0.22);
        }

        .rd-mark::after {
            content: "";
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #fff;
        }

        .rd-nav-links {
            display: flex;
            align-items: center;
            gap: 16px;
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
            min-height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 0 16px;
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
                linear-gradient(90deg, rgba(245, 247, 251, 0.98) 0%, rgba(245, 247, 251, 0.94) 40%, rgba(245, 247, 251, 0.62) 62%, rgba(245, 247, 251, 0.08) 100%),
                linear-gradient(0deg, rgba(245, 247, 251, 1) 0%, rgba(245, 247, 251, 0) 16%);
        }

        .rd-hero > div:first-child {
            position: relative;
            z-index: 3;
            max-width: 760px;
            padding: 28px 0;
        }

        .rd-hero > div:nth-child(2) {
            position: absolute;
            top: 26px;
            right: -92px;
            bottom: 34px;
            left: 34%;
            z-index: 1;
            display: flex;
            align-items: center;
            pointer-events: none;
        }

        .rd-hero > div:nth-child(2) .rd-product-shell {
            width: 100%;
            transform: perspective(1100px) rotateY(-7deg) rotateX(2deg);
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

        .rd-title-xl {
            max-width: 780px;
            margin: 0 0 18px;
            color: var(--rd-ink);
            font-size: clamp(48px, 7vw, 92px);
            line-height: 0.94;
            font-weight: 940;
            letter-spacing: 0;
        }

        .rd-lead {
            max-width: 690px;
            margin: 0 0 18px;
            color: #344054;
            font-size: 21px;
            line-height: 1.42;
        }

        .rd-note {
            max-width: 690px;
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
            font-size: 30px;
            line-height: 1.05;
            font-weight: 940;
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
            grid-template-columns: minmax(280px, .88fr) minmax(0, 1.12fr);
            gap: 26px;
            align-items: end;
            margin-bottom: 26px;
        }

        .rd-section-head h2 {
            margin: 0;
            color: var(--rd-ink);
            font-size: clamp(34px, 5vw, 58px);
            line-height: 1;
            font-weight: 930;
            letter-spacing: 0;
        }

        .rd-section-head p {
            margin: 0;
            color: var(--rd-muted);
            font-size: 17px;
            line-height: 1.55;
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
            min-height: 190px;
            padding: 18px;
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
            font-size: 22px;
            line-height: 1.08;
            font-weight: 900;
        }

        .rd-card p {
            margin: 0;
            color: #475467;
            font-size: 14px;
            line-height: 1.46;
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
            font-size: 26px;
            line-height: 1.1;
            font-weight: 900;
        }

        .rd-native-panel p {
            margin: 0 0 18px;
            color: var(--rd-muted);
            font-size: 15px;
            line-height: 1.5;
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
            grid-template-columns: repeat(5, minmax(0, 1fr));
        }

        .rd-price {
            min-height: 365px;
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
            font-size: 22px;
            line-height: 1.1;
            font-weight: 900;
        }

        .rd-price-value {
            margin-bottom: 5px;
            color: var(--rd-ink);
            font-size: 31px;
            line-height: 1;
            font-weight: 930;
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
            font-size: clamp(34px, 5vw, 58px);
            line-height: 1;
            font-weight: 930;
        }

        .rd-final p {
            max-width: 760px;
            margin: 0;
            color: #d0d5dd;
            font-size: 17px;
            line-height: 1.5;
        }

        .rd-footer {
            margin-top: 24px;
            padding: 20px 0 0;
            border-top: 1px solid rgba(16, 24, 40, 0.10);
            color: var(--rd-muted);
            font-size: 13px;
        }

        @media (max-width: 1120px) {
            .rd-section-head,
            .rd-faq-grid,
            .rd-final {
                grid-template-columns: 1fr;
            }

            .rd-price-grid,
            .rd-card-grid-4 {
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

            .rd-nav-links {
                display: none;
            }

            .rd-title-xl {
                font-size: 44px;
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
                transform: none;
            }

            .rd-proof-grid,
            .rd-card-grid-3,
            .rd-card-grid-4,
            .rd-price-grid,
            .rd-kpi-grid,
            .rd-grid-2,
            .rd-grid-3,
            .rd-decision-grid,
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
                <div class="rd-eyebrow">AI-сервис анализа рынка</div>
                <h1 class="rd-title-xl">Рынок не ждет. Ошибки тоже.</h1>
                <p class="rd-lead">RealDemand помогает понять, стоит ли выходить в новую сферу, регион или категорию. Быстро, наглядно и с опорой на проверяемые факты.</p>
                <p class="rd-note">Сервис сводит официальную статистику, потребительские индексы, поисковый спрос, открытые данные о конкурентах и сетевые обсуждения в один рабочий вывод: запускать, тестировать, ждать или менять гипотезу.</p>
                <div class="rd-actions">
                    <a class="rd-btn" href="#demo">Посчитать сценарий</a>
                    <a class="rd-btn secondary" href="#product">Посмотреть интерфейс</a>
                </div>
                <div class="rd-proof-grid">
                    <div class="rd-proof"><strong>Факты</strong><span>У каждого вывода есть источник, сигнал и понятная логика.</span></div>
                    <div class="rd-proof"><strong>Ранний сигнал</strong><span>Поиск и сеть показывают движение раньше отчетности.</span></div>
                    <div class="rd-proof"><strong>Решение</strong><span>Итог собирается в рекомендацию, а не в набор графиков.</span></div>
                </div>
            </div>
            <div>
                <div class="rd-product-shell">
                    <div class="rd-window-bar">
                        <div class="rd-chip-row">
                            <div class="rd-dots"><span></span><span></span><span></span></div>
                            <div class="rd-window-title">RealDemand / Market Overview</div>
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
                                    <h2>Обзор рынка</h2>
                                    <p>Сводная оценка спроса, конкуренции, регионального контекста и ранних сетевых сигналов.</p>
                                </div>
                                <div class="rd-health">
                                    <div class="rd-health-label"><span>Уверенность</span><span>84%</span></div>
                                    <div class="rd-health-bar"><span style="width:84%"></span></div>
                                </div>
                            </div>
                            <div class="rd-kpi-grid">
                                <div class="rd-kpi"><div class="rd-kpi-label">Индекс</div><div class="rd-kpi-value">82</div><div class="rd-kpi-note">Пилот оправдан</div></div>
                                <div class="rd-kpi"><div class="rd-kpi-label">Спрос</div><div class="rd-kpi-value">+24%</div><div class="rd-kpi-note">6 месяцев</div></div>
                                <div class="rd-kpi"><div class="rd-kpi-label">Конкуренция</div><div class="rd-kpi-value">Средняя</div><div class="rd-kpi-note">Есть окно входа</div></div>
                                <div class="rd-kpi"><div class="rd-kpi-label">Сетевой сигнал</div><div class="rd-kpi-value">+31%</div><div class="rd-kpi-note">Обсуждения растут</div></div>
                            </div>
                            <div class="rd-grid-2">
                                <div class="rd-panel">
                                    <div class="rd-panel-title">Динамика спроса <span>12 месяцев</span></div>
                                    <div class="rd-line-chart"><div class="rd-axis"><span>Янв</span><span>Мар</span><span>Май</span><span>Июл</span><span>Сен</span><span>Дек</span></div></div>
                                </div>
                                <div class="rd-panel">
                                    <div class="rd-panel-title">Краткий вывод <span>AI summary</span></div>
                                    <div class="rd-summary"><strong>Рекомендация</strong><p>Запускать пилот в двух районах. Центр города лучше рассматривать на втором этапе из-за стоимости входа.</p></div>
                                    <div class="rd-tag-row"><span>Растущий спрос</span><span>Средняя конкуренция</span><span>Пилот</span><span>Риск бюджета</span></div>
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
        <section class="rd-section" id="problem">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Проблема</div>
                    <h2>Данных много. Картина не складывается.</h2>
                </div>
                <p>Команды собирают таблицы, поисковые запросы, отчеты, страницы конкурентов и комментарии из сети. На это уходят часы или дни, а результат часто остается разрозненным.</p>
            </div>
            <div class="rd-card-grid-3">
                <div class="rd-card"><div class="num">01</div><h3>Источники разбросаны</h3><p>Официальная статистика, поведенческие сигналы и активность аудитории живут в разных местах.</p></div>
                <div class="rd-card amber"><div class="num">02</div><h3>Анализ съедает время</h3><p>Команда тратит время на сбор и сверку вместо проверки гипотезы и выбора сценария.</p></div>
                <div class="rd-card coral"><div class="num">03</div><h3>Сигнал приходит поздно</h3><p>Отчеты и продажи часто показывают изменение с задержкой, а сетевой спрос проявляется раньше.</p></div>
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
                    <div class="rd-eyebrow">Живой демо-сценарий</div>
                    <h2>Выберите рынок. Получите первый вывод.</h2>
                </div>
                <p>Это прототип логики RealDemand: пользователь задает регион, сферу и бюджет пилота, а система собирает скоринг, риски и следующий шаг.</p>
            </div>
            <div class="rd-native-panel">
                <h3>Быстрая оценка запуска</h3>
                <p>Сценарий основан на демонстрационных сигналах из макета: спрос, конкуренция, уверенность данных, сетевой шум и бюджет пилота.</p>
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
                    <div class="rd-decision-card"><span>Рекомендация</span><strong>{escape(launch_label)}</strong><em>{escape(sector.label)}</em></div>
                    <div class="rd-decision-card"><span>Динамика спроса</span><strong>+{region.demand_growth}%</strong><em>последние 6 месяцев</em></div>
                    <div class="rd-decision-card"><span>Конкуренция</span><strong>{escape(competition_label)}</strong><em>{region.competition}/100 по плотности</em></div>
                    <div class="rd-decision-card"><span>Уверенность данных</span><strong>{region.confidence}%</strong><em>источники сходятся</em></div>
                </div>
                <div class="rd-grid-2">
                    <div class="rd-panel">
                        <div class="rd-panel-title">География спроса <span>{escape(region_name)}</span></div>
                        <div class="rd-map">
                            <div class="rd-map-card"><strong>{escape(region.district)} район</strong><p>{escape(region.note)}</p></div>
                        </div>
                    </div>
                    <div class="rd-panel">
                        <div class="rd-panel-title">Вывод для команды <span>версия 0.1</span></div>
                        <div class="rd-summary"><strong>{escape(launch_label)}</strong><p>{escape(launch_note)} Слабое место рынка: {escape(sector.weak_spot.lower())}.</p></div>
                        <div class="rd-tag-row">
                            <span>Сетевой сигнал +{region.social_growth}%</span>
                            <span>Бюджет {budget} тыс. ₽</span>
                            <span>{escape(region.district)} район</span>
                            <span>{escape(sector_name)}</span>
                        </div>
                        <div class="rd-source-list" style="margin-top:14px;">
                            <div class="rd-source-item"><span>Официальная статистика</span><span>проверено</span></div>
                            <div class="rd-source-item"><span>Поисковая динамика</span><span>рост</span></div>
                            <div class="rd-source-item"><span>Конкуренты</span><span>{escape(competition_label.lower())}</span></div>
                            <div class="rd-source-item"><span>Отзывы и обсуждения</span><span>+{region.social_growth}%</span></div>
                        </div>
                    </div>
                </div>
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
                    <h2>Рабочий интерфейс для рыночной разведки.</h2>
                </div>
                <p>Система устроена как B2B-аналитический кабинет: фильтры, источники, карта спроса, конкурентная среда, сценарии запуска и отчет для обсуждения внутри команды.</p>
            </div>
            <div class="rd-product-shell">
                <div class="rd-window-bar">
                    <div class="rd-chip-row">
                        <div class="rd-dots"><span></span><span></span><span></span></div>
                        <div class="rd-window-title">RealDemand / Competitive Intelligence</div>
                    </div>
                    <div class="rd-chip-row">
                        <span class="rd-chip">Top players</span>
                        <span class="rd-chip">Signals</span>
                        <span class="rd-chip dark">Alerts on</span>
                    </div>
                </div>
                <div class="rd-dashboard">
                    <aside class="rd-sidebar">
                        <div class="rd-side-brand"><span class="rd-side-dot"></span>RealDemand</div>
                        <div class="rd-side-label">Рабочая область</div>
                        <div class="rd-side-item"><span>Обзор рынка</span></div>
                        <div class="rd-side-item"><span>География спроса</span></div>
                        <div class="rd-side-item active"><span>Конкуренты</span></div>
                        <div class="rd-side-item"><span>Сценарии</span></div>
                        <div class="rd-side-label">Сигналы</div>
                        <div class="rd-side-item active"><span>Упоминания</span></div>
                        <div class="rd-side-item active"><span>Отзывы</span></div>
                        <div class="rd-side-item"><span>Реклама</span></div>
                    </aside>
                    <main class="rd-main">
                        <div class="rd-dashboard-title">
                            <div>
                                <h2>Конкурентная среда</h2>
                                <p>Игроки, сила присутствия, динамика интереса, отзывы и признаки активности в сети.</p>
                            </div>
                            <div class="rd-health">
                                <div class="rd-health-label"><span>Рыночная плотность</span><span>62%</span></div>
                                <div class="rd-health-bar"><span style="width:62%"></span></div>
                            </div>
                        </div>
                        <div class="rd-grid-2">
                            <div class="rd-panel">
                                <div class="rd-panel-title">Активность игроков <span>упоминания / отзывы</span></div>
                                <div class="rd-line-chart"><div class="rd-axis"><span>CleanPro</span><span>HomeFresh</span><span>City</span><span>Chisto24</span></div></div>
                            </div>
                            <div class="rd-panel">
                                <div class="rd-panel-title">Топ игроков <span>по силе сигнала</span></div>
                                <div class="rd-source-list">
                                    <div class="rd-source-item"><span>CleanPro</span><span>+12%</span></div>
                                    <div class="rd-source-item"><span>HomeFresh</span><span>+7%</span></div>
                                    <div class="rd-source-item"><span>City Clean</span><span>+19%</span></div>
                                    <div class="rd-source-item"><span>Chisto24</span><span>локальный</span></div>
                                </div>
                            </div>
                        </div>
                        <div class="rd-grid-3">
                            <div class="rd-panel"><div class="rd-panel-title">Слабые места рынка</div><div class="rd-source-list"><div class="rd-source-item"><span>Мало игроков 24/7</span><span>окно</span></div><div class="rd-source-item"><span>Отзывы о скорости</span><span>боль</span></div></div></div>
                            <div class="rd-panel"><div class="rd-panel-title">Растущие темы</div><div class="rd-source-list"><div class="rd-source-item"><span>Уборка после ремонта</span><span>+28%</span></div><div class="rd-source-item"><span>Экспресс-заказ</span><span>+22%</span></div></div></div>
                            <div class="rd-panel"><div class="rd-panel-title">Финальный вывод</div><div class="rd-summary"><strong>Конкуренция</strong><p>Рынок занят, но в отдельных сценариях спрос растет быстрее, чем предложение.</p></div></div>
                        </div>
                    </main>
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
                    <h2>Проверяем. Сверяем. Решаем.</h2>
                </div>
                <p>Источники подбираются под задачу: для региональной оценки важны одни данные, для конкурентного анализа другие, для раннего тренда третьи.</p>
            </div>
            <div class="rd-card-grid-4">
                <div class="rd-card"><div class="num">Официальная статистика</div><h3>База региона</h3><p>Демография, доходы, занятость, структура отраслей и количество компаний.</p></div>
                <div class="rd-card blue"><div class="num">Потребительская динамика</div><h3>Живой спрос</h3><p>Индексы и поведенческие сигналы показывают, что происходит сейчас.</p></div>
                <div class="rd-card amber"><div class="num">Сеть и медиа</div><h3>Ранний шум</h3><p>Обсуждения, отзывы и упоминания помогают ловить движение до отчетов.</p></div>
                <div class="rd-card green"><div class="num">Конкуренты</div><h3>Кто уже там</h3><p>Сайты, карточки компаний, выдача и соцсети показывают плотность рынка.</p></div>
            </div>
        </section>
        <section class="rd-section" id="cases">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Сценарии</div>
                    <h2>Аналитика для рабочих решений.</h2>
                </div>
                <p>RealDemand нужен командам, которые выбирают регион, оценивают спрос, сравнивают конкурентов и готовят аргументацию для решения.</p>
            </div>
            <div class="rd-card-grid-4">
                <div class="rd-card"><div class="num">Сценарий 01</div><h3>Новый регион</h3><p>Понять, в какой город или район выходить и где конкуренция терпимая.</p></div>
                <div class="rd-card"><div class="num">Сценарий 02</div><h3>Новая сфера</h3><p>Сравнить соседние категории и найти спрос при приемлемой конкуренции.</p></div>
                <div class="rd-card"><div class="num">Сценарий 03</div><h3>Мониторинг</h3><p>Отслеживать отзывы, посты, обсуждения, новых игроков и всплески интереса.</p></div>
                <div class="rd-card"><div class="num">Сценарий 04</div><h3>Отчет</h3><p>Собрать PDF/Word с выводом, источниками и понятной логикой.</p></div>
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
                    <h2>От источников к рабочему выводу.</h2>
                </div>
                <p>Команда видит не только рекомендацию, но и ограничения данных: где источники сходятся, где спорят между собой и какой риск остается.</p>
            </div>
            <div class="rd-compare">
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>3-8 часов ручного анализа</div><div class="rd-compare-cell"><strong>Стало</strong>15-30 минут до первого вывода</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>таблицы, статьи, поисковые сигналы и хаос</div><div class="rd-compare-cell"><strong>Стало</strong>единая картина по спросу, конкурентам и регионам</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>“рынок выглядит интересным”</div><div class="rd-compare-cell"><strong>Стало</strong>“вот сигналы роста, конкуренция и риски”</div></div>
                <div class="rd-compare-row"><div class="rd-compare-cell"><strong>Было</strong>поздняя реакция на рост интереса</div><div class="rd-compare-cell"><strong>Стало</strong>ранние сигналы из поиска, конкурентов и сети</div></div>
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
                    <h2>Разные задачи. Разные форматы.</h2>
                </div>
                <p>Разовый отчет подходит для быстрой проверки гипотезы, подписка для регулярного мониторинга, API для аналитических команд, коробка для внутреннего контура.</p>
            </div>
            <div class="rd-price-grid">
                <div class="rd-price"><h3>Разовый отчет</h3><div class="rd-price-value">19 900 ₽</div><div class="rd-price-sub">за 1 исследование</div><ul><li>Одна сфера, регион или категория</li><li>PDF/Word-отчет с источниками</li><li>Быстрая проверка гипотезы</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=Разовый отчет">Заказать</a></div>
                <div class="rd-price"><h3>SaaS Start</h3><div class="rd-price-value">14 900 ₽</div><div class="rd-price-sub">в месяц</div><ul><li>10 анализов в месяц</li><li>1 пользователь</li><li>Базовый индекс сферы</li><li>Экспорт отчета</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=SaaS Start">Начать</a></div>
                <div class="rd-price featured"><div class="rd-badge">Популярно</div><h3>SaaS Growth</h3><div class="rd-price-value">29 900 ₽</div><div class="rd-price-sub">в месяц</div><ul><li>30 анализов в месяц</li><li>3 пользователя</li><li>Конкуренты, география и динамика</li><li>Мониторинг сетевой активности</li></ul><a class="rd-btn" href="mailto:demo@realdemand.ai?subject=SaaS Growth">Запросить демо</a></div>
                <div class="rd-price"><h3>API / Data Feed</h3><div class="rd-price-value">от 49 900 ₽</div><div class="rd-price-sub">в месяц</div><ul><li>Интеграция с BI/CRM</li><li>Доступ к индексам и данным</li><li>Регулярное обновление сигналов</li></ul><a class="rd-btn secondary" href="mailto:demo@realdemand.ai?subject=API">Обсудить API</a></div>
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
                        <h2>Ответы на частые вопросы.</h2>
                    </div>
                </div>
                <div class="rd-faq-list">
                    <details class="rd-faq" open><summary>Откуда берутся данные?</summary><p>Из источников под конкретную задачу: официальная статистика, потребительские индексы, поисковая динамика, открытые страницы конкурентов, соцсети и медиа.</p></details>
                    <details class="rd-faq"><summary>Как проверяется качество?</summary><p>Вывод привязывается к источникам и типам сигналов. Если данных мало или они противоречат друг другу, отчет показывает это как риск.</p></details>
                    <details class="rd-faq"><summary>Зачем смотреть сеть?</summary><p>Интерес часто сначала появляется в обсуждениях, отзывах, постах, карточках компаний и поиске. Продажи и официальные отчеты догоняют позже.</p></details>
                    <details class="rd-faq"><summary>Какие есть форматы доступа?</summary><p>Доступны разовый отчет, SaaS-подписка, API/Data Feed и коробочная поставка.</p></details>
                </div>
            </div>
            <div class="rd-final">
                <div>
                    <div class="rd-eyebrow" style="background:#fff;">Следующий шаг</div>
                    <h2>Оцените рынок до запуска.</h2>
                    <p>Запросите демо RealDemand. Покажем, как из статистики, спроса, конкурентов и сетевых сигналов собрать аргументированную оценку рынка.</p>
                </div>
                <a class="rd-btn" href="mailto:demo@realdemand.ai?subject=Запрос демо RealDemand">Получить демо</a>
            </div>
            <div class="rd-footer">RealDemand / анализ рынка / спрос / конкуренты / регионы / ранние сигналы</div>
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
