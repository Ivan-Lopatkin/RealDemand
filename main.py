from __future__ import annotations

import base64
from dataclasses import dataclass
from html import escape
from pathlib import Path

import streamlit as st


ASSET_DIR = Path(__file__).parent / "assets"
ARCHITECTURE_IMAGE = ASSET_DIR / "realdemand_architecture.jpg"


@dataclass(frozen=True)
class LocationCandidate:
    district: str
    base_score: int
    demand: int
    competition: int
    traffic: int
    rent: str
    reason: str
    warning: str


LOCATION_DATA: dict[str, list[LocationCandidate]] = {
    "Москва": [
        LocationCandidate("Таганский", 87, 91, 63, 88, "высокая", "сильный поток и платежеспособный спрос", "дорогая аренда"),
        LocationCandidate("Хорошево-Мневники", 82, 84, 52, 76, "средняя+", "растущий жилой массив и умеренная конкуренция", "нужно проверять вечерний поток"),
        LocationCandidate("Южнопортовый", 75, 78, 48, 68, "средняя", "ниже конкуренция и понятная аудитория рядом", "спрос зависит от формата точки"),
    ],
    "Санкт-Петербург": [
        LocationCandidate("Петроградский", 85, 87, 66, 84, "высокая", "поток, доход и плотность точек дают сильный сигнал", "дорогой вход"),
        LocationCandidate("Приморский", 81, 83, 51, 74, "средняя", "много новых жилых кварталов и семейной аудитории", "важна доступность пешком"),
        LocationCandidate("Московский", 77, 79, 58, 71, "средняя+", "баланс трафика, спроса и платежеспособности", "конкуренты сильны в выдаче"),
    ],
    "Казань": [
        LocationCandidate("Ново-Савиновский", 84, 86, 55, 79, "средняя", "жилой спрос, торговые точки и транспортный поток сходятся", "нужно контролировать конкурентов в ТЦ"),
        LocationCandidate("Советский", 78, 80, 49, 70, "средняя-", "растущие кварталы и ниже плотность игроков", "слабее дневной поток"),
        LocationCandidate("Вахитовский", 73, 82, 71, 83, "высокая", "спрос высокий, но вход дороже и рынок плотнее", "не лучший первый тест"),
    ],
}


BUSINESS_PROFILES: dict[str, dict[str, int | str]] = {
    "Кофейня": {"fit": 6, "critical": "утренний трафик, офисы, конкуренты в радиусе 700 м"},
    "Барбершоп": {"fit": 2, "critical": "мужская аудитория 20-45, жилые кварталы, видимость с улицы"},
    "Салон красоты": {"fit": 4, "critical": "доход района, повторные визиты, соседство с жилыми домами"},
    "Небольшой магазин": {"fit": 1, "critical": "пешеходный поток, витринность, якорные точки рядом"},
}

COMMERCIAL_LISTINGS: dict[str, dict[str, list[tuple[str, str, str, str]]]] = {
    "Москва": {
        "Таганский": [
            ("Нижняя Сыромятническая, 10", "72 м²", "420 тыс. ₽/мес.", "первый этаж, витрина"),
            ("Большие Каменщики, 6", "54 м²", "310 тыс. ₽/мес.", "первый этаж, рядом офисы"),
        ],
        "Хорошево-Мневники": [
            ("пр-т Маршала Жукова, 31", "68 м²", "240 тыс. ₽/мес.", "жилой поток"),
            ("ул. Народного Ополчения, 44", "45 м²", "175 тыс. ₽/мес.", "низкий вход"),
        ],
        "Южнопортовый": [
            ("2-й Южнопортовый проезд, 18", "60 м²", "190 тыс. ₽/мес.", "у метро"),
            ("ул. Трофимова, 35", "82 м²", "260 тыс. ₽/мес.", "витринная линия"),
        ],
    },
    "Санкт-Петербург": {
        "Петроградский": [
            ("Большой проспект П.С., 47", "58 м²", "280 тыс. ₽/мес.", "высокий поток"),
            ("Каменноостровский пр., 39", "41 м²", "210 тыс. ₽/мес.", "премиальный район"),
        ],
        "Приморский": [
            ("Комендантский пр., 17", "64 м²", "185 тыс. ₽/мес.", "новые ЖК"),
            ("Богатырский пр., 49", "77 м²", "220 тыс. ₽/мес.", "семейная аудитория"),
        ],
        "Московский": [
            ("Московский пр., 191", "52 м²", "230 тыс. ₽/мес.", "рядом метро"),
            ("ул. Типанова, 21", "70 м²", "205 тыс. ₽/мес.", "районный трафик"),
        ],
    },
    "Казань": {
        "Ново-Савиновский": [
            ("пр-т Ямашева, 93", "62 м²", "145 тыс. ₽/мес.", "рядом ТЦ и остановки"),
            ("ул. Чистопольская, 71", "48 м²", "118 тыс. ₽/мес.", "первый этаж, витрина"),
        ],
        "Советский": [
            ("ул. Сибирский тракт, 34", "75 м²", "105 тыс. ₽/мес.", "низкая аренда"),
            ("ул. Губкина, 30", "55 м²", "82 тыс. ₽/мес.", "жилой поток"),
        ],
        "Вахитовский": [
            ("ул. Баумана, 51", "45 м²", "230 тыс. ₽/мес.", "центр, высокий поток"),
            ("ул. Пушкина, 12", "66 м²", "260 тыс. ₽/мес.", "дорогой вход"),
        ],
    },
}


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def adjusted_score(candidate: LocationCandidate, business_type: str, budget: int) -> int:
    profile = BUSINESS_PROFILES[business_type]
    fit = int(profile["fit"])
    budget_bonus = 0
    if budget >= 2_500_000:
        budget_bonus = 4
    elif budget < 900_000 and candidate.rent.startswith("высок"):
        budget_bonus = -9
    elif budget < 1_500_000 and candidate.rent.startswith("высок"):
        budget_bonus = -5
    competition_penalty = max(0, candidate.competition - 65) // 4
    return max(0, min(99, candidate.base_score + fit + budget_bonus - competition_penalty))


def ranked_locations(city: str, business_type: str, budget: int) -> list[tuple[LocationCandidate, int]]:
    ranked = [(candidate, adjusted_score(candidate, business_type, budget)) for candidate in LOCATION_DATA[city]]
    return sorted(ranked, key=lambda item: item[1], reverse=True)


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)



def render_css() -> None:
    html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

        :root {
            --void: #0c0f14;
            --panel: #141a22;
            --panel-2: #1b232d;
            --raise: #222c38;
            --line: #28323e;
            --line-soft: #1f2832;
            --paper: #eef1f4;
            --paper-dim: #c3ccd6;
            --muted: #8593a3;
            --muted-2: #5e6b79;
            --amber: #f2a93b;
            --amber-bright: #ffc15e;
            --amber-deep: #b5781d;
            --teal: #54d3c4;
            --teal-deep: #2a8d82;
            --coral: #ff6f5e;
            --radius: 4px;
            --radius-lg: 10px;
            --max: 1200px;
            --mono: 'Space Mono', ui-monospace, monospace;
            --display: 'Space Grotesk', system-ui, sans-serif;
            --body: 'Manrope', system-ui, sans-serif;
        }

        html { scroll-behavior: smooth; }

        html, body { background-color: var(--void) !important; }
        body, .stApp { color: var(--paper); }
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stBottomBlockContainer"],
        section.main, .main, .appview-container, .block-container {
            background: transparent !important;
        }

        .stApp {
            background:
                radial-gradient(1100px 600px at 82% -8%, rgba(242,169,59,.10), transparent 60%),
                radial-gradient(900px 600px at -6% 12%, rgba(84,211,196,.07), transparent 55%),
                var(--void);
            color: var(--paper);
            font-family: var(--body);
            -webkit-font-smoothing: antialiased;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            background-image:
                linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
            background-size: 64px 64px;
            mask-image: radial-gradient(120% 90% at 50% 0%, #000 35%, transparent 90%);
        }

        .stApp * { font-family: inherit; }
        .block-container > * { position: relative; z-index: 1; }

        [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"], #MainMenu, footer {
            visibility: hidden; height: 0;
        }

        .block-container { max-width: var(--max); padding: 0 22px 72px; }

        /* ---------- nav ---------- */
        .rd-nav {
            position: sticky; top: 0; z-index: 30;
            display: flex; align-items: center; justify-content: space-between;
            gap: 18px; min-height: 60px; margin: 0 -22px 8px; padding: 12px 22px;
            background: rgba(12,15,20,.78);
            border-bottom: 1px solid var(--line-soft);
            backdrop-filter: blur(16px);
        }
        .rd-brand {
            display: inline-flex; align-items: center; gap: 11px;
            color: var(--paper) !important; text-decoration: none !important;
            font-family: var(--display); font-size: 17px; font-weight: 600; letter-spacing: -.01em;
        }
        .rd-mark {
            width: 26px; height: 26px; position: relative; flex: none;
            border: 1.5px solid var(--amber); transform: rotate(45deg);
            border-radius: 3px;
            box-shadow: inset 0 0 0 4px rgba(242,169,59,.16);
        }
        .rd-mark::after {
            content: ""; position: absolute; inset: 7px;
            background: var(--amber); border-radius: 2px;
        }
        .rd-nav-links {
            display: flex; align-items: center; gap: 20px;
            font-family: var(--mono); font-size: 11px; letter-spacing: .08em;
            text-transform: uppercase; color: var(--muted);
        }
        .rd-nav-links a { color: inherit !important; text-decoration: none !important; transition: color .15s; }
        .rd-nav-links a:hover { color: var(--amber) !important; }

        .rd-btn, .rd-btn:visited {
            display: inline-flex; align-items: center; gap: 8px;
            min-height: 42px; padding: 0 18px;
            border-radius: var(--radius); border: 1px solid var(--amber);
            background: var(--amber); color: #11161d !important;
            font-family: var(--display); font-size: 13px; font-weight: 600; letter-spacing: .01em;
            text-decoration: none !important; white-space: nowrap;
            transition: transform .15s, box-shadow .15s, background .15s;
            box-shadow: 0 0 0 1px rgba(242,169,59,.2), 0 14px 34px rgba(242,169,59,.16);
        }
        .rd-btn:hover { background: var(--amber-bright); transform: translateY(-1px); }
        .rd-btn.ghost {
            background: transparent; color: var(--paper) !important;
            border-color: var(--line); box-shadow: none;
        }
        .rd-btn.ghost:hover { border-color: var(--amber); color: var(--amber) !important; background: transparent; }

        /* ---------- shared ---------- */
        .rd-eyebrow {
            display: inline-flex; align-items: center; gap: 8px;
            font-family: var(--mono); font-size: 11px; font-weight: 700;
            letter-spacing: .16em; text-transform: uppercase; color: var(--amber);
            margin: 0 0 18px;
        }
        .rd-eyebrow::before {
            content: ""; width: 18px; height: 1px; background: var(--amber); opacity: .7;
        }

        .rd-section { padding: 64px 0; border-top: 1px solid var(--line-soft); }
        .rd-section-head {
            display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, .85fr);
            gap: 28px; align-items: end; margin-bottom: 36px;
        }
        .rd-section-title {
            margin: 0; font-family: var(--display); font-weight: 600;
            font-size: clamp(28px, 3.4vw, 44px); line-height: 1.04; letter-spacing: -.02em;
            color: var(--paper);
        }
        .rd-section-title em { color: var(--amber); font-style: normal; }
        .rd-section-head p {
            margin: 0; align-self: end; color: var(--muted);
            font-size: 16px; line-height: 1.6;
        }

        /* ---------- hero ---------- */
        .rd-hero {
            display: grid; grid-template-columns: minmax(0, 1.02fr) minmax(440px, 1.05fr);
            gap: 44px; align-items: center; padding: 52px 0 30px;
        }
        .rd-hero-copy { min-width: 0; }
        .rd-h1 {
            margin: 0 0 22px; font-family: var(--display); font-weight: 600;
            font-size: clamp(40px, 5.4vw, 70px); line-height: .98; letter-spacing: -.03em;
            color: var(--paper);
        }
        .rd-h1 em { color: var(--amber); font-style: normal; }
        .rd-lead { max-width: 540px; margin: 0 0 26px; color: var(--paper-dim); font-size: 19px; line-height: 1.55; }
        .rd-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 30px; }

        .rd-readout {
            display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px;
            padding: 14px 16px; border: 1px solid var(--line);
            border-radius: var(--radius); background: rgba(20,26,34,.6);
            font-family: var(--mono); font-size: 12px; color: var(--muted);
        }
        .rd-readout .k { color: var(--teal); }
        .rd-readout .v { color: var(--paper); }
        .rd-readout .sep { color: var(--muted-2); }
        .rd-readout .verdict { color: var(--amber); font-weight: 700; }
        .rd-dot {
            width: 7px; height: 7px; border-radius: 50%; background: var(--teal);
            box-shadow: 0 0 0 0 rgba(84,211,196,.5); animation: rdpulse 2.4s infinite;
        }
        @keyframes rdpulse {
            0% { box-shadow: 0 0 0 0 rgba(84,211,196,.45); }
            70% { box-shadow: 0 0 0 7px rgba(84,211,196,0); }
            100% { box-shadow: 0 0 0 0 rgba(84,211,196,0); }
        }

        /* ---------- verdict instrument (signature) ---------- */
        .rd-instrument {
            position: relative; border: 1px solid var(--line);
            border-radius: var(--radius-lg); background:
                linear-gradient(180deg, rgba(27,35,45,.9), rgba(18,24,31,.95));
            box-shadow: 0 40px 90px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.04);
            overflow: hidden;
        }
        .rd-inst-bar {
            display: flex; align-items: center; justify-content: space-between;
            gap: 12px; padding: 12px 16px; border-bottom: 1px solid var(--line);
            font-family: var(--mono); font-size: 11px; letter-spacing: .06em;
            text-transform: uppercase; color: var(--muted);
            background: rgba(12,15,20,.5);
        }
        .rd-inst-live { display: inline-flex; align-items: center; gap: 8px; color: var(--teal); }
        .rd-inst-body { padding: 16px; display: grid; gap: 14px; }

        .rd-map {
            position: relative; height: 268px; border-radius: var(--radius);
            border: 1px solid var(--line); overflow: hidden;
            background:
                radial-gradient(120px 120px at 30% 42%, rgba(242,169,59,.34), transparent 70%),
                radial-gradient(150px 150px at 66% 38%, rgba(84,211,196,.20), transparent 72%),
                radial-gradient(110px 110px at 54% 78%, rgba(255,111,94,.16), transparent 72%),
                linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px),
                #0a0d12;
            background-size: auto, auto, auto, 30px 30px, 30px 30px, auto;
        }
        .rd-contour {
            position: absolute; border: 1px solid rgba(242,169,59,.22);
            border-radius: 50%;
        }
        .rd-contour.c1 { inset: 78px 58% 70px 22%; }
        .rd-contour.c2 { inset: 62px 50% 52px 12%; border-color: rgba(242,169,59,.13); }
        .rd-plot {
            position: absolute; inset: 26px 30px; border: 1px dashed rgba(255,255,255,.14);
            border-radius: 2px; transform: rotate(-6deg);
        }
        .rd-node {
            position: absolute; width: 16px; height: 16px; transform: rotate(45deg);
            border: 1.5px solid #0a0d12; border-radius: 3px;
            display: grid; place-items: center;
        }
        .rd-node b {
            transform: rotate(-45deg); font-family: var(--mono); font-size: 9px;
            font-weight: 700; color: #0a0d12;
        }
        .rd-node.n1 { left: 28%; top: 40%; background: var(--amber); width: 22px; height: 22px;
            box-shadow: 0 0 0 5px rgba(242,169,59,.18); }
        .rd-node.n2 { left: 64%; top: 35%; background: var(--teal); }
        .rd-node.n3 { left: 52%; top: 74%; background: var(--coral); }

        .rd-map-flag {
            position: absolute; left: 14px; bottom: 14px; right: 14px;
            display: flex; align-items: center; justify-content: space-between; gap: 10px;
            padding: 10px 12px; border: 1px solid var(--line);
            border-radius: var(--radius); background: rgba(10,13,18,.86);
            backdrop-filter: blur(4px);
        }
        .rd-map-flag span { font-family: var(--mono); font-size: 10px; letter-spacing: .08em;
            text-transform: uppercase; color: var(--muted); }
        .rd-map-flag strong { display: block; margin-top: 3px; font-family: var(--display);
            font-size: 14px; font-weight: 600; color: var(--paper); }
        .rd-map-flag em {
            font-family: var(--mono); font-size: 11px; font-weight: 700; font-style: normal;
            color: var(--teal); white-space: nowrap; padding: 5px 8px;
            border: 1px solid rgba(84,211,196,.3); border-radius: 3px; background: rgba(84,211,196,.08);
        }

        .rd-verdict {
            display: grid; grid-template-columns: auto 1fr; gap: 16px; align-items: center;
            padding: 14px 16px; border: 1px solid var(--amber-deep); border-radius: var(--radius);
            background: linear-gradient(135deg, rgba(242,169,59,.14), rgba(242,169,59,.03));
        }
        .rd-score-big {
            font-family: var(--mono); font-weight: 700; font-size: 46px; line-height: 1;
            color: var(--amber-bright); letter-spacing: -.02em;
        }
        .rd-score-big small { display: block; font-size: 11px; letter-spacing: .1em;
            color: var(--amber); margin-top: 4px; }
        .rd-verdict-label { font-family: var(--mono); font-size: 11px; letter-spacing: .12em;
            text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
        .rd-verdict-word { font-family: var(--display); font-weight: 700; font-size: 24px;
            color: var(--paper); line-height: 1; }
        .rd-verdict-sub { margin-top: 7px; font-size: 12px; color: var(--paper-dim); line-height: 1.4; }

        .rd-gauges { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .rd-gauge { padding: 11px; border: 1px solid var(--line); border-radius: var(--radius);
            background: var(--panel); }
        .rd-gauge span { font-family: var(--mono); font-size: 10px; letter-spacing: .08em;
            text-transform: uppercase; color: var(--muted); }
        .rd-gauge strong { display: block; margin: 6px 0 8px; font-family: var(--mono);
            font-size: 16px; font-weight: 700; color: var(--paper); }
        .rd-track { height: 4px; border-radius: 99px; background: #0a0d12; overflow: hidden; }
        .rd-track i { display: block; height: 100%; border-radius: inherit; }
        .rd-track i.a { background: var(--amber); }
        .rd-track i.t { background: var(--teal); }
        .rd-track i.c { background: var(--coral); }

        .rd-inst-listings { display: grid; gap: 1px; border: 1px solid var(--line);
            border-radius: var(--radius); overflow: hidden; background: var(--line); }
        .rd-inst-listings div { display: flex; justify-content: space-between; gap: 12px;
            padding: 10px 12px; background: var(--panel); font-family: var(--mono); font-size: 11px; }
        .rd-inst-listings span { color: var(--paper-dim); }
        .rd-inst-listings strong { color: var(--teal); font-weight: 700; white-space: nowrap; }

        /* corner ticks */
        .rd-tick { position: absolute; width: 9px; height: 9px; border-color: var(--amber); opacity: .5; }
        .rd-tick.tl { top: 8px; left: 8px; border-top: 1.5px solid; border-left: 1.5px solid; }
        .rd-tick.tr { top: 8px; right: 8px; border-top: 1.5px solid; border-right: 1.5px solid; }
        .rd-tick.bl { bottom: 8px; left: 8px; border-bottom: 1.5px solid; border-left: 1.5px solid; }
        .rd-tick.br { bottom: 8px; right: 8px; border-bottom: 1.5px solid; border-right: 1.5px solid; }

        /* ---------- cards / grids ---------- */
        .rd-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
        .rd-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
        .rd-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }

        .rd-card {
            position: relative; padding: 22px 20px; border: 1px solid var(--line);
            border-radius: var(--radius); background: var(--panel);
            transition: border-color .18s, transform .18s;
        }
        .rd-card:hover { border-color: var(--raise); transform: translateY(-2px); }
        .rd-card .idx { font-family: var(--mono); font-size: 11px; font-weight: 700;
            letter-spacing: .1em; color: var(--muted); }
        .rd-card .tag { font-family: var(--mono); font-size: 10px; font-weight: 700;
            letter-spacing: .1em; text-transform: uppercase; color: var(--teal); }
        .rd-card strong { display: block; margin: 12px 0 9px; font-family: var(--display);
            font-size: 19px; font-weight: 600; line-height: 1.18; color: var(--paper); }
        .rd-card p { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.55; }
        .rd-card.amber { border-color: var(--amber-deep);
            background: linear-gradient(160deg, rgba(242,169,59,.09), var(--panel) 55%); }
        .rd-card.amber .tag { color: var(--amber); }
        .rd-card.teal { border-color: var(--teal-deep);
            background: linear-gradient(160deg, rgba(84,211,196,.08), var(--panel) 55%); }
        .rd-card.coral { border-color: #8a3a32;
            background: linear-gradient(160deg, rgba(255,111,94,.09), var(--panel) 55%); }
        .rd-card.coral .tag { color: var(--coral); }

        /* stat row */
        .rd-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
        .rd-stat { padding: 20px; border: 1px solid var(--line); border-radius: var(--radius);
            background: var(--panel); }
        .rd-stat b { display: block; font-family: var(--mono); font-weight: 700;
            font-size: 30px; color: var(--amber); letter-spacing: -.01em; }
        .rd-stat span { display: block; margin-top: 8px; color: var(--muted); font-size: 13px; line-height: 1.5; }

        /* ---------- table ---------- */
        .rd-table { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
        .rd-trow { display: grid; grid-template-columns: .85fr 1fr 1fr 1.05fr; border-top: 1px solid var(--line); }
        .rd-trow:first-child { border-top: 0; }
        .rd-trow.head { background: var(--panel-2); }
        .rd-trow.head .rd-tcell { font-family: var(--mono); font-size: 11px; font-weight: 700;
            letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
        .rd-tcell { padding: 16px; border-left: 1px solid var(--line); color: var(--muted);
            font-size: 13.5px; line-height: 1.5; background: var(--panel); }
        .rd-tcell:first-child { border-left: 0; }
        .rd-tcell strong { display: block; margin-bottom: 5px; font-family: var(--display);
            font-size: 14px; font-weight: 600; color: var(--paper); }
        .rd-tcell.win { color: var(--paper-dim); }
        .rd-tcell.win::before { content: "→ "; color: var(--amber); font-weight: 700; }

        /* ---------- price ---------- */
        .rd-price { padding: 24px 20px; border: 1px solid var(--line); border-radius: var(--radius);
            background: var(--panel); }
        .rd-price.feature { border-color: var(--amber-deep);
            background: linear-gradient(165deg, rgba(242,169,59,.1), var(--panel) 60%); }
        .rd-price .tag { font-family: var(--mono); font-size: 10px; font-weight: 700;
            letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
        .rd-price b { display: block; margin: 12px 0; font-family: var(--display);
            font-size: 26px; font-weight: 600; color: var(--paper); }
        .rd-price.feature b { color: var(--amber-bright); }
        .rd-price p { margin: 0; color: var(--muted); font-size: 13.5px; line-height: 1.55; }

        /* ---------- final ---------- */
        .rd-final {
            position: relative; display: grid; grid-template-columns: 1.4fr .9fr; gap: 28px;
            align-items: center; padding: 40px; border: 1px solid var(--amber-deep);
            border-radius: var(--radius-lg); overflow: hidden;
            background:
                radial-gradient(700px 300px at 85% 20%, rgba(242,169,59,.16), transparent 60%),
                linear-gradient(180deg, var(--panel-2), var(--panel));
        }
        .rd-final h2 { margin: 0 0 14px; font-family: var(--display); font-weight: 600;
            font-size: clamp(28px, 3.6vw, 46px); line-height: 1.02; letter-spacing: -.02em; color: var(--paper); }
        .rd-final h2 em { color: var(--amber); font-style: normal; }
        .rd-final p { margin: 0 0 18px; color: var(--paper-dim); font-size: 16px; line-height: 1.6; max-width: 620px; }
        .rd-roadmap { display: flex; flex-wrap: wrap; gap: 8px; }
        .rd-roadmap span { font-family: var(--mono); font-size: 11px; padding: 7px 11px;
            border: 1px solid var(--line); border-radius: 3px; color: var(--paper-dim);
            background: rgba(12,15,20,.4); }
        .rd-final-box { padding: 22px; border: 1px solid var(--amber-deep); border-radius: var(--radius);
            background: rgba(12,15,20,.5); }
        .rd-final-box .tag { font-family: var(--mono); font-size: 10px; font-weight: 700;
            letter-spacing: .1em; text-transform: uppercase; color: var(--amber); }
        .rd-final-box strong { display: block; margin: 12px 0 18px; font-family: var(--display);
            font-size: 21px; font-weight: 600; line-height: 1.2; color: var(--paper); }

        .rd-src { margin-top: 14px; font-family: var(--mono); font-size: 11px; color: var(--muted-2); line-height: 1.6; }

        /* ---------- streamlit demo widgets (dark theme) ---------- */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--line) !important;
            border-radius: var(--radius-lg) !important;
            background: var(--panel) !important;
            padding: 22px !important;
        }
        .rd-demo-shell { margin-top: 4px; padding: 22px; border: 1px solid var(--line);
            border-radius: var(--radius-lg); background: var(--panel); }
        div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label {
            color: var(--muted) !important; font-family: var(--mono) !important;
            font-size: 11px !important; font-weight: 700 !important; letter-spacing: .08em !important;
            text-transform: uppercase !important;
        }
        div[data-baseweb="select"] > div {
            background: var(--void) !important; border-color: var(--line) !important;
            border-radius: var(--radius) !important; color: var(--paper) !important;
        }
        div[data-baseweb="select"] * { color: var(--paper) !important; }
        [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] { background: var(--amber) !important; }
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div { background: var(--amber) !important; }
        .stProgress > div > div > div { background: #0a0d12 !important; }
        .stProgress > div > div > div > div { background: linear-gradient(90deg, var(--amber), var(--amber-bright)) !important; }
        [data-testid="stProgress"] p, .stProgress p { color: var(--paper-dim) !important; font-family: var(--mono) !important; }

        .rd-result { display: grid; grid-template-columns: 1.1fr .9fr; gap: 14px; align-items: start; margin-top: 18px; }
        .rd-result-main { padding: 20px; border: 1px solid var(--amber-deep); border-radius: var(--radius);
            background: linear-gradient(160deg, rgba(242,169,59,.1), var(--panel-2) 60%); }
        .rd-result-main .tag { font-family: var(--mono); font-size: 10px; font-weight: 700;
            letter-spacing: .1em; text-transform: uppercase; color: var(--amber); }
        .rd-result-main strong { display: block; margin: 10px 0; font-family: var(--display);
            font-size: 28px; font-weight: 600; color: var(--paper); }
        .rd-result-main p { margin: 0 0 14px; color: var(--paper-dim); font-size: 14px; line-height: 1.55; }
        .rd-next { display: inline-flex; font-family: var(--mono); font-size: 11px; font-weight: 700;
            color: var(--void); background: var(--amber); padding: 8px 12px; border-radius: 3px; }
        .rd-mini { display: grid; gap: 8px; }
        .rd-mini-row { display: flex; justify-content: space-between; align-items: center;
            padding: 12px 14px; border: 1px solid var(--line); border-radius: var(--radius);
            background: var(--panel); font-family: var(--mono); font-size: 12px; }
        .rd-mini-row span { color: var(--muted); }
        .rd-mini-row strong { color: var(--paper); font-weight: 700; }
        .rd-listings { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px; }
        .rd-listing { padding: 16px; border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel); }
        .rd-listing .tag { font-family: var(--mono); font-size: 11px; color: var(--teal); }
        .rd-listing strong { display: block; margin: 8px 0 7px; font-family: var(--display);
            font-size: 16px; font-weight: 600; color: var(--paper); }
        .rd-listing p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
        .rd-rank { display: grid; gap: 10px; margin-top: 14px; }
        .rd-rank-card { padding: 14px 16px; border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel); }
        .rd-rank-top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 9px; }
        .rd-rank-top span { font-family: var(--display); font-size: 15px; font-weight: 600; color: var(--paper); }
        .rd-rank-top em { font-family: var(--mono); font-size: 13px; font-weight: 700; font-style: normal; color: var(--amber); }
        .rd-rank-card p { margin: 9px 0 0; color: var(--muted); font-size: 12.5px; line-height: 1.5; }

        .rd-architecture { padding: 16px; border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel); }
        .rd-architecture img { width: 100%; display: block; border-radius: 3px; border: 1px solid var(--line); }
        .rd-architecture.fallback { font-family: var(--mono); font-size: 13px; color: var(--muted); text-align: center; padding: 40px; }

        /* ---------- responsive ---------- */
        @media (max-width: 1080px) {
            .rd-hero, .rd-section-head, .rd-result, .rd-final { grid-template-columns: 1fr; }
            .rd-hero { gap: 32px; }
            .rd-section-head { gap: 12px; }
            .rd-section-head p { align-self: start; }
            .rd-grid-4 { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 680px) {
            .block-container { padding-left: 16px; padding-right: 16px; }
            .rd-nav { margin-left: -16px; margin-right: -16px; gap: 10px; padding: 12px 16px; }
            .rd-nav-links { display: none; }
            .rd-nav .rd-btn { padding: 0 13px; font-size: 12px; min-height: 40px; }
            .rd-grid-2, .rd-grid-3, .rd-grid-4, .rd-stats, .rd-gauges, .rd-listings { grid-template-columns: 1fr; }
            .rd-instrument { min-width: 0; }
            .rd-trow { grid-template-columns: 1fr; }
            .rd-tcell { border-left: 0; border-top: 1px solid var(--line); }
            .rd-tcell:first-child { border-top: 0; }
            .rd-verdict { grid-template-columns: 1fr; text-align: left; }
        }
        </style>
        """
    )


def render_nav() -> None:
    html(
        """
        <nav class="rd-nav">
            <a class="rd-brand" href="#top"><span class="rd-mark"></span><span>RealDemand</span></a>
            <div class="rd-nav-links">
                <a href="#problem">Проблема</a>
                <a href="#audience">ЦА</a>
                <a href="#how">Как</a>
                <a href="#demo">Демо</a>
                <a href="#market">Рынок</a>
                <a href="#rivals">Конкуренты</a>
                <a href="#money">Деньги</a>
            </div>
            <a class="rd-btn" href="#demo">Запустить разбор →</a>
        </nav>
        """
    )


def instrument_markup() -> str:
    return """
        <div class="rd-instrument">
            <span class="rd-tick tl"></span><span class="rd-tick tr"></span>
            <span class="rd-tick bl"></span><span class="rd-tick br"></span>
            <div class="rd-inst-bar">
                <span>RealDemand · разбор локации</span>
                <span class="rd-inst-live"><span class="rd-dot"></span>оценка вживую</span>
            </div>
            <div class="rd-inst-body">
                <div class="rd-map">
                    <span class="rd-contour c2"></span>
                    <span class="rd-contour c1"></span>
                    <span class="rd-plot"></span>
                    <span class="rd-node n1"><b>1</b></span>
                    <span class="rd-node n2"><b>2</b></span>
                    <span class="rd-node n3"><b>3</b></span>
                    <div class="rd-map-flag">
                        <div><span>лучший старт</span><strong>Ново-Савиновский</strong></div>
                        <em>2 объекта</em>
                    </div>
                </div>
                <div class="rd-verdict">
                    <div class="rd-score-big">91<small>/ 100</small></div>
                    <div>
                        <div class="rd-verdict-label">Вердикт · Казань / кофейня / 1.8 млн ₽</div>
                        <div class="rd-verdict-word">ОТКРЫВАТЬ</div>
                        <div class="rd-verdict-sub">Спрос и трафик высокие, конкуренция умеренная, есть свободные помещения под формат.</div>
                    </div>
                </div>
                <div class="rd-gauges">
                    <div class="rd-gauge"><span>Спрос</span><strong>86</strong><div class="rd-track"><i class="a" style="width:86%"></i></div></div>
                    <div class="rd-gauge"><span>Трафик</span><strong>79</strong><div class="rd-track"><i class="t" style="width:79%"></i></div></div>
                    <div class="rd-gauge"><span>Конкур.</span><strong>55</strong><div class="rd-track"><i class="c" style="width:55%"></i></div></div>
                </div>
                <div class="rd-inst-listings">
                    <div><span>пр-т Ямашева, 93 · 62 м²</span><strong>145 тыс. ₽/мес</strong></div>
                    <div><span>ул. Чистопольская, 71 · 48 м²</span><strong>118 тыс. ₽/мес</strong></div>
                </div>
            </div>
        </div>
    """


def render_hero() -> None:
    html(
        f"""
        <section class="rd-hero" id="top">
            <div class="rd-hero-copy">
                <div class="rd-eyebrow">Гео-оценка для офлайн-бизнеса</div>
                <h1 class="rd-h1">Где открыть точку, чтобы она <em>зарабатывала</em></h1>
                <p class="rd-lead">RealDemand читает спрос, конкурентов, трафик и реальные объявления аренды, а потом ставит локации балл и говорит прямо: открывать здесь или искать дальше.</p>
                <div class="rd-actions">
                    <a class="rd-btn" href="#demo">Запустить разбор →</a>
                    <a class="rd-btn ghost" href="#how">Как считаем</a>
                </div>
                <div class="rd-readout">
                    <span class="dotwrap"></span>
                    <span class="k">55.79°N 49.12°E</span>
                    <span class="sep">/</span>
                    <span class="v">КАЗАНЬ · КОФЕЙНЯ · 1.8 МЛН ₽</span>
                    <span class="sep">→</span>
                    <span class="v">БАЛЛ 91</span>
                    <span class="sep">·</span>
                    <span class="verdict">ОТКРЫВАТЬ</span>
                </div>
            </div>
            <div>{instrument_markup()}</div>
        </section>
        <section style="padding:18px 0 0;">
            <div class="rd-stats">
                <div class="rd-stat"><b>1–5 млн ₽</b><span>цена ошибки локации: аренда, ремонт, найм и месяцы слабой выручки до закрытия.</span></div>
                <div class="rd-stat"><b>Топ-3</b><span>района плюс конкретные доступные помещения под площадь, ставку и формат.</span></div>
                <div class="rd-stat"><b>С объяснением</b><span>не чёрный ящик: балл, причины, риски и следующий шаг для каждой точки.</span></div>
            </div>
        </section>
        """
    )


def render_problem() -> None:
    html(
        """
        <section class="rd-section" id="problem">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Проблема</div>
                    <h2 class="rd-section-title">Локацию выбирают <em>на глаз</em> — и это самый дорогой риск запуска</h2>
                </div>
                <p>Карты показывают данные, риелторы продают метры, объявления живут отдельно от аналитики. А вопрос предпринимателя простой: какое доступное помещение снять, чтобы точка зарабатывала?</p>
            </div>
            <div class="rd-grid-3">
                <div class="rd-card coral"><div class="tag">01 · разрыв</div><strong>Данных много, решения нет</strong><p>Карты, отзывы, Wordstat, объявления и статистика существуют — но свести их в один вывод приходится вручную.</p></div>
                <div class="rd-card amber"><div class="tag">02 · поздно</div><strong>Ошибка видна после подписи</strong><p>Неудачный адрес проявляется уже после аренды, ремонта и найма — когда выйти почти невозможно.</p></div>
                <div class="rd-card teal"><div class="tag">03 · отрыв</div><strong>Район ≠ помещение</strong><p>Даже сильный район бесполезен, если сейчас нет свободного объекта под нужную площадь, ставку и формат.</p></div>
            </div>
        </section>
        """
    )


def render_audience() -> None:
    html(
        """
        <section class="rd-section" id="audience">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Целевая аудитория</div>
                    <h2 class="rd-section-title">Предприниматель, открывающий <em>1–3 точки</em></h2>
                </div>
                <p>Кофейни, барбершопы, салоны красоты и небольшие магазины в городах РФ. Есть бюджет на запуск, но нет аналитического отдела и времени вручную мониторить аренду.</p>
            </div>
            <div class="rd-grid-4">
                <div class="rd-card"><div class="tag">кто</div><strong>Фаундер или управляющий</strong><p>Сам решает по району, аренде и первому бюджету — без согласований.</p></div>
                <div class="rd-card teal"><div class="tag">когда</div><strong>Перед подписью аренды</strong><p>На руках 2–5 помещений или район поиска. Нужно выбрать до необратимых затрат.</p></div>
                <div class="rd-card amber"><div class="tag">почему больно</div><strong>Аренда фиксирует ошибку</strong><p>Плохой адрес не лечится рекламой и скидками — только переездом.</p></div>
                <div class="rd-card"><div class="tag">проверка</div><strong>15–30 интервью</strong><p>Цель: понять, как выбирают место и каким данным реально доверяют.</p></div>
            </div>
            <div style="margin:30px 0 18px;"><div class="rd-eyebrow">Честно: что подтверждено, а что гипотеза</div></div>
            <div class="rd-grid-3">
                <div class="rd-card teal"><div class="tag">подтверждено</div><strong>Рынок растёт двузначно</strong><p>Оборот кофеен и кафе в РФ за 2025 год вырос на ~22%, число салонов красоты — на 12% год к году. Решений о локации становится больше.</p></div>
                <div class="rd-card"><div class="tag">проверяем сейчас</div><strong>Где именно платят</strong><p>15–30 интервью: на каком шаге аренды предприниматель готов заплатить за внешний отчёт и каким источникам доверяет.</p></div>
                <div class="rd-card coral"><div class="tag">гипотеза</div><strong>Цена 4 900 ₽</strong><p>Пока выведена из цены ошибки, а не из прямого опроса. Первая партия платных отчётов это проверит.</p></div>
            </div>
        </section>
        """
    )


def render_architecture() -> None:
    image_uri = image_data_uri(ARCHITECTURE_IMAGE)
    image_markup = (
        f'<div class="rd-architecture"><img src="{image_uri}" alt="Архитектура RealDemand"></div>'
        if image_uri
        else '<div class="rd-architecture fallback">схема архитектуры · assets/realdemand_architecture.jpg</div>'
    )
    html(
        f"""
        <section class="rd-section" id="how">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Как считаем</div>
                    <h2 class="rd-section-title">Четыре слоя сигналов сводятся в <em>один балл</em> объекта</h2>
                </div>
                <p>Единый конвейер: сбор геоданных, парсинг коммерческой аренды, оценка районов и помещений, визуализация top-3 и выбор объекта.</p>
            </div>
            {image_markup}
            <div class="rd-grid-4" style="margin-top:14px;">
                <div class="rd-card"><div class="tag">спрос</div><strong>Wordstat и категория</strong><p>Частотность, районный интерес и близкие пользовательские боли.</p></div>
                <div class="rd-card teal"><div class="tag">конкуренты</div><strong>Карты и 2GIS</strong><p>Плотность, рейтинг, отзывы, формат и расстояние до игроков.</p></div>
                <div class="rd-card"><div class="tag">трафик</div><strong>Хабы и пешие потоки</strong><p>Транспорт, метро, парки, площади и точки притяжения.</p></div>
                <div class="rd-card amber"><div class="tag">аренда</div><strong>Объявления и соответствие</strong><p>Парсим объекты, проверяем площадь, ставку, витрину и риск входа.</p></div>
            </div>
        </section>
        """
    )


def render_demo() -> None:
    html(
        """
        <section class="rd-section" id="demo">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Живой разбор</div>
                    <h2 class="rd-section-title">Задайте параметры — получите <em>вердикт и объекты</em></h2>
                </div>
                <p>Город, формат и бюджет на входе. На выходе — top-3 района, причины балла, риски, доступные помещения и следующий шаг.</p>
            </div>
        </section>
        """
    )

    with st.container(border=True):
        col_1, col_2, col_3 = st.columns([1, 1, 1], gap="medium")
        with col_1:
            city = st.selectbox("Город", list(LOCATION_DATA), index=2)
        with col_2:
            business_type = st.selectbox("Тип бизнеса", list(BUSINESS_PROFILES), index=0)
        with col_3:
            budget = st.slider("Бюджет запуска, ₽", min_value=600_000, max_value=5_000_000, value=1_800_000, step=100_000)

        ranked = ranked_locations(city, business_type, budget)
        top_candidate, top_score = ranked[0]
        profile = BUSINESS_PROFILES[business_type]
        listings = COMMERCIAL_LISTINGS.get(city, {}).get(top_candidate.district, [])

        verdict = "ОТКРЫВАТЬ" if top_score >= 80 else ("ПРОВЕРИТЬ" if top_score >= 68 else "ПРИДЕРЖАТЬ")

        st.progress(top_score / 100, text=f"ИТОГОВЫЙ БАЛЛ · {top_score}/100 · {verdict}")

        listing_rows = "".join(
            '<div class="rd-listing">'
            f'<div class="tag">{escape(area)} · {escape(price)}</div>'
            f'<strong>{escape(address)}</strong>'
            f'<p>{escape(fit)}. Проверяем ставку, витрину, первый этаж и срок экспозиции.</p>'
            "</div>"
            for address, area, price, fit in listings
        )

        rank_rows = "".join(
            '<div class="rd-rank-card">'
            f'<div class="rd-rank-top"><span>{i}. {escape(c.district)}</span><em>{s}/100</em></div>'
            f'<div class="rd-track"><i class="a" style="width:{s}%"></i></div>'
            f'<p>{escape(c.reason)}. Риск: {escape(c.warning)}.</p>'
            "</div>"
            for i, (c, s) in enumerate(ranked, start=1)
        )

        next_step = (
            f'<span class="rd-next">след. шаг → написать по {len(listings)} объектам и сверить ставку</span>'
            if listings
            else '<span class="rd-next">след. шаг → расширить поиск помещений по району</span>'
        )

        html(
            f"""
            <div class="rd-result">
                <div class="rd-result-main">
                    <div class="tag">Вердикт · {escape(business_type)} · {escape(city)}</div>
                    <strong>{escape(top_candidate.district)} — {escape(verdict)}</strong>
                    <p>Лучшая стартовая зона под формат. Критичные факторы: {escape(str(profile["critical"]))}. Ниже — реальные объекты аренды, проходящие первичную проверку.</p>
                    {next_step}
                </div>
                <div class="rd-mini">
                    <div class="rd-mini-row"><span>спрос</span><strong>{top_candidate.demand}/100</strong></div>
                    <div class="rd-mini-row"><span>конкуренция</span><strong>{top_candidate.competition}/100</strong></div>
                    <div class="rd-mini-row"><span>трафик</span><strong>{top_candidate.traffic}/100</strong></div>
                    <div class="rd-mini-row"><span>помещений в выдаче</span><strong>{len(listings)}</strong></div>
                </div>
            </div>
            <div class="rd-listings">{listing_rows}</div>
            <div class="rd-rank">{rank_rows}</div>
            """
        )


def render_usp() -> None:
    html(
        """
        <section class="rd-section" id="usp">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">УТП</div>
                    <h2 class="rd-section-title">Не слой данных, а <em>готовое решение</em></h2>
                </div>
                <p>Ключевое отличие — балл и объяснение, почему конкретное доступное помещение подходит конкретному типу бизнеса.</p>
            </div>
            <div class="rd-grid-3">
                <div class="rd-card amber"><div class="tag">движок решений</div><strong>Топ объектов, а не сводка</strong><p>Пользователь получает ранжирование, причины, риски и следующий шаг — без аналитика в штате.</p></div>
                <div class="rd-card teal"><div class="tag">парсер аренды</div><strong>Помещения прямо в выдаче</strong><p>Система подтягивает объявления аренды и проверяет площадь, ставку, формат, витрину и риск входа.</p></div>
                <div class="rd-card"><div class="tag">для малого офлайна</div><strong>Не корпоративная аналитика</strong><p>Интерфейс и цена рассчитаны на предпринимателя с 1–3 точками, а не на корпоративный отдел.</p></div>
            </div>
        </section>
        """
    )


def render_market() -> None:
    html(
        """
        <section class="rd-section" id="market">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Размер рынка</div>
                    <h2 class="rd-section-title">Точек открывается <em>больше</em>, чем кто-то успевает считать локации</h2>
                </div>
                <p>Чем больше новых кофеен, салонов и магазинов, тем больше разовых решений о локации — и людей, которым нужен быстрый ответ перед арендой.</p>
            </div>
            <div class="rd-stats">
                <div class="rd-stat"><b>273,5 млрд ₽</b><span>оборот рынка кофеен и кафе-кондитерских РФ за 2025 год, рост ~22% за год.</span></div>
                <div class="rd-stat"><b>249 тыс.</b><span>точек общепита в РФ на конец 2024 года против 198 тыс. в 2020-м.</span></div>
                <div class="rd-stat"><b>76 400</b><span>салонов красоты и барбершопов в РФ, +12% год к году по геоданным.</span></div>
            </div>
            <div class="rd-grid-3" style="margin-top:14px;">
                <div class="rd-card"><div class="tag">TAM</div><strong>Все офлайн-точки услуг и торговли</strong><p>Тысячи кофеен, салонов, барбершопов и магазинов открываются и переезжают в городах РФ ежегодно.</p></div>
                <div class="rd-card teal"><div class="tag">SAM</div><strong>1–3 точки без аналитики</strong><p>Сегмент без аналитической команды, где цена ошибки выше готовности платить за корпоративную геоаналитику.</p></div>
                <div class="rd-card amber"><div class="tag">SOM · пилот</div><strong>3 города, 2 ниши</strong><p>Москва, Петербург, Казань — кофейни и салоны красоты. Цель года: сотни платных отчётов и первые пилоты с сетями.</p></div>
            </div>
            <p class="rd-src">источники: РБК Исследования рынков и открытые геоданные сервисов карт, 2025 · цифры — ориентир масштаба, не прогноз выручки RealDemand.</p>
        </section>
        """
    )


def render_competition() -> None:
    html(
        """
        <section class="rd-section" id="rivals">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Конкуренты и альтернативы</div>
                    <h2 class="rd-section-title">Против Яндекс, Сбер и <em>Геоинтеллект</em></h2>
                </div>
                <p>Сильные геоаналитические платформы. Наша ставка — узкий сценарий для малого бизнеса: довести не до района, а до конкретного доступного помещения.</p>
            </div>
            <div class="rd-table">
                <div class="rd-trow head">
                    <div class="rd-tcell">Игрок</div>
                    <div class="rd-tcell">Что даёт</div>
                    <div class="rd-tcell">Ограничение</div>
                    <div class="rd-tcell">Где выигрываем</div>
                </div>
                <div class="rd-trow">
                    <div class="rd-tcell"><strong>Яндекс Геоаналитика</strong>геоданные карт</div>
                    <div class="rd-tcell">Трафик, демография, организации и поисковые запросы по категориям.</div>
                    <div class="rd-tcell">Сильный анализ территории, но не сценарий под выбор конкретного арендного объекта.</div>
                    <div class="rd-tcell win">Парсинг объявлений, проверка помещения и путь до выбора объекта.</div>
                </div>
                <div class="rd-trow">
                    <div class="rd-tcell"><strong>Сбер Геоаналитика</strong>оценка локаций</div>
                    <div class="rd-tcell">Покупатели, конкуренты, трафик, недвижимость, прогноз спроса и оборота.</div>
                    <div class="rd-tcell">Мощная корпоративная платформа с индивидуальной ценой и широкими задачами.</div>
                    <div class="rd-tcell win">Лёгкий продукт для первого выбора, разового отчёта и быстрого запуска.</div>
                </div>
                <div class="rd-trow">
                    <div class="rd-tcell"><strong>Геоинтеллект</strong>геомаркетинг и ГИС</div>
                    <div class="rd-tcell">Геоотчёты, модели зон пригодности, кейсы для сетей, ритейла и государства.</div>
                    <div class="rd-tcell">Зрелое решение для сложных задач — избыточно для предпринимателя с 1–3 точками.</div>
                    <div class="rd-tcell win">Самостоятельный выбор помещения и объяснимая рекомендация под формат.</div>
                </div>
            </div>
        </section>
        """
    )


def render_money() -> None:
    html(
        """
        <section class="rd-section" id="money">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">Монетизация</div>
                    <h2 class="rd-section-title">Редкое решение — <em>дорогая</em> разовая покупка</h2>
                </div>
                <p>Локацию выбирают не каждый день, поэтому первая покупка — разовый отчёт по объектам. Сети и франшизы выбирают регулярно — им подходит подписка и продажи сетям.</p>
            </div>
            <div class="rd-grid-3">
                <div class="rd-price feature"><div class="tag">разовый отчёт</div><b>4 900 ₽</b><p>Район и 5–10 помещений: балл, конкуренты, спрос, ставка аренды, риски и объяснение.</p></div>
                <div class="rd-price"><div class="tag">подписка · малый бизнес</div><b>5 000–50 000 ₽/мес</b><p>Мониторинг объявлений, сравнение адресов, сохранение сценариев и выгрузка.</p></div>
                <div class="rd-price"><div class="tag">сети · франшизы</div><b>от 149 000 ₽</b><p>Пакеты городов, доступ по API, командные роли, мониторинг объектов и настраиваемые веса модели.</p></div>
            </div>
            <div class="rd-grid-4" style="margin-top:14px;">
                <div class="rd-card"><div class="tag">почему 4 900 ₽</div><strong>Якорь — цена ошибки</strong><p>В 200+ раз дешевле потерь от неверной аренды и дешевле разового консультанта.</p></div>
                <div class="rd-card"><div class="tag">почему подписка</div><strong>Повтор</strong><p>Для тех, кто открывает несколько точек подряд.</p></div>
                <div class="rd-card"><div class="tag">маржа</div><strong>Растёт</strong><p>После автоматизации парсинга себестоимость отчёта падает.</p></div>
                <div class="rd-card"><div class="tag">расширение</div><strong>Доступ по API</strong><p>Данные встраиваются в процессы сетей и франшиз.</p></div>
            </div>
        </section>
        """
    )


def render_mvp() -> None:
    html(
        """
        <section class="rd-section" id="mvp">
            <div class="rd-section-head">
                <div>
                    <div class="rd-eyebrow">MVP · метрики · риски</div>
                    <h2 class="rd-section-title">MVP проверяет не карту, а <em>готовность платить</em></h2>
                </div>
                <p>Запуск узкий: 2 ниши, 3 города, полуавтоматический сбор геоданных и парсинг объявлений коммерческой аренды.</p>
            </div>
            <div class="rd-grid-3">
                <div class="rd-card teal"><div class="tag">mvp</div><strong>Кофейни и салоны красоты</strong><p>Ниши с высокой зависимостью от места и понятными требованиями к помещению.</p></div>
                <div class="rd-card"><div class="tag">данные</div><strong>Геосигналы + аренда</strong><p>Районные факторы, конкуренты и открытые объявления коммерческой недвижимости.</p></div>
                <div class="rd-card amber"><div class="tag">ресурсы</div><strong>1,2–1,8 млн ₽</strong><p>3 месяца: продукт, разработка, парсер, данные, дизайн, первые продажи и интервью.</p></div>
            </div>
            <div class="rd-grid-4" style="margin-top:14px;">
                <div class="rd-card"><div class="idx">М01</div><strong>Конверсия в платный отчёт</strong><p>Доля купивших отчёт после демо.</p></div>
                <div class="rd-card"><div class="idx">М02</div><strong>Уверенность в решении</strong><p>Готовность показать отчёт партнёру или инвестору.</p></div>
                <div class="rd-card"><div class="idx">М03</div><strong>Контакты по объектам</strong><p>Доля отчётов, после которых связались с арендодателем.</p></div>
                <div class="rd-card"><div class="idx">М04</div><strong>Калибровка модели</strong><p>Сходимость балла с фактами по открытым точкам.</p></div>
            </div>
            <div class="rd-grid-2" style="margin-top:14px;">
                <div class="rd-card coral"><div class="tag">риски</div><strong>Данные, копирование, юридика, цикл продаж</strong><p>Объявления дублируются и устаревают, крупные игроки могут скопировать аналитический слой, парсинг чужих площадок несёт юридический риск, а сделки с сетями закрываются медленно.</p></div>
                <div class="rd-card teal"><div class="tag">как снижаем</div><strong>Гибрид данных, юр-проверка, разные циклы</strong><p>Несколько источников и удаление дублей; открытые и партнёрские данные вместо агрессивного сбора с чужих площадок; объяснимый балл против копирования; короткий разовый отчёт кормит компанию, пока зреют пилоты с сетями.</p></div>
            </div>
        </section>
        """
    )


def render_investment() -> None:
    html(
        """
        <section class="rd-section" id="invest">
            <div class="rd-final">
                <span class="rd-tick tl"></span><span class="rd-tick tr"></span>
                <span class="rd-tick bl"></span><span class="rd-tick br"></span>
                <div>
                    <div class="rd-eyebrow">Инвесторам</div>
                    <h2>Почему в RealDemand стоит <em>поверить</em></h2>
                    <p>Рынок офлайн-бизнеса большой, цена ошибки локации высокая, а инструменты чаще показывают данные, чем помогают выбрать помещение. Мы стартуем с платного отчёта по объектам и растём в подписку, продажи сетям и интеграции по API.</p>
                    <div class="rd-roadmap">
                        <span>01 → 3 города, 2 ниши</span>
                        <span>02 → подписка для сетей 1–3 точек</span>
                        <span>03 → интеграции по API и решения под брендом партнёра</span>
                    </div>
                </div>
                <div class="rd-final-box">
                    <div class="tag">следующий шаг</div>
                    <strong>20 отчётов с объектами аренды и 3 пилота с сетями за 3 месяца</strong>
                    <a class="rd-btn" href="mailto:team@realdemand.example">Написать команде →</a>
                </div>
            </div>
        </section>
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="RealDemand — гео-оценка локаций для офлайн-бизнеса",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    render_css()
    render_nav()
    render_hero()
    render_problem()
    render_audience()
    render_architecture()
    render_demo()
    render_usp()
    render_market()
    render_competition()
    render_money()
    render_mvp()
    render_investment()


if __name__ == "__main__":
    main()