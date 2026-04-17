# Comprehensive Astrology Report: Synthesis Algorithm Plan

## 1. Vision and Objective
The goal is to create the **best astrology report ever**. Currently, most astrology reports (including our V1 implementation) rely on static lookup tables (e.g., "Mars in 10th House means X"). 
However, real astrology is about **synthesis**. The person’s actual experience depends on a combination of factors: House, Rashi, Planet, Drishti (Aspects), Degrees (Avasthas), Divisional Charts (D9, D10), and Timing (Dasha/Panchang).

Taking inspiration from our **Heatmap Algorithm** (which uses a weighted composite scoring system across Shadbala, Ashtakavarga, Gochara, Yogas, etc.), we will build a **Narrative Synthesis Engine** that calculates the true outcome of specific life areas.

---

## 2. Core Philosophy: The Tag-Based Synthesis Engine
Instead of just printing isolated paragraphs, the algorithm will evaluate multiple astrological variables, score them against predefined **Narrative Tags**, and select the highest-scoring outcomes to construct the final prediction.

### Example: Career Synthesis (10th House)
If Mars is in the 10th house, it suggests a technical/military career. But if the 10th Lord is in the 8th house (sudden changes/research) and Saturn aspects the 10th house (delays/hard work), the prediction must merge these.

**Algorithm Flow for a Life Domain (e.g., Career):**
1. **Bhava (House) Analysis**: Which sign is the 10th house? Which planets occupy it?
2. **Bhava Lord Analysis**: Where is the 10th Lord placed? What is its Shadbala? Is it combust/retrograde?
3. **Drishti (Aspects)**: Which planets aspect the 10th house and the 10th Lord?
4. **Karaka Analysis**: Analyze the natural significators (e.g., Saturn/Sun/Mercury/Jupiter for Career).
5. **Divisional Chart Confirmation**: Analyze the D10 (Dasamsa) Lagna and 10th house.
6. **Tag Scoring**: Add points to tags like `career_technical`, `career_medical`, `career_business`, `career_struggle`, `career_fame`. 
7. **Narrative Generation**: Select the top 3 tags and fetch their associated highly specific, translated text blocks.

---

## 3. Data Layers Required for the Algorithm

### Layer 1: Core Dispositions (Currently Implemented)
- **Lagna & Moon Sign**: Foundational personality.
- **Planetary Placements**: Planets in Houses and Signs.
- **Shadbala**: True strength of planets.
- **Special Conditions**: Retrograde (Vakri), Combust (Asta), Mangal Dosha, Kaal Sarp.
- **Yogas**: Combinations of planets.

### Layer 2: Advanced Modifiers (Needs Implementation/Expansion)
- **Drishti (Aspects)**: 
  - All planets aspect the 7th house from themselves.
  - Mars aspects 4th and 8th.
  - Jupiter aspects 5th and 9th.
  - Saturn aspects 3rd and 10th.
- **Avasthas (Degrees)**: Based on the exact degree of a planet in a sign, it is in Infant (Bala), Youth (Yuva), Old (Vriddha), or Dead (Mrita) state. This determines if the planet can actually deliver its results.
- **Conjunction Closeness (Graha Yuddha/Moudhya)**: How close are planets in degrees? (Partially done via Graha Yuddha).

### Layer 3: Divisional Confirmation (Needs Narrative Mapping)
- **D9 (Navamsa)**: True strength of planets, soul's purpose, and marriage partner details. (We have D9 calculation, but need to map it to narrative text).
- **D10 (Dasamsa)**: Granular career predictions.

### Layer 5: Micro-Timing & Exact Promises (KP Astrology System)
- **Cuspal Sub-Lords**: The ultimate promise of an event. E.g., The 7th Cusp Sub-Lord dictates if marriage is promised. If its Star-Lord signifies 2, 7, 11, marriage happens.
- **Planet's Star-Lord (Nakshatra Swami)**: A planet gives the results of its Star-Lord first. This is crucial for pinpoint accuracy.

### Layer 6: Soul's Purpose & Material Status (Jaimini System)
- **Chara Karakas**: Atmakaraka (Soul's desire), Amatyakaraka (Career driver), Darakaraka (Spouse).
- **Arudha Lagna (AL)**: How the world perceives the native. E.g., AL in 10th house = Famous/Public figure.
- **Upapada Lagna (UL)**: Reality of marriage and spouse's family.

### Layer 7: Destiny Triggers & Nadi Principles
- **Bhrigu Bindu**: The mathematical destiny point (midpoint of Moon and Rahu). Transits over this point trigger massive life events.
- **Nadi Linkages**: Planetary trines (1-5-9 axis) and adjacencies (2-12 axis). E.g., Jupiter trine Mars = Engineer/Surgeon signature, regardless of houses.
- **Double Transit Theory (K.N. Rao)**: Events occur ONLY when Jupiter and Saturn simultaneously aspect a relevant house/lord.

### Layer 8: 3D Holistic Reading (Sudarshana Chakra)
- **Triple Ascendant View**: Reading the life event simultaneously from Lagna (Physical), Moon (Mental), and Sun (Soul). If an event is promised in all three, it is a 100% certainty.

### Layer 9: Hyper-Personalized Remedial Matrix
- **Gemstone Prescription**: Dynamically calculate the safest, most beneficial gemstone (avoiding lords of 6, 8, 12).
- **Rudraksha & Mantras**: Specific Mukhi Rudrakshas and exact Beej Mantras with chanting counts based on Shadbala deficits.
- **Astro-Vastu**: Identifying lucky directions for the native's home/office based on the strongest planets.

---

## 4. The "Best Report" Algorithm (Step-by-Step)

To generate the final PDF report, the engine will run the following steps:

### Step 1: Compute Base & Elite Metrics
Calculate planetary degrees, KP Sub-Lords, Jaimini Karakas, Arudha Lagna, Bhrigu Bindu, D9/D10, aspects, Nakshatra Padas, and Avasthas.

### Step 2: Domain-Specific Synthesis Runs (The "Jury" System)
For each life domain (e.g., Career), the algorithm holds a "Jury Vote":
1. **Parashari Vote**: 10th Lord + House + Aspects + D10.
2. **KP Vote**: 10th Cusp Sub-Lord's Star-Lord significations.
3. **Jaimini Vote**: Amatyakaraka placement + Arudha Lagna influence.
4. **Nadi Vote**: Planets trine to Saturn (Nadi Karaka for Karma).

*Result*: The engine tallies the votes. If 3 out of 4 systems promise "Business", the narrative outputs a highly confident, translated text: *"Astrological synthesis strongly indicates entrepreneurship..."*

### Step 3: Pinpoint Timeline Integration
- **Vimshottari Dasha**: Defines the broad chapter.
- **Double Transit Trigger**: Scans the next 2-3 years to find the exact month Jupiter and Saturn aspect the domain's house, giving the user a highly specific "Golden Window".
- **Panchang & Gochara**: Fine-tunes to the daily level.

### Step 4: The 360° Remedial Output
- Cross-reference afflictions with Lal Kitab.
- Add Vedic Gemstone/Rudraksha guidelines (with strict safety checks).
- Provide Astro-Vastu alignment tips.

---

## 5. What Needs to be Built Next

To transition from the current "Dictionary Lookup" report to this "World-Class Synthesis Algorithm", we need to build:

1. **`app/astrology/drishti.py`**: A module to calculate exact aspects between planets and houses.
2. **`app/astrology/avasthas.py`**: Planetary states based on degrees (Bala, Kumara, Yuva, Vriddha, Mrita) and Lajjitadi Avasthas.
3. **`app/astrology/nadi.py` & `advanced_jaimini.py`**: Trine linkages and Arudha/Upapada Lagna calculators.
4. **`app/astrology/remedies_pro.py`**: Gemstone, Rudraksha, and Vastu calculator.
5. **`app/services/synthesis_engine.py`**: The core ML/Tag-based scoring engine that aggregates the Parashari, KP, Jaimini, and Nadi "votes" to output the single most accurate narrative prediction for a life domain.

By implementing this, the report will no longer just say "Mars is in the 10th house". It will say: *"Because Mars is in the 10th house, aspected by Jupiter, and the 10th lord is strong in D10, you are destined for an executive role in engineering or real estate, and your success will peak during your Youth."*

---

## 6. Phase 7 Shipped Capabilities (v2.0 Update)

The v2.0 Algorithm Upgrade successfully transitioned the predictive engine to the new **World-Class Synthesis Engine Model**:
1. **Dynamic Domain Scoring**: The core report narrative now uses the `score_domain()` logic to calculate life domain outcomes using 5 independent votes (**Parashari, Jaimini, Nadi, KP, and Bhrigu**).
2. **10 Distinct Life Domains**: Expanded coverage to Career, Wealth, Marriage, Health, Education, Children, Property, Spirituality, Legal, and Travel.
3. **Dasha-Domain Matrix**: Implemented the dynamic `Maha/Antar/Pratyantar` matrix which maps current dasha lord signatures and transit quality over all 10 life domains in a comprehensive table.
4. **Confidence Tracks**: The UI tracking uses a signal agreement ratio (`confidence` / `panchang_score`) across the entire heatmap to separate consistent vs noisy windows. Low confidence is visually distinct to prevent over-reliance on unstable periods.
