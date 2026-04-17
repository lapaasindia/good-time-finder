"""
Astrology report generator.

Builds a reader-friendly, plain-English report structure that can be rendered
to JSON or PDF without assuming astrology knowledge.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.astrology.avasthas import compute_all_avasthas
from app.astrology.calculations import (
    build_context,
    moon_constellation,
    natal_lagna,
    natal_moon_sign,
    planet_houses,
    planet_signs,
)
from app.astrology.dasha import compute_antardashas, compute_mahadashas
from app.astrology.drishti import compute_aspects
from app.astrology.extra_yogas import detect_all_extra_yogas
from app.astrology.gochara import _house_from_sign, gochara_score
from app.astrology.houses_info import HOUSE_DATA
from app.astrology.jaimini import compute_chara_karakas
from app.astrology.lal_kitab import get_lal_kitab_remedies
from app.astrology.nadi import compute_nadi_linkages
from app.astrology.personality_info import ZODIAC_PROFILES
from app.astrology.planets_info import PLANET_DATA
from app.astrology.remedies_pro import prescribe_astro_vastu, prescribe_gemstones, prescribe_rudraksha
from app.astrology.sade_sati import compute_sade_sati
from app.astrology.shadbala import benefic_strength_score, lagna_lord_strength, shadbala_summary
from app.astrology.special_conditions import compute_special_conditions, get_raw_longitudes
from app.astrology.yogas import detect_all_yogas
from app.core.models import Person
from app.services.synthesis_engine import SynthesisEngine
from app.core.domain_scorer import DomainScore, ScoringContext


PLANET_PLAIN_MEANINGS: dict[str, str] = {
    "Sun": "identity, confidence, leadership, and visibility",
    "Moon": "emotions, habits, security needs, and intuition",
    "Mars": "drive, courage, conflict response, and initiative",
    "Mercury": "thinking, communication, learning, and business sense",
    "Jupiter": "growth, wisdom, teachers, faith, and long-term perspective",
    "Venus": "love, comfort, beauty, pleasure, and relationship style",
    "Saturn": "discipline, responsibility, patience, and long-term work",
    "Rahu": "ambition, appetite, novelty, foreign influence, and obsession",
    "Ketu": "detachment, inner work, specialization, and spiritual distance",
}

TERM_GUIDE = [
    {
        "term": "Lagna",
        "meaning": "Your rising sign. It describes how you meet life, your natural style, and the kind of situations you keep attracting.",
    },
    {
        "term": "Moon Sign",
        "meaning": "Your emotional operating system. It shows how you process stress, comfort, and day-to-day feelings.",
    },
    {
        "term": "Dasha",
        "meaning": "A timing cycle. Think of it like the long chapter and short chapter currently shaping what themes are louder in life.",
    },
    {
        "term": "Transit",
        "meaning": "Where planets are moving now. Transits change the weather around your natal chart and explain why some periods feel easier or heavier.",
    },
    {
        "term": "Yoga",
        "meaning": "A meaningful planetary combination. Yogas can strengthen certain talents, opportunities, or recurring life patterns.",
    },
    {
        "term": "Shadbala",
        "meaning": "A rough strength score for each planet. Strong planets tend to deliver their results more clearly and consistently.",
    },
    {
        "term": "Dosha",
        "meaning": "A stress pattern or imbalance. It does not mean doom; it usually means a life area that needs maturity, care, or better timing.",
    },
]

DOMAIN_GUIDANCE = {
    "career": {
        "label": "Career & Profession",
        "what_it_means": "work direction, reputation, authority, growth, and the kind of responsibilities you carry in public life",
        "positive": "This area has momentum. Results usually improve when you act steadily, stay visible, and choose long-term positioning over quick wins.",
        "mixed": "This area can work, but timing and consistency matter more than brute force. Progress usually comes in stages rather than all at once.",
        "care": "This area needs patience and better pacing right now. It is wiser to reduce noise, protect energy, and fix weak foundations before forcing expansion.",
        "focus": [
            "Prioritize work that compounds over time.",
            "Choose clarity over urgency in public or career decisions.",
        ],
    },
    "wealth": {
        "label": "Wealth & Finances",
        "what_it_means": "income stability, savings habits, gains, and your ability to turn effort into usable resources",
        "positive": "Financial patterns look constructive. Slow, sensible accumulation is favored more than impulsive speculation.",
        "mixed": "Money can move in the right direction, but only if budgeting and discipline stay stronger than mood or social pressure.",
        "care": "This area needs protection. Leakage, overpromising, or emotional spending can undo progress faster than expected.",
        "focus": [
            "Protect savings and cash flow before chasing upside.",
            "Prefer practical planning over risky bets.",
        ],
    },
    "finance": {
        "label": "Wealth & Finances",
        "what_it_means": "income stability, savings habits, gains, and your ability to turn effort into usable resources",
        "positive": "Financial patterns look constructive. Slow, sensible accumulation is favored more than impulsive speculation.",
        "mixed": "Money can move in the right direction, but only if budgeting and discipline stay stronger than mood or social pressure.",
        "care": "This area needs protection. Leakage, overpromising, or emotional spending can undo progress faster than expected.",
        "focus": [
            "Protect savings and cash flow before chasing upside.",
            "Prefer practical planning over risky bets.",
        ],
    },
    "marriage": {
        "label": "Marriage & Relationships",
        "what_it_means": "partnership, emotional reciprocity, relationship timing, and how you handle closeness and commitment",
        "positive": "This area is more cooperative than usual. Honest communication and shared routines bring faster improvement than dramatic gestures.",
        "mixed": "Relationships can grow, but expectations need regular tuning. Good intentions alone may not be enough without emotional clarity.",
        "care": "This area is more sensitive now. It helps to slow reactions, choose maturity over pride, and avoid forced decisions.",
        "focus": [
            "Name expectations clearly instead of assuming them.",
            "Treat steadiness as more important than intensity.",
        ],
    },
    "health": {
        "label": "Health & Well-being",
        "what_it_means": "energy, recovery, resilience, stress load, and the daily habits that keep you physically and mentally steady",
        "positive": "Vitality looks decent when routines are respected. Consistency matters more than extreme fixes.",
        "mixed": "Health is manageable, but stress can spill into the body quickly. Recovery improves when rest and digestion are not ignored.",
        "care": "This area needs active maintenance. Prevention, sleep, and rhythm matter more than pushing through fatigue.",
        "focus": [
            "Protect sleep, digestion, and recovery windows.",
            "Reduce all-or-nothing habits and favor repeatable routines.",
        ],
    },
    "education": {
        "label": "Education & Knowledge",
        "what_it_means": "learning, skill acquisition, academic pursuits, and intellectual growth",
        "positive": "This is an excellent time for learning and acquiring new skills. Focus is sharp.",
        "mixed": "Progress in learning requires structured discipline. Distractions may arise.",
        "care": "Focus may scatter easily. Break down complex subjects and protect your study time.",
        "focus": ["Prioritize structured learning.", "Avoid overwhelming yourself with too many topics."],
    },
    "children": {
        "label": "Children & Creativity",
        "what_it_means": "parenting, progeny, creative projects, and personal expression",
        "positive": "Creative flow is strong, and matters involving children are supportive.",
        "mixed": "Patience is needed in creative endeavors or parenting matters.",
        "care": "Expect delays or stress in these areas. Focus on understanding rather than controlling.",
        "focus": ["Foster patience in creative blocks.", "Listen more when dealing with children."],
    },
    "property": {
        "label": "Property & Vehicles",
        "what_it_means": "real estate, home environment, vehicles, and foundational comforts",
        "positive": "Favorable energy for investments, home improvements, or securing assets.",
        "mixed": "Delays or moderate friction possible in property or vehicle matters. Double check details.",
        "care": "Avoid hasty property investments or major changes to your home environment.",
        "focus": ["Delay major property decisions if unsure.", "Focus on maintaining what you have."],
    },
    "spirituality": {
        "label": "Spirituality & Luck",
        "what_it_means": "inner growth, religious pursuits, mentors, and natural fortune",
        "positive": "Strong alignment with spiritual growth and serendipitous opportunities.",
        "mixed": "Inner peace requires deliberate effort and stepping back from daily noise.",
        "care": "You may feel disconnected or unlucky. Focus on grounding practices and giving back.",
        "focus": ["Dedicate time to inner reflection.", "Don't force luck; let things unfold."],
    },
    "legal": {
        "label": "Legal & Competitors",
        "what_it_means": "disputes, opposition, court matters, and handling adversaries",
        "positive": "You have the upper hand in resolving disputes or facing competition.",
        "mixed": "Competitors or legal matters require careful negotiation and patience.",
        "care": "Avoid starting new disputes. Protect yourself and seek counsel.",
        "focus": ["Resolve conflicts amicably if possible.", "Avoid unnecessary provocations."],
    },
    "travel": {
        "label": "Travel & Foreign",
        "what_it_means": "journeys, relocation, foreign connections, and isolation",
        "positive": "Travel and foreign connections are highly fruitful and expansive.",
        "mixed": "Journeys may have minor hiccups. Plan carefully and stay flexible.",
        "care": "Travel may bring stress or exhaustion. Avoid unnecessary long journeys.",
        "focus": ["Double check all travel arrangements.", "Keep a flexible itinerary."],
    }
}

SUPPORTIVE_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
CHALLENGING_PLANETS = {"Saturn", "Mars", "Rahu", "Ketu"}


def _traits_excerpt(text: str, limit: int = 3) -> str:
    parts = [piece.strip() for piece in text.replace(".", "").split(",") if piece.strip()]
    return ", ".join(parts[:limit])


def _with_indefinite_article(phrase: str) -> str:
    cleaned = phrase.strip()
    if not cleaned:
        return cleaned
    article = "an" if cleaned[0].lower() in {"a", "e", "i", "o", "u"} else "a"
    return f"{article} {cleaned}"


def _friendly_date(dt: datetime | None) -> str:
    if not dt:
        return "Unknown"
    return dt.strftime("%d %b %Y")


def _score_band(score: float) -> str:
    if score >= 1.5:
        return "Excellent"
    if score >= 0.5:
        return "Supportive"
    if score > -0.5:
        return "Mixed"
    return "Needs care"


def _confidence_band(score: float, factor_count: int = 0) -> str:
    magnitude = abs(score)
    if magnitude >= 1.5 or factor_count >= 5:
        return "High"
    if magnitude >= 0.7 or factor_count >= 3:
        return "Medium"
    return "Light"


def _strength_band(strength: float) -> str:
    if strength >= 1.3:
        return "Strong"
    if strength >= 1.0:
        return "Steady"
    if strength >= 0.8:
        return "Sensitive"
    return "Weak"


def _planet_theme(planet: str) -> str:
    return PLANET_PLAIN_MEANINGS.get(planet, "important life themes")


def _planet_cycle_line(planet: str) -> str:
    theme = _planet_theme(planet)
    return f"{planet} periods usually make {theme} louder."


def _readable_house_name(house: int) -> str:
    house_info = HOUSE_DATA.get(house)
    if not house_info:
        return f"House {house}"
    return house_info.name_en.split("(")[0].strip()


def _dominant_planet_lines(shadbala: dict[str, float]) -> tuple[list[dict], list[dict]]:
    ordered = sorted(shadbala.items(), key=lambda item: item[1], reverse=True)
    dominant = [
        {
            "planet": planet,
            "strength": round(strength, 2),
            "band": _strength_band(strength),
        }
        for planet, strength in ordered[:3]
    ]
    sensitive = [
        {
            "planet": planet,
            "strength": round(strength, 2),
            "band": _strength_band(strength),
        }
        for planet, strength in sorted(shadbala.items(), key=lambda item: item[1])[:3]
    ]
    return dominant, sensitive


def _planet_flags(planet: str, special_summary: dict) -> list[str]:
    flags: list[str] = []
    if planet in special_summary.get("combust_planets", []):
        flags.append("combust")
    if planet in special_summary.get("retrograde_planets", []):
        flags.append("retrograde")
    for war in special_summary.get("graha_yuddha", []):
        if planet == war.get("winner"):
            flags.append("won planetary war")
        if planet == war.get("loser"):
            flags.append("lost planetary war")
    return flags


def _planet_blurb(
    planet: str,
    sign: str,
    house: int,
    strength: float,
    avastha_state: str,
    flags: list[str],
) -> str:
    sign_profile = ZODIAC_PROFILES.get(sign)
    tone = _traits_excerpt(sign_profile.nature_en, 3).lower() if sign_profile else sign.lower()
    house_info = HOUSE_DATA.get(house)
    house_topics = house_info.domain_en.rstrip(".").lower() if house_info else f"house {house} topics"
    strength_band = _strength_band(strength).lower()

    lines = [
        f"{planet} here connects { _planet_theme(planet) } with {house_topics}.",
        f"{sign} adds a {tone} tone, so this planet tends to express itself in a {tone} way.",
        f"This placement reads as {strength_band} overall, which suggests the planet can deliver results {'clearly and consistently' if strength >= 1.0 else 'but may need more maturity, timing, or support'}.",
    ]
    if avastha_state:
        lines.append(
            f"It is in {avastha_state} avastha, which gives extra context about how directly the planet tends to act."
        )
    if flags:
        lines.append(f"Extra conditions noted: {', '.join(flags)}.")
    return " ".join(lines)


def _house_blurb(house: int, occupants: list[str], aspected_by: list[str]) -> str:
    house_info = HOUSE_DATA.get(house)
    if not house_info:
        return f"House {house} is active in this chart."

    sentences = [f"This house covers {house_info.domain_en.lower()}."]
    if occupants:
        sentences.append(
            f"Because {', '.join(occupants)} {'is' if len(occupants) == 1 else 'are'} placed here, these topics stay visible and regularly ask for attention."
        )
    else:
        sentences.append("No major planet sits here, so this area may behave more through its ruler and transits than through constant daily pressure.")

    if aspected_by:
        supportive = [planet for planet in aspected_by if planet in SUPPORTIVE_PLANETS]
        challenging = [planet for planet in aspected_by if planet in CHALLENGING_PLANETS]
        if supportive:
            sentences.append(
                f"Supportive influence comes from {', '.join(supportive)}, which usually helps these topics move with more guidance or softness."
            )
        if challenging:
            sentences.append(
                f"Pressure comes from {', '.join(challenging)}, so this house may need patience, structure, or better boundaries."
            )
    return " ".join(sentences)


def _build_reader_guide() -> dict:
    return {
        "overview": (
            "Read this report like a weather forecast, not a fixed verdict. "
            "The natal chart shows your default wiring, while timing sections "
            "show when certain themes become louder or easier to work with."
        ),
        "how_to_use": [
            "Start with the Executive Summary for the big picture.",
            "Use the Life Domain section to see which areas of life are naturally stronger and which need steadier handling.",
            "Use the Timing section when planning important moves, conversations, launches, or recovery periods.",
            "Use Remedies and the Action Plan as practical support, not superstition-driven fear.",
        ],
        "terms": TERM_GUIDE,
    }


def _build_chart_basics(
    lagna: str,
    moon_sign: str,
    lagna_profile,
    moon_profile,
    lagna_strength: float,
    benefic_strength: float,
) -> dict:
    lagna_traits = _traits_excerpt(lagna_profile.nature_en, 4) if lagna_profile else lagna
    moon_traits = _traits_excerpt(moon_profile.nature_en, 4) if moon_profile else moon_sign
    work_style = lagna_profile.career_en if lagna_profile else "A practical work style shaped by the chart."
    health_line = lagna_profile.health_en if lagna_profile else "Health follows routine, stress management, and body awareness."
    relationship_line = moon_profile.relationship_en if moon_profile else "Relationships improve with emotional honesty and steadiness."

    if lagna_strength >= 0.6:
        body_line = "Your chart has a fairly anchored core, so self-direction improves when you trust your natural approach instead of copying others."
    elif lagna_strength >= 0.0:
        body_line = "Your chart can hold direction, but momentum improves when you reduce overthinking and keep life structured."
    else:
        body_line = "Your chart benefits from stronger foundations, clear routines, and fewer reactive decisions."

    benefic_line = (
        "Supportive planets are strong enough to help through mentors, relationships, and good judgement."
        if benefic_strength >= 1.1
        else "Supportive results are available, but they build best through discipline rather than luck alone."
    )

    plain_english = (
        f"{lagna} rising gives you {_with_indefinite_article(lagna_traits.lower())} outer style. "
        f"{moon_sign} Moon shapes the emotional side as {moon_traits.lower()}. "
        f"Together this often produces someone who does best with thoughtful pacing, clear systems, and environments that feel emotionally manageable. "
        f"{benefic_line}"
    )

    return {
        "plain_english": plain_english,
        "identity": body_line,
        "work_style": work_style,
        "relationships": relationship_line,
        "wellbeing": health_line,
    }


def _current_cycle_text(current_maha, current_antar) -> str:
    if not current_maha:
        return "The current dasha cycle could not be identified from the available data."

    maha_line = _planet_cycle_line(current_maha.planet)
    if not current_antar:
        return f"You are in {current_maha.planet} Mahadasha. In simple terms, this is the main life chapter right now. {maha_line}"

    antar_line = _planet_cycle_line(current_antar.planet)
    return (
        f"You are in {current_maha.planet} Mahadasha with {current_antar.planet} Antardasha. "
        f"Think of {current_maha.planet} as the long chapter and {current_antar.planet} as the current sub-theme. "
        f"{maha_line} {antar_line}"
    )


def _timing_band_from_context(
    transit_scores: dict[str, dict[str, float]],
    current_maha,
    current_antar,
    sade_sati,
) -> tuple[str, float]:
    values = [item["score"] for item in transit_scores.values()]
    avg_transit = sum(values) / len(values) if values else 0.0
    timing_score = avg_transit

    if current_maha and current_maha.planet in SUPPORTIVE_PLANETS:
        timing_score += 0.25
    if current_maha and current_maha.planet in CHALLENGING_PLANETS:
        timing_score -= 0.2
    if current_antar and current_antar.planet in SUPPORTIVE_PLANETS:
        timing_score += 0.15
    if current_antar and current_antar.planet in CHALLENGING_PLANETS:
        timing_score -= 0.15
    if getattr(sade_sati, "currently_active", False):
        timing_score -= 0.45
    elif getattr(sade_sati, "dhaiya_active", False):
        timing_score -= 0.2

    return _score_band(timing_score), round(timing_score, 2)


def _best_focus_from_transits(supportive_transits: list[dict]) -> list[str]:
    if not supportive_transits:
        return [
            "Use this phase for steady maintenance rather than dramatic expansion.",
            "Let planning and consistency do more work than urgency.",
        ]

    focus: list[str] = []
    for item in supportive_transits[:3]:
        planet = item["planet"]
        if planet == "Jupiter":
            focus.append("Good for learning, mentoring, long-term planning, and high-trust decisions.")
        elif planet == "Venus":
            focus.append("Helpful for relationships, design, comfort upgrades, and diplomacy.")
        elif planet == "Mercury":
            focus.append("Helpful for writing, negotiations, paperwork, study, and commercial moves.")
        elif planet == "Moon":
            focus.append("Good for emotional resets, home matters, and reconnecting with supportive people.")
        elif planet == "Sun":
            focus.append("Useful for visibility, leadership, confidence, and speaking up clearly.")
        elif planet == "Saturn":
            focus.append("Use this period for disciplined effort, systems, and long-term clean-up.")
        elif planet == "Mars":
            focus.append("Good for action that needs courage, speed, or a decisive push.")
    return focus[:3]


def _caution_focus_from_timing(challenging_transits: list[dict], sade_sati) -> list[str]:
    cautions: list[str] = []
    if getattr(sade_sati, "currently_active", False):
        cautions.append("Saturn pressure is active, so slower progress is not failure. Leave buffer time and avoid panic decisions.")
    elif getattr(sade_sati, "dhaiya_active", False):
        cautions.append("Saturn is asking for cleaner habits and tighter emotional boundaries than usual.")

    for item in challenging_transits[:3]:
        planet = item["planet"]
        if planet == "Mars":
            cautions.append("Watch impatience, arguments, injuries from rushing, and forceful decisions.")
        elif planet == "Saturn":
            cautions.append("Expect delays or heavier workloads. Build slack instead of overcommitting.")
        elif planet == "Rahu":
            cautions.append("Avoid impulsive bets, glamour-driven decisions, or confusing promises.")
        elif planet == "Ketu":
            cautions.append("Avoid disengaging too quickly from responsibilities that still need closure.")
        elif planet == "Moon":
            cautions.append("Emotions may swing faster than usual, so rest before making personal decisions.")
    return cautions[:3]


def _build_timing_overview(
    current_maha,
    current_antar,
    dasha_list: list[dict],
    transit_scores: dict[str, dict[str, float]],
    sade_sati,
) -> dict:
    supportive_transits = sorted(
        [dict(planet=planet, **data) for planet, data in transit_scores.items() if data["score"] > 0.0],
        key=lambda item: item["score"],
        reverse=True,
    )[:4]
    challenging_transits = sorted(
        [dict(planet=planet, **data) for planet, data in transit_scores.items() if data["score"] < 0.0],
        key=lambda item: item["score"],
    )[:4]

    timing_band, timing_score = _timing_band_from_context(transit_scores, current_maha, current_antar, sade_sati)
    if timing_band == "Excellent":
        plain_english = "The current timing looks unusually supportive. Strong moves still benefit from planning, but the weather is more cooperative than average."
    elif timing_band == "Supportive":
        plain_english = "The current period supports progress, especially when you work with discipline and do not overcomplicate simple opportunities."
    elif timing_band == "Mixed":
        plain_english = "This is a workable but uneven phase. Good outcomes are possible, though pacing, preparation, and emotional steadiness matter more."
    else:
        plain_english = "This looks like a slower, heavier phase. Focus on repair, foundations, and cleaner decisions rather than forcing results."

    return {
        "current_cycle": _current_cycle_text(current_maha, current_antar),
        "timing_band": timing_band,
        "timing_score": timing_score,
        "plain_english": plain_english,
        "next_dashas": dasha_list[:5],
        "supportive_transits": supportive_transits,
        "challenging_transits": challenging_transits,
        "best_for_now": _best_focus_from_transits(supportive_transits),
        "caution_for_now": _caution_focus_from_timing(challenging_transits, sade_sati),
    }


def _domain_key(domain_str: str) -> str:
    lowered = domain_str.lower()
    if "career" in lowered or "profession" in lowered:
        return "career"
    if "wealth" in lowered or "finance" in lowered:
        return "finance"
    if "marriage" in lowered or "relationship" in lowered:
        return "marriage"
    if "health" in lowered or "well-being" in lowered:
        return "health"
    if "education" in lowered or "knowledge" in lowered:
        return "education"
    if "children" in lowered or "creativity" in lowered:
        return "children"
    if "property" in lowered or "vehicles" in lowered:
        return "property"
    if "spirituality" in lowered or "luck" in lowered:
        return "spirituality"
    if "legal" in lowered or "competitors" in lowered:
        return "legal"
    if "travel" in lowered or "foreign" in lowered:
        return "travel"
    return "career"


def _build_domain_story(syn: DomainScore, timeline: list[dict] = None) -> dict:
    domain_key = _domain_key(syn.category)
    guide = DOMAIN_GUIDANCE.get(domain_key) or DOMAIN_GUIDANCE.get("career")
    
    score_band = syn.band.title()
    if score_band in {"Exceptional", "Strong"}:
        plain = f"{guide['label']} here means {guide['what_it_means']}. {guide['positive']}"
    elif score_band == "Moderate":
        plain = f"{guide['label']} here means {guide['what_it_means']}. {guide['mixed']}"
    else:
        plain = f"{guide['label']} here means {guide['what_it_means']}. {guide['care']}"

    factors_en = []
    factors_hi = []
    for f in syn.factors:
        factors_en.append(f.text_en)
        factors_hi.append(f.text_hi)

    return {
        "domain_en": syn.category,
        "domain_hi": getattr(syn, "domain_hi", syn.category),
        "score": round(syn.score, 2),
        "score_band": score_band,
        "confidence": "High" if syn.confidence >= 0.7 else "Medium" if syn.confidence >= 0.4 else "Low",
        "summary_en": syn.summary_en,
        "summary_hi": syn.summary_hi,
        "key_factors_en": factors_en,
        "key_factors_hi": factors_hi,
        "plain_english": plain,
        "focus_now": guide.get("focus", []),
        "timeline": timeline or []
    }


def _build_remedy_focus(report: dict) -> dict:
    dosha_details = report["doshas"].get("dosha_details", [])
    active_doshas = [item for item in dosha_details if item.get("present")]
    gemstones = report["remedies"].get("gemstones", {})
    rudraksha = report["remedies"].get("rudraksha", [])
    vastu = report["remedies"].get("vastu", {})
    lal_kitab = report["remedies"].get("lal_kitab", [])

    priority_actions: list[str] = []
    supportive_items: list[str] = []
    avoidances: list[str] = []

    for item in active_doshas[:2]:
        remedies = item.get("remedies") or []
        if remedies:
            priority_actions.append(f"{item['name']}: {remedies[0]}")

    for planet, gem in gemstones.items():
        status = gem.get("status", "")
        if status != "Optional (Already Strong)":
            supportive_items.append(f"{planet}: {gem.get('gem_en')} - {status}.")

    for item in rudraksha[:2]:
        planet_name = item['planet']
        benefit_text = item['benefit_en'].replace(f'To balance weak {planet_name}: ', '')
        supportive_items.append(f"{planet_name}: {item['rudraksha_en']} for {benefit_text}.")

    if vastu:
        supportive_items.append(
            f"Environment: emphasize the {vastu.get('direction_en')} direction because {vastu.get('benefit_en')}"
        )

    for item in lal_kitab[:3]:
        for avoid in item.get("avoid_en", [])[:2]:
            if avoid not in avoidances:
                avoidances.append(avoid)

    if not priority_actions:
        priority_actions.append("Keep remedies simple and repeatable. Consistency matters more than collecting many rituals.")
    if not supportive_items:
        supportive_items.append("Use grounding routines, clean schedules, and better rest as the first remedy layer.")
    if not avoidances:
        avoidances.append("Avoid fear-based astrology decisions and dramatic all-or-nothing moves.")

    return {
        "priority_actions": priority_actions[:4],
        "supportive_items": supportive_items[:5],
        "avoidances": avoidances[:4],
    }


def _build_action_plan(
    timing_overview: dict,
    chart_signature: dict,
    synthesis_items: list[dict],
    remedy_focus: dict,
) -> dict:
    strong_domains = [item["domain_en"] for item in synthesis_items if item["score_band"] in {"Excellent", "Supportive"}][:2]
    weaker_domains = [item["domain_en"] for item in synthesis_items if item["score_band"] == "Needs care"][:2]
    dominant = [item["planet"] for item in chart_signature.get("dominant_planets", [])[:2]]
    sensitive = [item["planet"] for item in chart_signature.get("sensitive_planets", [])[:2]]

    lean_into = []
    if strong_domains:
        lean_into.append(f"Use the current strengths in {', '.join(strong_domains)} with deliberate, not rushed, decisions.")
    if dominant:
        lean_into.append(f"Lead with the better-developed parts of the chart: {', '.join(dominant)} themes tend to respond well when used responsibly.")
    lean_into.extend(timing_overview.get("best_for_now", [])[:2])

    watch_for = []
    if weaker_domains:
        watch_for.append(f"Go slower in {', '.join(weaker_domains)} until the foundations feel clearer.")
    if sensitive:
        watch_for.append(f"Sensitive planets right now are {', '.join(sensitive)}, so those themes need better pacing and boundaries.")
    watch_for.extend(timing_overview.get("caution_for_now", [])[:2])

    next_steps = []
    next_steps.extend(remedy_focus.get("priority_actions", [])[:2])
    next_steps.append("Review the Timing section before locking in major commitments or launches.")
    next_steps.append("Treat this report as a decision aid: combine it with practical facts, health advice, and financial common sense.")

    return {
        "lean_into": lean_into[:4],
        "watch_for": watch_for[:4],
        "next_steps": next_steps[:4],
    }


def _build_executive_summary(
    lagna: str,
    moon_sign: str,
    chart_basics: dict,
    chart_signature: dict,
    timing_overview: dict,
    synthesis_items: list[dict],
    doshas: dict,
) -> dict:
    lagna_traits = _traits_excerpt(ZODIAC_PROFILES.get(lagna).nature_en, 3).lower() if ZODIAC_PROFILES.get(lagna) else lagna.lower()
    moon_traits = _traits_excerpt(ZODIAC_PROFILES.get(moon_sign).nature_en, 3).lower() if ZODIAC_PROFILES.get(moon_sign) else moon_sign.lower()
    headline = f"{lagna} Lagna with {moon_sign} Moon: {lagna_traits} on the outside, {moon_traits} underneath."

    strengths = []
    cautions = []
    timing_highlights = []

    for item in chart_signature.get("dominant_planets", [])[:2]:
        strengths.append(f"{item['planet']} is one of the steadier planets in the chart.")

    for item in synthesis_items:
        if item["score_band"] in {"Excellent", "Supportive"} and len(strengths) < 4:
            strengths.append(f"{item['domain_en']}: {item['summary_en']}")
        if item["score_band"] == "Needs care" and len(cautions) < 3:
            cautions.append(f"{item['domain_en']}: {item['summary_en']}")

    for item in chart_signature.get("sensitive_planets", [])[:2]:
        if len(cautions) >= 4:
            break
        cautions.append(f"{item['planet']} needs steadier handling and better timing than the chart's strongest planets.")

    active_doshas = [item["name"] for item in doshas.get("dosha_details", []) if item.get("present")]
    if active_doshas:
        cautions.append(f"Active pressure patterns include {', '.join(active_doshas[:2])}, so maturity matters more than fear.")

    timing_highlights.append(timing_overview["current_cycle"])
    timing_highlights.append(f"Current timing band: {timing_overview['timing_band']}.")
    timing_highlights.extend(timing_overview.get("best_for_now", [])[:2])

    overview = (
        f"{chart_basics['plain_english']} "
        f"At the moment, the timing feels {timing_overview['timing_band'].lower()}, which means the best results usually come from thoughtful pacing rather than impulsive moves."
    )

    return {
        "headline": headline,
        "overview": overview,
        "strengths": strengths[:4],
        "cautions": cautions[:4],
        "timing_highlights": timing_highlights[:4],
    }


def generate_full_report_data(person: Person, current_dt: datetime | None = None) -> dict:
    """Generate a reader-friendly report payload for JSON and PDF output."""
    if current_dt is None:
        current_dt = datetime.now(timezone.utc)

    natal_longitudes = get_raw_longitudes(person.birth_datetime)
    lagna = natal_lagna(person)
    moon_sign = natal_moon_sign(person)
    nakshatra = moon_constellation(person.birth_datetime, person.birth_location)
    natal_planet_signs = planet_signs(person.birth_datetime, person.birth_location)
    natal_planet_houses = planet_houses(person.birth_datetime, person.birth_location)

    shadbala = shadbala_summary(natal_planet_signs, natal_planet_houses)
    drishti = compute_aspects(natal_planet_houses)
    avasthas = compute_all_avasthas(natal_longitudes)
    yogas = detect_all_yogas(natal_planet_houses, natal_planet_signs, lagna)
    extra_yogas = detect_all_extra_yogas(natal_planet_houses, natal_planet_signs, lagna)
    all_yogas = yogas + extra_yogas
    special = compute_special_conditions(person.birth_datetime, natal_planet_houses, natal_planet_signs, lagna)
    nadi_links = compute_nadi_linkages(natal_planet_houses)
    chara_karakas = compute_chara_karakas(natal_longitudes)

    # Compute KP & Bhrigu base values
    from app.astrology.kp import kp_score, true_kp_cuspal_score
    from app.astrology.bhrigu import calculate_bhrigu_bindu, bhrigu_transit_score
    moon_long = natal_longitudes.get("Moon", 0.0)
    rahu_long = natal_longitudes.get("Rahu", 0.0)
    bb_long = calculate_bhrigu_bindu(moon_long, rahu_long)
    bhrigu_bonus = bhrigu_transit_score(bb_long, natal_longitudes)
    kp_score_val = kp_score(natal_longitudes, lagna, "career")
    kp_cuspal_val = true_kp_cuspal_score(
        "career", person.birth_datetime, person.birth_location.latitude,
        person.birth_location.longitude, natal_longitudes, natal_planet_houses
    )

    synthesis_ctx = ScoringContext(
        natal_houses=natal_planet_houses,
        natal_signs=natal_planet_signs,
        lagna=lagna,
        shadbala=shadbala,
        drishti_house=drishti[0],
        drishti_planet=drishti[1],
        avasthas=avasthas,
        nadi_links=nadi_links,
        chara_karakas=chara_karakas,
        kp_natal_cuspal=kp_cuspal_val,
        kp_natal_score=kp_score_val,
        bhrigu_bonus=bhrigu_bonus,
        active_maha=None,
        active_antar=None,
    )
    synthesis_engine = SynthesisEngine(ctx=synthesis_ctx)
    synthesis_outcomes = synthesis_engine.run_all()

    remedies_lal_kitab = get_lal_kitab_remedies(natal_planet_houses)
    remedies_gems = prescribe_gemstones(natal_planet_houses, natal_planet_signs, lagna, shadbala)
    remedies_rudraksha = prescribe_rudraksha(shadbala)
    remedies_vastu = prescribe_astro_vastu(shadbala)

    mahas = compute_mahadashas(person.birth_datetime, nakshatra, natal_longitudes.get("Moon", 0.0))
    current_maha = None
    current_antar = None
    dasha_list: list[dict] = []
    # Synchronize timezone awareness with dasha system outputs
    if mahas and mahas[0].end.tzinfo is not None and current_dt.tzinfo is None:
        eval_dt = current_dt.replace(tzinfo=mahas[0].end.tzinfo)
    elif mahas and mahas[0].end.tzinfo is None and current_dt.tzinfo is not None:
        eval_dt = current_dt.replace(tzinfo=None)
    else:
        eval_dt = current_dt

    for maha in mahas:
        if maha.end > eval_dt:
            dasha_list.append(
                {
                    "planet": maha.planet,
                    "start": maha.start.strftime("%Y-%m-%d"),
                    "end": maha.end.strftime("%Y-%m-%d"),
                }
            )
        if maha.start <= eval_dt <= maha.end:
            current_maha = maha
            for antar in compute_antardashas(maha):
                if antar.start <= eval_dt <= antar.end:
                    current_antar = antar
                    break

    sade_sati = compute_sade_sati(moon_sign, current_dt)

    transit_context = build_context(current_dt, person.birth_location, person)
    transit_signs = transit_context.planet_signs
    gochara_results = gochara_score(transit_signs, moon_sign)
    transit_scores: dict[str, dict[str, float]] = {}
    for planet, sign in transit_signs.items():
        if planet in {"Lagna", "Uranus", "Neptune", "Pluto"}:
            continue
        transit_scores[planet] = {
            "house_from_moon": _house_from_sign(moon_sign, sign),
            "score": gochara_results.get(planet, 0.0),
        }

    lagna_profile = ZODIAC_PROFILES.get(lagna)
    moon_profile = ZODIAC_PROFILES.get(moon_sign)
    lagna_strength = lagna_lord_strength(lagna, shadbala, natal_planet_houses)
    benefic_strength = benefic_strength_score(shadbala, {"Jupiter", "Venus", "Mercury", "Moon"})
    chart_basics = _build_chart_basics(
        lagna,
        moon_sign,
        lagna_profile,
        moon_profile,
        lagna_strength,
        benefic_strength,
    )

    dominant_planets, sensitive_planets = _dominant_planet_lines(shadbala)
    chart_signature = {
        "dominant_planets": dominant_planets,
        "sensitive_planets": sensitive_planets,
        "summary": (
            f"The chart is carried most clearly by {', '.join(item['planet'] for item in dominant_planets[:2])}, "
            f"while {', '.join(item['planet'] for item in sensitive_planets[:2])} need more careful timing."
        ),
    }

    timing_overview = _build_timing_overview(current_maha, current_antar, dasha_list, transit_scores, sade_sati)

    # Phase 5.5: Dasha × Domain Activation Matrix
    from app.services.dasha_domain_matrix import build_dasha_domain_matrix
    # Find current pratyantar for the matrix
    current_pratyantar = None
    if current_antar:
        from app.astrology.dasha import compute_pratyantardashas
        try:
            for prat in compute_pratyantardashas(current_antar):
                if prat.start <= current_dt <= prat.end:
                    current_pratyantar = prat
                    break
        except Exception:
            pass

    dasha_matrix = build_dasha_domain_matrix(
        maha_lord=current_maha.planet if current_maha else None,
        antar_lord=current_antar.planet if current_antar else None,
        pratyantar_lord=current_pratyantar.planet if current_pratyantar else None,
        shadbala=shadbala,
        natal_houses=natal_planet_houses,
    )
    from app.services.timeline_builder import build_domain_timeline
    from app.services.life_predictor import LifePredictorService
    _predictor = LifePredictorService()
    
    synthesis_items = []
    for syn in synthesis_outcomes:
        # Build 12 month timeline for each domain
        # Using a very low-res step to keep it fast
        domain_tl = build_domain_timeline(
            person=person,
            category=_domain_key(syn.category),
            start_dt=current_dt,
            months=12,
            predictor=_predictor
        )
        synthesis_items.append(_build_domain_story(syn, domain_tl))

    report = {
        "personal_info": {
            "name": person.name,
            "dob": person.birth_datetime.strftime("%d %b %Y, %I:%M %p"),
            "place": f"{person.birth_location.latitude:.4f}, {person.birth_location.longitude:.4f}",
            "coordinates": {
                "latitude": person.birth_location.latitude,
                "longitude": person.birth_location.longitude,
            },
            "timezone": person.birth_location.timezone,
            "lagna": lagna,
            "moon_sign": moon_sign,
            "nakshatra": nakshatra,
        },
        "reader_guide": _build_reader_guide(),
        "chart_basics": chart_basics,
        "chart_signature": chart_signature,
        "planetary_positions": [],
        "houses_info": [],
        "personality": {
            "lagna_based": {
                "nature_en": lagna_profile.nature_en if lagna_profile else "",
                "nature_hi": lagna_profile.nature_hi if lagna_profile else "",
                "career_en": lagna_profile.career_en if lagna_profile else "",
                "career_hi": lagna_profile.career_hi if lagna_profile else "",
                "health_en": lagna_profile.health_en if lagna_profile else "",
                "health_hi": lagna_profile.health_hi if lagna_profile else "",
                "relationship_en": lagna_profile.relationship_en if lagna_profile else "",
                "relationship_hi": lagna_profile.relationship_hi if lagna_profile else "",
            }
        },
        "synthesis": synthesis_items,
        "shadbala": shadbala,
        "yogas": [],
        "doshas": special.summary(),
        "remedies": {
            "lal_kitab": [],
            "gemstones": remedies_gems,
            "rudraksha": remedies_rudraksha,
            "vastu": remedies_vastu,
        },
        "current_dasha": {
            "maha": current_maha.planet if current_maha else "Unknown",
            "antar": current_antar.planet if current_antar else "Unknown",
            "summary": timing_overview["current_cycle"],
        },
        "dasha_list": dasha_list[:5],
        "sade_sati": {
            "natal_moon_sign": sade_sati.natal_moon_sign,
            "currently_active": sade_sati.currently_active,
            "current_phase": {
                "phase": sade_sati.current_phase.phase,
                "saturn_sign": sade_sati.current_phase.saturn_sign,
                "start": sade_sati.current_phase.start.isoformat(),
                "end": sade_sati.current_phase.end.isoformat(),
                "intensity": sade_sati.current_phase.intensity,
            }
            if sade_sati.current_phase
            else None,
            "dhaiya_active": sade_sati.dhaiya_active,
            "dhaiya_sign": sade_sati.dhaiya_sign,
            "penalty": sade_sati.penalty,
            "summary": sade_sati.summary(),
            "phases": [
                {
                    "phase": phase.phase,
                    "saturn_sign": phase.saturn_sign,
                    "start": phase.start.isoformat(),
                    "end": phase.end.isoformat(),
                    "intensity": phase.intensity,
                }
                for phase in sade_sati.phases
            ],
        },
        "timing_overview": timing_overview,
        "transits": transit_scores,
        "dasha_domain_matrix": dasha_matrix,
    }

    special_summary = report["doshas"]

    for planet, sign in natal_planet_signs.items():
        house_num = natal_planet_houses.get(planet, 1)
        planet_info = PLANET_DATA.get(planet)
        strength = shadbala.get(planet, 1.0)
        avastha = avasthas.get(planet)
        flags = _planet_flags(planet, special_summary)

        report["planetary_positions"].append(
            {
                "planet": planet,
                "sign": sign,
                "house": house_num,
                "strength": round(strength, 2),
                "strength_band": _strength_band(strength),
                "avastha_en": avastha.state_en if avastha else "",
                "avastha_hi": avastha.state_hi if avastha else "",
                "nature_en": planet_info.nature_en if planet_info else "",
                "nature_hi": planet_info.nature_hi if planet_info else "",
                "significations_en": planet_info.significations_en if planet_info else "",
                "significations_hi": planet_info.significations_hi if planet_info else "",
                "flags": flags,
                "interpretation_en": _planet_blurb(
                    planet,
                    sign,
                    house_num,
                    strength,
                    avastha.state_en if avastha else "",
                    flags,
                ),
            }
        )

    house_aspects = drishti[0]
    for house in range(1, 13):
        house_info = HOUSE_DATA.get(house)
        occupants = [planet for planet, planet_house in natal_planet_houses.items() if planet_house == house]
        aspected_by = sorted(list(house_aspects.get(house, set())))

        report["houses_info"].append(
            {
                "house": house,
                "name_en": house_info.name_en if house_info else f"House {house}",
                "name_hi": house_info.name_hi if house_info else f"भाव {house}",
                "domain_en": house_info.domain_en if house_info else "",
                "domain_hi": house_info.domain_hi if house_info else "",
                "body_parts_en": house_info.body_parts_en if house_info else "",
                "body_parts_hi": house_info.body_parts_hi if house_info else "",
                "occupants": occupants,
                "aspected_by": aspected_by,
                "interpretation_en": _house_blurb(house, occupants, aspected_by),
            }
        )

    for yoga in all_yogas:
        if yoga.present:
            report["yogas"].append(
                {
                    "name": yoga.name,
                    "description": yoga.description,
                    "score": yoga.strength,
                }
            )

    for item in remedies_lal_kitab:
        report["remedies"]["lal_kitab"].append(
            {
                "planet": item.planet,
                "house": item.house,
                "effect_en": item.effect_en,
                "effect_hi": item.effect_hi,
                "remedies_en": item.remedies_en,
                "remedies_hi": item.remedies_hi,
                "donate_en": item.donate_en,
                "donate_hi": item.donate_hi,
                "avoid_en": item.avoid_en,
                "avoid_hi": item.avoid_hi,
            }
        )

    report["remedy_focus"] = _build_remedy_focus(report)
    report["action_plan"] = _build_action_plan(
        timing_overview,
        chart_signature,
        synthesis_items,
        report["remedy_focus"],
    )
    report["executive_summary"] = _build_executive_summary(
        lagna,
        moon_sign,
        chart_basics,
        chart_signature,
        timing_overview,
        synthesis_items,
        report["doshas"],
    )

    return report
