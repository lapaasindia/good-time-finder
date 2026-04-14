# Life Predictor — Full Architecture Plan

## Vision

A complete Vedic astrology **Life Predictor** engine in Python.

Goes beyond muhurtha (auspicious timing) into:
- natal chart reading
- dasha/antardasha timing engine
- planetary strength (Shadbala)
- transit scoring (Gochara + Ashtakavarga)
- yoga detection
- per-category life predictions

---

## System Layers

```
┌─────────────────────────────────────────────────────┐
│                   API / UI Layer                    │
│     FastAPI routes: /natal, /predict, /find         │
├─────────────────────────────────────────────────────┤
│                 Services Layer                      │
│   LifePredictorService   GoodTimeFinderService      │
├─────────────────────────────────────────────────────┤
│                  Core Layer                         │
│  DashaEngine  YogaEngine  RankingEngine  Engine     │
├─────────────────────────────────────────────────────┤
│                  Rules Layer                        │
│  Travel  Marriage  Career  Finance  Health  ...     │
├─────────────────────────────────────────────────────┤
│               Astrology Layer                       │
│  calculations  shadbala  gochara  dasha  yogas      │
│  ashtakavarga                                       │
└─────────────────────────────────────────────────────┘
```

---

## Categories

| Tag           | Domain                              |
|---------------|-------------------------------------|
| `general`     | Universal muhurtha indicators       |
| `travel`      | Journeys, relocation                |
| `marriage`    | Marriage, partnerships              |
| `career`      | Job, business, promotions           |
| `finance`     | Investments, loans, wealth          |
| `health`      | Medical procedures, surgery         |
| `education`   | Exams, admission, new study         |
| `property`    | Buying/selling property             |
| `children`    | Conception, childbirth              |
| `spirituality`| Spiritual practice, initiation      |
| `legal`       | Court cases, legal proceedings      |

---

## New Astrological Systems

### 1. Shadbala (Planetary Strength)
Six sources of planetary strength combined into a total score per planet.

| Bala        | Description                                 |
|-------------|---------------------------------------------|
| Sthana Bala | Positional strength (own sign, exaltation)  |
| Dig Bala    | Directional strength by house               |
| Kala Bala   | Temporal strength (day/night, hora, etc.)   |
| Chesta Bala | Motional strength (retrograde, slow)        |
| Naisargika Bala | Natural strength (fixed hierarchy)     |
| Drik Bala   | Aspect strength from other planets          |

**Usage**: Strong benefic planets active in a time period boost scores.

---

### 2. Gochara (Transit Scoring)
Evaluates current planetary transits relative to the **natal Moon sign**.

Classical Vedic gochara tables define which houses from natal Moon are good/bad for each planet.

| Planet   | Good Houses (from natal Moon) |
|----------|-------------------------------|
| Sun      | 3, 6, 10, 11                 |
| Moon     | 1, 3, 6, 7, 10, 11           |
| Mars     | 3, 6, 11                     |
| Mercury  | 2, 4, 6, 8, 10, 11           |
| Jupiter  | 2, 5, 7, 9, 11               |
| Venus    | 1, 2, 3, 4, 5, 8, 9, 11, 12 |
| Saturn   | 3, 6, 11                     |
| Rahu     | 3, 6, 11                     |

**Usage**: Transit score = sum of good-house transits minus bad-house transits.

---

### 3. Ashtakavarga (Transit Strength Grid)
Each planet has a bindu (point) grid across 12 signs, scored 0–8.
When a transiting planet is in a sign with high bindus, it is stronger.

Simplified version: use a fixed bindu table per planet based on natal chart.

---

### 4. Vimshottari Dasha System
120-year planetary period cycle based on natal Moon nakshatra.

| Planet  | Years |
|---------|-------|
| Ketu    | 7     |
| Venus   | 20    |
| Sun     | 6     |
| Moon    | 10    |
| Mars    | 7     |
| Rahu    | 18    |
| Jupiter | 16    |
| Saturn  | 19    |
| Mercury | 17    |

Three levels: **Mahadasha → Antardasha → Pratyantardasha**

**Usage**: The active dasha planets heavily influence which life areas are activated.

---

### 5. Yogas (Planetary Combinations)
Specific combinations of planet positions that indicate life themes.

Categories:
- **Wealth Yogas** (Dhana Yoga): e.g. lords of 2nd and 11th conjunct
- **Raja Yogas**: e.g. lord of Kendra conjunct lord of Trikona
- **Spiritual Yogas** (e.g. Sanyasa Yoga)
- **Career Yogas** (e.g. strong 10th lord)
- **Health Yogas** (e.g. 6th lord afflicted)
- **Relationship Yogas** (e.g. strong Venus + 7th house)

---

## Scoring Architecture

### Multi-dimensional score per time window

```
FinalScore = (
    rule_score         * 1.0   # muhurtha rules (nature: good/bad)
  + shadbala_bonus     * 0.5   # strength of active planets
  + gochara_score      * 0.8   # transit score vs natal Moon
  + dasha_bonus        * 1.2   # bonus if dasha favors the category
  + yoga_score         * 1.0   # active yogas relevant to category
  + ashtakavarga_bonus * 0.3   # bindu strength at transit point
)
```

### Per-category ranking models

Each category has its own weight vector:

| Category   | Dasha Weight | Gochara Weight | Shadbala Weight | Rule Weight |
|------------|-------------|----------------|-----------------|-------------|
| career     | 1.5         | 0.8            | 1.0             | 0.7         |
| finance    | 1.2         | 1.0            | 0.8             | 0.8         |
| health     | 0.8         | 1.2            | 1.5             | 1.0         |
| marriage   | 1.0         | 1.0            | 0.8             | 1.2         |
| travel     | 0.5         | 0.6            | 0.5             | 1.5         |
| education  | 1.2         | 0.8            | 1.0             | 1.0         |
| spirituality | 0.8       | 0.6            | 0.6             | 1.2         |

---

## Final Project Structure

```
good_time_finder/
├── pyproject.toml
├── README.md
├── PLAN.md
├── app/
│   ├── api/
│   │   └── main.py                  ← All routes
│   ├── astrology/
│   │   ├── calculations.py          ← Swiss Ephemeris base
│   │   ├── shadbala.py              ← Planetary strength
│   │   ├── gochara.py               ← Transit scoring
│   │   ├── dasha.py                 ← Vimshottari dasha
│   │   ├── yogas.py                 ← Yoga detection
│   │   └── ashtakavarga.py          ← Bindu grid
│   ├── config/
│   │   ├── __init__.py              ← YAML loader
│   │   └── events.yaml              ← All categories
│   ├── core/
│   │   ├── enums.py
│   │   ├── models.py
│   │   ├── scoring.py               ← Multi-dim scoring
│   │   ├── windows.py
│   │   ├── engine.py                ← Rule evaluation engine
│   │   ├── yoga_engine.py           ← Yoga evaluation
│   │   ├── dasha_engine.py          ← Dasha period engine
│   │   └── ranking.py               ← Per-category ranking
│   ├── rules/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── travel.py
│   │   ├── marriage.py
│   │   ├── general.py
│   │   ├── career.py                ← NEW
│   │   ├── finance.py               ← NEW
│   │   ├── health.py                ← NEW
│   │   ├── education.py             ← NEW
│   │   ├── property.py              ← NEW
│   │   ├── children.py              ← NEW
│   │   ├── spirituality.py          ← NEW
│   │   └── legal.py                 ← NEW
│   └── services/
│       ├── finder.py                ← Good time finder
│       └── life_predictor.py        ← Life prediction orchestrator  ← NEW
└── tests/
    ├── test_rules.py
    ├── test_scoring.py
    ├── test_windows.py
    ├── test_api.py
    ├── test_shadbala.py             ← NEW
    ├── test_gochara.py              ← NEW
    ├── test_dasha.py                ← NEW
    └── test_yogas.py                ← NEW
```

---

## API Routes

| Method | Route              | Description                                 |
|--------|--------------------|---------------------------------------------|
| GET    | /health            | Health check                                |
| POST   | /natal             | Compute natal chart, yogas, shadbala        |
| POST   | /dashas            | Get dasha timeline for a person             |
| POST   | /gochara           | Get transit scores for a date range         |
| POST   | /find              | Good Time Finder (muhurtha windows)         |
| POST   | /predict           | Full life prediction for a category + range |

---

## Life Prediction Response Shape

```json
{
  "category": "career",
  "person": "Rahul",
  "time_range": { "start": "...", "end": "..." },

  "active_dashas": [
    { "mahadasha": "Jupiter", "antardasha": "Saturn", "start": "...", "end": "..." }
  ],

  "yogas": [
    { "name": "RajaYoga", "strength": 0.85, "description": "..." }
  ],

  "gochara_score": 4.2,
  "shadbala_summary": {
    "Jupiter": 1.4,
    "Saturn": 0.8,
    "Sun": 1.1
  },

  "windows": [
    {
      "start": "...", "end": "...",
      "score": 8.4, "rank": 42.0,
      "nature": "good",
      "active_events": ["StrongJupiterCareer", "GoodLunarDayForCareer"],
      "dasha_active": ["Jupiter/Saturn"],
      "yogas_active": ["RajaYoga"]
    }
  ],

  "top_windows": [ ... ],
  "overall_period_score": 6.8,
  "narrative": "Jupiter mahadasha is active. Strong gochara in 10th house..."
}
```

---

## Implementation Order

1. `astrology/dasha.py` — Vimshottari engine
2. `astrology/shadbala.py` — Simplified planetary strength
3. `astrology/gochara.py` — Transit house scoring
4. `astrology/yogas.py` — Yoga detection
5. `astrology/ashtakavarga.py` — Bindu scoring
6. `core/dasha_engine.py` — Active dasha at any datetime
7. `core/yoga_engine.py` — Active yogas for a person
8. `core/ranking.py` — Per-category weighted ranking
9. `core/scoring.py` — Update for multi-dim scoring
10. `rules/career.py`, `finance.py`, `health.py`, `education.py`, `property.py`, `children.py`, `spirituality.py`, `legal.py`
11. `config/events.yaml` — Expand with all new rules
12. `rules/registry.py` — Register all new rules
13. `services/life_predictor.py` — Unified orchestrator
14. `api/main.py` — Add new routes
15. Tests for all new modules
