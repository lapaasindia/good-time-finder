# Data Collection PRD — 10,000 Personality Life Events

**Status:** Draft
**Owner:** AI Data Agent
**Objective:** Collect 10,000 structured life events from popular personalities with accurate birth data to train, refine, and backtest the Life Predictor ML model.

## 1. Problem Statement
To refine the Random Forest model and ensure the newly introduced astrological factors (KP, Bhrigu, etc. in `ALGO_UPGRADE_PRD` v2.0) work robustly, we need a massive, high-quality dataset of life events. The current backtest baseline has 391 events. We need to scale this to **10,000 accurate, categorized life events** from popular personalities.

## 2. Goals
- Collect accurate natal details (Date, Time, Lat, Lon, Timezone) for popular personalities.
- Extract major life events for each personality with exact or approximate dates.
- Map each event to one of the 15 system categories (`career`, `finance`, `health`, `marriage`, `education`, etc.).
- Produce structured output (CSV/JSON) ready for ML ingestion and backtesting.

## 3. Data Sources
- **Astro-Databank (astro.com)**: Primary source for accurate birth data (Aim for Rodden Rating A or AA) and related life events.
- **Wikidata / Wikipedia**: To extract comprehensive life event dates (marriages, promotions, accidents, legal issues) to augment Astro-Databank events.

## 4. Target Schema

### 4.1 Personality Data (`personalities.json` or `.csv`)
| Field | Type | Description |
|-------|------|-------------|
| `person_id` | String | Unique identifier (e.g., `P0001`) |
| `name` | String | Name of the personality |
| `birth_date` | YYYY-MM-DD | Exact birth date |
| `birth_time` | HH:MM | Exact birth time (local) |
| `timezone` | String | Timezone string or offset (e.g., "America/New_York", or offset format) |
| `latitude` | Float | Birth location latitude |
| `longitude` | Float | Birth location longitude |
| `rodden_rating` | String | Must be 'A' or 'AA' to ensure accuracy |

### 4.2 Event Data (`events.json` or `.csv`)
| Field | Type | Description |
|-------|------|-------------|
| `event_id` | String | Unique identifier |
| `person_id` | String | Reference to the personality |
| `event_date` | YYYY-MM-DD | Date of the transit/event |
| `category` | String | Must map exactly to our algorithm categories (see 4.3) |
| `polarity` | Integer | +1 (Positive/Gain) or -1 (Negative/Loss/Challenge) |
| `description` | String | Brief description (e.g., "Won Academy Award", "Car accident") |

### 4.3 Category Mapping
Events must be strictly mapped to the following categories established in `ALGO_UPGRADE_PRD`:
- `career` (e.g., elected, promoted, debut)
- `finance` (e.g., bankruptcy, major contract signing)
- `health` (e.g., diagnosed with illness, surgery)
- `marriage` (e.g., wedding day)
- `education` (e.g., graduated university)
- `children` (e.g., birth of a child)
- `property` (e.g., bought mansion, house fire)
- `spirituality` (e.g., ordained, spiritual awakening)
- `legal` (e.g., arrested, convicted, sued)
- `travel` (e.g., major foreign relocation)
- `business` (e.g., founded company, IPO)
- `relationships` (e.g., divorce, separation)
- `accidents` (e.g., car crash, physical injury)
- `fame` (e.g., won Nobel prize, Oscar)

## 5. Execution Logic for Data Agent

The agent executing this PRD should operate in the following loop:
1. **Target Identification:** Identify individuals with `AA` or `A` Rodden rating data. (Scripting against Astro-Databank wiki is recommended).
2. **Natal Data Extraction:** Parse the birth details: Date, Time (convert to standard HH:MM), and Location (Geocode to Lat/Lon if not explicitly provided).
3. **Event Extraction:** Parse the "Events" section from Astro-Databank, or cross-reference with Wikipedia timelines.
4. **LLM Transformation:** Use an LLM or heuristic mapping to parse the unstructured event text ("M1", "Accident") into a precise `event_date`, `category`, and `polarity`.
5. **Validation:**
   - Exclude any persons where birth time is unknown or speculative (Rating C, DD, XX, etc.).
   - Discard events where the exact date (or at least month/year, if standardizing implies mid-month padding is ok) is unknown. 
6. **Rate Limiting & Continuity:** Implement saving checkpoints every 100 records and handle rate limits (especially if scraping Astro-Databank or Wikipedia natively).

## 6. Success Metrics
- Total unique personalities: ≥ 1,500
- Total life events: ≥ 10,000 (avg 6-7 events per person)
- `rodden_rating` validation: 100% of data is A or AA.
- Category distribution: Ensure no category is empty. At least 50 events in the rarest categories.
