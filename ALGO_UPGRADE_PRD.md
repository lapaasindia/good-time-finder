# Algorithm Upgrade PRD — Heatmap & Report Unification

**Status:** Draft  
**Owner:** Engineering  
**Last Updated:** 2026-04-17  
**Target Release:** v2.0  
**Backtest Baseline:** 70.84% accuracy (277/391 events, linear model)

---

## 0. Problem Statement

The Life Predictor produces two artifacts from the same natal chart:

1. **Heatmap** (`/predict`) — per-slot composite score across a time range.
2. **Report** (`/report`) — narrative PDF covering personality, domains, dashas, remedies.

Today these diverge:

- **KP scoring is frozen** in the heatmap loop (natal values re-used per slot), meaning the #2-highest weighted feature (`kp_cuspal=1.0`) contributes zero dynamic signal.
- **The `SynthesisEngine` has no KP or Bhrigu input**, so the report narrative is Parashari+Jaimini+Nadi only, even though the heatmap claims all four systems drive the prediction.
- **All 15 categories share identical weights** (`CATEGORY_WEIGHTS`), making per-domain tuning non-functional.
- **Three features (`chandra_bala`, `avastha`, `gulika`) have weight 0** — dead code paths.
- **Narrative has 3 bands only** (≥2 / ≥0 / <0), too coarse for a premium report.
- **Only 4 domains synthesized** (career, wealth, marriage, health) out of 10+ category tags.
- **Normalization** mixes absolute `tanh` + relative rank, producing false extremes on charts with flat score distributions.
- **One failing unit test** (`test_negative_inputs_are_still_valid_scores`) — composite escapes the documented `[-3, 3]` range.

## 1. Goals

- G1. **Correctness** — KP and every advanced feature contributes real, per-slot signal.
- G2. **Consistency** — report narrative and heatmap score reflect the same underlying math.
- G3. **Differentiation** — category tuning actually changes rankings.
- G4. **Depth** — report adds a 12-month domain timeline and per-domain "why" breakdown.
- G5. **Quality** — no test regressions; maintain ≥70.84% backtest accuracy.

## 2. Non-Goals

- Re-training or replacing the Random Forest model (stays `USE_ML_MODEL = False`).
- Changing the Swiss Ephemeris backend or Lahiri ayanamsa.
- UI redesign (already shipped in prior v1.x).
- New astrological systems (no Tajaka, no Nadi Amsa, no BCP).

## 3. Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Backtest accuracy | 70.84% | ≥ 70.84% (no regression); stretch 73% |
| Unit tests | 139 pass / 1 fail | 140+ pass / 0 fail |
| KP score variance per window (1-month, hourly) | 0 | > 0.3 std dev |
| Category weight identicality | 15/15 identical | 0 identical (every category unique) |
| Report domains covered | 4 | 10 |
| Synthesis narrative bands | 3 | 5 |
| Heatmap ↔ Report correlation (same domain, same date) | N/A | r ≥ 0.7 |

---

## 4. Architecture Overview

```
                     ┌────────────────────┐
                     │   Natal Context    │
                     │ (planets, houses)  │
                     └─────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌────────────┐        ┌────────────┐       ┌────────────┐
   │ Per-Slot   │        │ Domain     │       │ Static     │
   │ Feature    │        │ Scorer     │       │ Chart      │
   │ Builder    │        │ (shared)   │       │ Signature  │
   └─────┬──────┘        └─────┬──────┘       └─────┬──────┘
         │                     │                    │
         ▼                     ▼                    ▼
   ┌────────────┐        ┌────────────┐       ┌────────────┐
   │ /predict   │        │ /report    │       │ Both       │
   │ heatmap    │        │ narrative  │       │ surfaces   │
   └────────────┘        └────────────┘       └────────────┘
```

**Shared component:** `app/core/domain_scorer.py` (new) — produces a stable per-domain score from any chart+time, consumed by both the heatmap (as a static anchor) and the report (as the synthesis score).

---

## 5. Phases

### ✅ Phase 1 — Bugfix Pass (Zero Behavior Change)

**Goal:** Restore correctness without changing any scoring philosophy. Ship-safe. ~30 min.

#### Logic
- Clamp final composite to `[-3, 3]` at the end of `compute_composite_score` and `batch_composite_scores`.
- Decouple ashtakavarga and panchang into independent feature slots (currently summed before weighting).
- Either delete or repurpose the three zero-weight features; preferred: assign small non-zero weights (`0.1–0.2`) so they contribute noise reduction instead of nothing.

#### Checklist
- [ ] 1.1 Add `max(-3.0, min(3.0, score))` clamp at end of `compute_composite_score` (`app/core/ranking.py:243`).
- [ ] 1.2 Apply same clamp inside `batch_composite_scores` for each row (`app/core/ranking.py:270`).
- [ ] 1.3 Re-run `tests/test_ranking.py::test_negative_inputs_are_still_valid_scores` — expect pass.
- [ ] 1.4 Split feature row in `life_predictor.py:465-472`: replace `s.avarga + s.panchang_s` with two independent slots `s.avarga` and `s.panchang_s`.
- [ ] 1.5 Extend `_feature_row`, `_classical_score_from_row`, `compute_composite_score`, `batch_composite_scores` to 20 features (add `panchang`).
- [ ] 1.6 Add `panchang` to `CategoryWeights` with default `0.2`.
- [ ] 1.7 Restore `chandra_bala=0.25`, `avastha=0.2`, `gulika=0.15` in default `CategoryWeights`.
- [ ] 1.8 Verify `./.venv/bin/pytest` — all 140+ pass.
- [ ] 1.9 Run smoke `/predict` call, confirm composite is within `[-3, 3]`.

---

### ✅ Phase 2 — KP Dynamic Scoring

**Goal:** Make KP respond to actual time-slot transits, not just natal. Highest-impact correctness fix.

#### Logic
- Today `life_predictor.py:440-441` does `kp_score=natal_kp_score, kp_cuspal_score=natal_kp_cuspal`. This is natal-only.
- Change: compute `kp_score(transit_longitudes, natal_lagna, category)` inside the slot loop using `ctx.planet_signs` → longitudes.
- Change: call `true_kp_cuspal_score(category, birth_dt=dt, lat=loc.lat, lon=loc.lon, natal_longs=natal_longitudes, natal_houses=natal_p_houses)` per slot — the `birth_dt=dt` swap is what drives the cusp dynamics (cusps rotate each ~4 min).
- Keep the natal values as separate chart-signature fields: `kp_natal_score`, `kp_natal_cuspal`.

#### Checklist
- [ ] 2.1 In slot loop (`life_predictor.py:351-445`), add `transit_kp = kp_score(transit_longitudes, n_lagna, category)`.
- [ ] 2.2 Add `transit_kp_cuspal = true_kp_cuspal_score(category=category, birth_dt=dt, lat=location.latitude, lon=location.longitude, natal_longs=transit_longitudes, natal_houses=natal_p_houses)`.
  - Clarify: `natal_longs` param here receives transit longs; cusps are computed from `birth_dt=dt` using current location.
- [ ] 2.3 Replace slot scores `kp_score=natal_kp_score` → `kp_score=transit_kp`, `kp_cuspal_score=natal_kp_cuspal` → `kp_cuspal_score=transit_kp_cuspal`.
- [ ] 2.4 Add new `LifePrediction` fields `kp_natal_score: float` and `kp_natal_cuspal: float` (keep existing `kp_score/kp_cuspal_score` as "representative slot" average for the overall period).
- [ ] 2.5 Update `PredictResponse` schema + mapping in `api/main.py`.
- [ ] 2.6 Add `tests/test_kp_dynamic.py`:
  - Build fixed natal, run `predict` over a 1-month hourly range.
  - Assert `std_dev(window.kp_cuspal_score) > 0.3`.
  - Assert at least 3 distinct values of `kp_score`.
- [ ] 2.7 Run full backtest — confirm accuracy ≥ 70.84%.
- [ ] 2.8 If backtest dips, reduce `kp_cuspal` weight from 1.0 to 0.6 and re-run.

---

### ✅ Phase 3 — Category Differentiation

**Goal:** Every category (`career`, `marriage`, `health`, etc.) must weight factors differently.

#### Logic

| Category | Heavy Factors | Light / Negative |
|----------|--------------|------------------|
| career | `dasha`, `kp_cuspal`, `jaimini` (AmK), `rule`, `bhrigu` | `chandra_bala` |
| finance | `dasha`, `rule`, `jupiter gochara`, `double_transit`, `ashtakavarga` | `chandra_bala` |
| health | `shadbala` (lagna lord), `chandra_bala`, `avastha`, `sandhi_penalty` | `jaimini` |
| marriage | `gochara` (7H), `bhrigu`, `yoga`, `venus shadbala` | `gulika` |
| education | `jupiter shadbala`, `mercury shadbala`, `5H gochara`, `rule` | `gulika` |
| children | `jupiter`, `5H/9H gochara`, `bhrigu` | |
| property | `4H gochara`, `saturn/mars strength`, `ashtakavarga` | |
| spirituality | `jupiter`, `ketu strength`, `9H gochara`, `panchang` | `rule` (muhurta less relevant) |
| legal | `10H/6H`, `saturn strength`, `rule`, `sandhi_penalty` | |
| travel | `9H gochara`, `rahu`, `moon strength`, `panchang` | |
| business | same as career + `arudha`, `dhana yoga` | |
| relationships | `venus`, `7H`, `gochara` | |
| accidents | `gulika`, `badhaka`, `sandhi`, `saturn/mars transit` | `bhrigu` |
| fame | `sun shadbala`, `arudha`, `10H` | |
| general | balanced mean of all | |

- Introduce helper `_house_specific_gochara(transit_signs, natal_signs, house_num, moon_sign)` to compute gochara limited to specific houses, plumbed through into the slot loop only when category requires it.
- Introduce `planet_specific_shadbala(shadbala, planet)` pull for per-category planet emphasis.

#### Checklist
- [ ] 3.1 Replace the 15 identical `CategoryWeights` rows with distinct tuned values per table above.
- [ ] 3.2 Add `app/astrology/gochara.py::house_specific_gochara_score(planet_signs, natal_moon, relevant_houses)` for per-category house filtering.
- [ ] 3.3 In `life_predictor.py`, for categories where a specific house matters (e.g. `marriage → 7H`), pass that into gochara scoring and add as a feature column `gochara_house_specific`.
- [ ] 3.4 Add `planet_focus_score` feature that picks the category's primary planet's shadbala (e.g. `marriage → Venus`, `education → Mercury`).
- [ ] 3.5 Update `_feature_row` to include the two new columns; update `CategoryWeights` struct accordingly.
- [ ] 3.6 Add `tests/test_category_differentiation.py`:
  - Same chart+time, run `predict` across all 15 categories.
  - Assert no two categories produce the exact same composite.
  - Assert `marriage` places Venus-strong windows higher than `health` does.
- [ ] 3.7 Run backtest per-category if labels exist, else overall; target no regression.

---

### ✅ Phase 4 — Heatmap ⇄ Report Unification

**Goal:** The same factors that move the heatmap also move the report narrative.

#### Logic
Today the `SynthesisEngine` constructor (`synthesis_engine.py:22-32`) takes `planet_houses`, `planet_signs`, `lagna`, `shadbala`, `drishti`, `avasthas`, `nadi_links`, `chara_karakas` — **no KP, no Bhrigu, no Dasha**.

Refactor:
1. Add a new module `app/core/domain_scorer.py` with a single function:
   ```
   score_domain(category, ctx) → DomainScore
       where DomainScore = { score, factors: list[Factor], confidence }
             Factor = { system, polarity (+/-), weight, english, hindi }
   ```
2. `ctx` contains: `natal_planet_houses`, `natal_planet_signs`, `lagna`, `shadbala`, `drishti`, `avasthas`, `nadi_links`, `chara_karakas`, `kp_natal_score`, `kp_natal_cuspal`, `bhrigu_bindu`, `natal_longs`, `active_maha`, `active_antar`, `sade_sati`.
3. `score_domain` runs five **independent votes**:
   - Parashari (lord strength + aspects on domain house)
   - Jaimini (AmK / DK / PK / AK by domain)
   - Nadi (career signature for career; skip for non-career)
   - KP (cuspal sub-lord vote for the domain house)
   - Bhrigu (Bhrigu Bindu activation)
4. Return weighted sum, with `confidence = agreement_ratio * independent_signal_count`.
5. `SynthesisEngine` becomes a thin wrapper that calls `score_domain` for each of the 10 domains and maps the numeric score + factors to bilingual narrative bands.
6. In `life_predictor.py`, also call `score_domain` once per predict request with a mid-range time, and attach it to `LifePrediction.domain_static_score` — guarantees the report's domain score is visible in the heatmap response too.

#### Checklist
- [ ] 4.1 Create `app/core/domain_scorer.py` with `DomainScore`, `Factor`, `score_domain()`.
- [ ] 4.2 Implement `parashari_vote(category, ctx)`.
- [ ] 4.3 Implement `jaimini_vote(category, ctx)`.
- [ ] 4.4 Implement `nadi_vote(category, ctx)`.
- [ ] 4.5 Implement `kp_vote(category, ctx)` — maps `ctx.kp_natal_cuspal` + uses `true_kp_cuspal_score`.
- [ ] 4.6 Implement `bhrigu_vote(category, ctx)` — uses bhrigu_bindu position + domain house relevance.
- [ ] 4.7 Refactor `SynthesisEngine.synthesize_career/wealth/marriage/health` to delegate to `score_domain`.
- [ ] 4.8 Extend `SynthesisEngine` to cover **10 domains**: career, wealth, marriage, health, education, children, property, spirituality, legal, travel.
- [ ] 4.9 Add `domain_static_scores: dict[str, float]` field to `LifePrediction` dataclass.
- [ ] 4.10 Expose it in `PredictResponse`.
- [ ] 4.11 PDF renders **"Your natal <domain> score: +2.1"** next to **"Next 90-day timing: +1.6"** for side-by-side static vs dynamic view.
- [ ] 4.12 Add `tests/test_domain_scorer.py`:
  - Given a chart with `Jupiter in 10H exalted`, career score ≥ +1.5.
  - Given Saturn+Mars on 7H, marriage score ≤ -1.0.
  - `score_domain("career")` produces ≥ 3 factors in `factors` list.

---

### ✅ Phase 5 — Report Depth Upgrades

**Goal:** Report becomes a deliverable worth paying for.

#### Logic
- **12-Month Timeline per Domain:** reuse the heatmap engine to sample the next 12 months at weekly granularity per domain; extract top-3 peaks and top-3 troughs per domain; render a min chart in PDF.
- **Dasha × Domain Matrix:** for the current `Maha/Antar/Pratyantar`, score each domain's activation (is the dasha lord naturally karaka for that domain?) + the lord's current transit quality. Render as a 10×3 table.
- **5-Band Narrative:** instead of 3 bands (good/neutral/bad), use 5:
  - `score ≥ 2.2` → "Exceptional"
  - `1.0 ≤ score < 2.2` → "Strong"
  - `-0.5 ≤ score < 1.0` → "Moderate"
  - `-1.5 ≤ score < -0.5` → "Strained"
  - `score < -1.5` → "Challenging"
- **"Why this score" breakdown:** per domain, enumerate each vote with its ± contribution in a bulleted list (bilingual).

#### Checklist
- [ ] 5.1 Add `app/services/timeline_builder.py::build_domain_timeline(person, category, months=12)` — returns `[{month, peak_window, trough_window, avg_score}]`.
- [ ] 5.2 Call from `report_generator.py` for each of the 10 domains; cache results to avoid 10× the cost.
- [ ] 5.3 Add PDF section "12-Month Outlook" rendering a horizontal bar per month per domain (green/amber/red).
- [ ] 5.4 Add `app/services/dasha_domain_matrix.py` — table builder.
- [ ] 5.5 Add PDF section "Current Dasha Activation" with 10×3 matrix.
- [ ] 5.6 Update narrative band thresholds (5 bands) in `domain_scorer.py`.
- [ ] 5.7 Add bilingual strings for all 5 × 10 = 50 band narratives.
- [ ] 5.8 PDF: per-domain expandable "Why this score" section showing each Factor (system, polarity, weight, text).
- [ ] 5.9 Update `tests/test_report.py` to snapshot the new sections exist in the generated PDF (byte size > 40KB, contains expected keywords).

---

### ✅ Phase 6 — Normalization & Confidence

**Goal:** Stop generating fake extremes; surface uncertainty.

#### Logic
- Current normalization (`life_predictor.py:484-495`):
  ```
  abs_norm  = 3 * tanh(c / 2.5)
  rel_norm  = clamp(((c - median) / range) * 6, -3, 3)
  hybrid    = 0.7 * abs_norm + 0.3 * rel_norm
  ```
  The `rel_norm` term guarantees some slots reach ±3 even if all raw composites are near zero (flat week).
- Replace with:
  ```
  hybrid = 3 * tanh(c / SCALE)
  where SCALE = 2.0  (tuned so +3 is reached at raw ~6.0, which requires multiple aligned signals)
  ```
- **Confidence:** compute from `n_signals_agreeing / n_signals_total` where each non-zero feature is a "signal", agreeing = same sign as composite. Attach to each `PredictionWindow` and `DomainScore`.
- Low-confidence windows (`confidence < 0.4`) render neutral grey in heatmap regardless of score magnitude.

#### Checklist
- [ ] 6.1 Remove `rel_norm` + `hybrid` blend; replace with single `tanh` in `life_predictor.py:484-495`.
- [ ] 6.2 Calibrate `SCALE` constant: for the 391-event backtest, bucket raw composites to deciles and pick SCALE so deciles 1 and 10 map to ±2.5 (leaves ±3 for true outliers).
- [ ] 6.3 Add `confidence` float to `PredictionWindow` and `DomainScore` dataclasses.
- [ ] 6.4 Compute confidence in `_flush()` and in `score_domain`.
- [ ] 6.5 Expose `confidence` in `PredictResponse`.
- [ ] 6.6 UI: in `life_predictor_ui.html`, if `confidence < 0.4` then render cell neutral grey with "?" tooltip.
- [ ] 6.7 Add `tests/test_normalization.py`:
  - Synthesize raw composites all near 0; assert no normalized value exceeds ±0.5.
  - Synthesize one raw at +6, rest at 0; assert normalized +6 becomes +2.5 to +3.0.
- [ ] 6.8 Backtest check.

---

### ✅ Phase 7 — Verification & Docs

**Goal:** Lock in quality, document the new contract.

#### Checklist
- [ ] 7.1 `tests/test_heatmap_dynamics.py` — per-slot variance check for every feature that's marked "dynamic per-slot".
- [ ] 7.2 `tests/test_report_heatmap_alignment.py` — for 3 sample charts, `report.synthesis.career.score` must correlate with `predict(career).overall_period_score` with r ≥ 0.6.
- [ ] 7.3 Update `README.md` with new API schema.
- [ ] 7.4 Update `REPORT_ALGO_PLAN.md` to reflect what shipped.
- [ ] 7.5 Run full backtest, record new accuracy in memory/docs.
- [ ] 7.6 Smoke: UI → pick chart → view heatmap → export PDF → verify all 10 domains appear, each with "Why" breakdown.
- [ ] 7.7 Deploy.

---

## 6. Data Contracts

### 6.1 New `DomainScore`

```python
@dataclass
class Factor:
    system: Literal["parashari", "jaimini", "nadi", "kp", "bhrigu", "dasha"]
    polarity: int           # -1, 0, +1
    weight: float           # absolute contribution magnitude
    text_en: str
    text_hi: str

@dataclass
class DomainScore:
    category: str
    score: float                    # [-3, 3]
    band: Literal["exceptional", "strong", "moderate", "strained", "challenging"]
    confidence: float               # [0, 1]
    factors: list[Factor]
    summary_en: str
    summary_hi: str
```

### 6.2 Extended `PredictionWindow`

Add:
- `panchang_score: float`  (split out from ashtakavarga)
- `confidence: float`
- `kp_natal_score: float`
- `kp_natal_cuspal: float`

### 6.3 Extended `LifePrediction`

Add:
- `domain_static_scores: dict[str, float]`  (10 entries)
- `domain_confidences: dict[str, float]`

### 6.4 Extended `PredictResponse`

Mirror the above.

---

## 7. Risks

| Risk | Mitigation |
|------|-----------|
| KP per-slot calc is expensive (Swiss Ephemeris cusps at every step) | Cache cusps per (date, lat, lon) at minute resolution; reuse across runs. |
| Backtest regresses after category re-tuning | Per-category tuning pull request must include backtest diff; revert weights if regression > 2%. |
| PDF size explodes with 10 domains × 12-month charts | Use compact horizontal bar glyphs (7×12 chars), not raster images. |
| Report text becomes too long | Cap `factors` list to top-5 per domain, sorted by absolute weight. |
| Confidence field misinterpreted | Tooltip in UI + legend in PDF. |

## 8. Open Questions

- Do we want per-domain confidence thresholds in the PDF (e.g. hide "children" if user is child) or always show all 10?
- Should the heatmap show `composite_score` or `composite_score × confidence`?
- Do we expose `domain_static_scores` in `/predict` or keep it `/report` only?

## 9. Appendix — File Inventory

| Path | Role | Phase |
|------|------|-------|
| `app/core/ranking.py` | linear weights + composite | 1, 3 |
| `app/core/domain_scorer.py` (new) | shared domain scoring | 4 |
| `app/services/life_predictor.py` | heatmap orchestrator | 1, 2, 3, 6 |
| `app/services/synthesis_engine.py` | report narrative | 4 |
| `app/services/report_generator.py` | PDF payload builder | 4, 5 |
| `app/services/pdf_builder.py` | PDF renderer | 5 |
| `app/services/timeline_builder.py` (new) | 12-month domain timeline | 5 |
| `app/services/dasha_domain_matrix.py` (new) | Dasha × Domain table | 5 |
| `app/astrology/kp.py` | KP math | 2 |
| `app/astrology/bhrigu.py` | Bhrigu math | 4 |
| `app/astrology/gochara.py` | transit scoring | 3 |
| `app/api/main.py` | response schemas | 2, 4, 6 |
| `life_predictor_ui.html` | heatmap UI | 6 |
| `tests/test_ranking.py` | weights tests | 1 |
| `tests/test_kp_dynamic.py` (new) | KP dynamics | 2 |
| `tests/test_category_differentiation.py` (new) | category tuning | 3 |
| `tests/test_domain_scorer.py` (new) | domain scorer | 4 |
| `tests/test_heatmap_dynamics.py` (new) | per-slot variance | 7 |
| `tests/test_report_heatmap_alignment.py` (new) | cross-surface correlation | 7 |
| `tests/test_normalization.py` (new) | tanh calibration | 6 |

---

**End of PRD.**
