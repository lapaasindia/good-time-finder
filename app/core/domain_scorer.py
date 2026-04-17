"""
Shared domain scoring module for static chart signatures.
Calculates a category's overall potential across Parashari, Jaimini, Nadi, KP, and Bhrigu.
Used by both the Report generator and the Heatmap anchor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


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
    score: float                    # mapped roughly to [-3, 3]
    band: Literal["exceptional", "strong", "moderate", "strained", "challenging"]
    confidence: float               # [0, 1] based on signal agreement
    factors: list[Factor]
    summary_en: str
    summary_hi: str


@dataclass
class ScoringContext:
    natal_houses: dict[str, int]
    natal_signs: dict[str, str]
    lagna: str
    shadbala: dict[str, float]
    drishti_house: dict[int, set[str]]
    drishti_planet: dict[str, set[str]]
    avasthas: dict[str, Any]
    nadi_links: dict[str, dict[str, list[str]]]
    chara_karakas: dict[str, str]
    kp_natal_cuspal: float
    kp_natal_score: float
    bhrigu_bonus: float
    active_maha: str | None
    active_antar: str | None


def _get_band(score: float) -> tuple[str, str, str]:
    if score >= 2.2:
        return "exceptional", "Exceptional prospects.", "उत्कृष्ट संभावनाएं।"
    elif score >= 1.0:
        return "strong", "Strong potential with good growth.", "मजबूत क्षमता और अच्छी वृद्धि।"
    elif score >= -0.5:
        return "moderate", "Moderate trajectory. Requires effort.", "मध्यम ग्राफ। प्रयास की आवश्यकता है।"
    elif score >= -1.5:
        return "strained", "Strained. Delays or friction likely.", "तनावपूर्ण। देरी या घर्षण की संभावना।"
    else:
        return "challenging", "Challenging dynamics. Protect this area.", "चुनौतीपूर्ण गतिशीलता। इस क्षेत्र की रक्षा करें।"


def score_domain(category: str, ctx: ScoringContext) -> DomainScore:
    """Run independent votes for the domain and aggregate into a score."""
    factors: list[Factor] = []
    total_score = 0.0

    # 1. Parashari Vote
    p_score, p_factors = _parashari_vote(category, ctx)
    total_score += p_score
    factors.extend(p_factors)

    # 2. Jaimini Vote
    j_score, j_factors = _jaimini_vote(category, ctx)
    total_score += j_score
    factors.extend(j_factors)

    # 3. Nadi Vote
    n_score, n_factors = _nadi_vote(category, ctx)
    total_score += n_score
    factors.extend(n_factors)

    # 4. KP Vote
    kp_score, kp_factors = _kp_vote(category, ctx)
    total_score += kp_score
    factors.extend(kp_factors)

    # 5. Bhrigu Vote
    b_score, b_factors = _bhrigu_vote(category, ctx)
    total_score += b_score
    factors.extend(b_factors)

    # Confidence calculation: agreement ratio
    if not factors:
        confidence = 0.0
    else:
        pos_weight = sum(f.weight for f in factors if f.polarity > 0)
        neg_weight = sum(f.weight for f in factors if f.polarity < 0)
        total_weight = pos_weight + neg_weight
        if total_weight == 0:
            confidence = 0.0
        else:
            major = max(pos_weight, neg_weight)
            confidence = (major / total_weight) * min(1.0, len(factors) / 5.0)

    # Clamp and map to band
    final_score = max(-3.0, min(3.0, total_score))
    band, summ_en, summ_hi = _get_band(final_score)

    return DomainScore(
        category=category,
        score=round(final_score, 2),
        band=band,
        confidence=round(confidence, 2),
        factors=sorted(factors, key=lambda f: -f.weight),
        summary_en=summ_en,
        summary_hi=summ_hi
    )


def _lord_of(house: int, lagna: str, planet_signs: dict[str, str]) -> str | None:
    from app.astrology.yogas import _lord_of_house
    return _lord_of_house(house, lagna, planet_signs)


def _parashari_vote(category: str, ctx: ScoringContext) -> tuple[float, list[Factor]]:
    factors = []
    score = 0.0
    
    # Map categories to primary houses
    cat_to_house = {
        'career': 10, 'finance': 2, 'marriage': 7, 'health': 1,
        'education': 4, 'children': 5, 'property': 4, 'spirituality': 9,
        'legal': 6, 'travel': 9, 'business': 7, 'relationships': 7,
        'accidents': 8, 'fame': 10, 'general': 1
    }
    h = cat_to_house.get(category, 1)
    lord = _lord_of(h, ctx.lagna, ctx.natal_signs)
    
    if lord:
        lord_str = ctx.shadbala.get(lord, 1.0)
        if lord_str >= 1.2:
            score += 1.0
            factors.append(Factor("parashari", 1, 1.0, f"Strong {h}th Lord ({lord}) promises solid foundation.", f"मजबूत {h}वां स्वामी ({lord}) ठोस नींव का वादा करता है।"))
        elif lord_str < 0.8:
            score -= 1.0
            factors.append(Factor("parashari", -1, 1.0, f"Weak {h}th Lord ({lord}) indicates early struggles.", f"कमजोर {h}वां स्वामी ({lord}) शुरुआती संघर्षों का संकेत देता है।"))

        av = ctx.avasthas.get(lord)
        if av:
            if av.score >= 0.5:
                score += 0.5
                factors.append(Factor("parashari", 1, 0.5, f"{lord} in {av.state_en} Avastha gives active results.", f"{lord} {av.state_hi} अवस्था में सक्रिय परिणाम देता है।"))
            elif av.score <= 0.2:
                score -= 0.5
                factors.append(Factor("parashari", -1, 0.5, f"{lord} in {av.state_en} Avastha delays full results.", f"{lord} {av.state_hi} अवस्था में पूर्ण परिणामों में देरी करता है।"))

    aspects = ctx.drishti_house.get(h, set())
    if "Jupiter" in aspects:
        score += 1.0
        factors.append(Factor("parashari", 1, 1.0, f"Jupiter aspects {h}th house, offering protection.", f"{h}वें भाव पर बृहस्पति की दृष्टि, सुरक्षा प्रदान करती है।"))
    if "Saturn" in aspects:
        score -= 0.5
        factors.append(Factor("parashari", -1, 0.5, f"Saturn aspects {h}th house, bringing delays and effort.", f"{h}वें भाव पर शनि की दृष्टि, देरी और प्रयास लाती है।"))
        
    return score, factors


def _jaimini_vote(category: str, ctx: ScoringContext) -> tuple[float, list[Factor]]:
    factors = []
    score = 0.0
    
    cat_to_karaka = {
        'career': 'AmK', 'finance': 'DK', 'marriage': 'DK', 'health': 'AK',
        'education': 'PK', 'children': 'PK', 'property': 'MK', 'spirituality': 'AK',
        'business': 'AmK', 'relationships': 'DK', 'fame': 'AmK', 'general': 'AK'
    }
    
    k = cat_to_karaka.get(category)
    if k:
        karaka_planet = None
        for p, role in ctx.chara_karakas.items():
            if role == k:
                karaka_planet = p
                break
                
        if karaka_planet:
            p_str = ctx.shadbala.get(karaka_planet, 1.0)
            if p_str >= 1.2:
                score += 1.0
                factors.append(Factor("jaimini", 1, 1.0, f"Strong {k} ({karaka_planet}) elevates prospects.", f"मजबूत {k} ({karaka_planet}) संभावनाओं को बढ़ाता है।"))
            elif p_str < 0.8:
                score -= 0.5
                factors.append(Factor("jaimini", -1, 0.5, f"Weak {k} ({karaka_planet}) creates obstacles.", f"कमजोर {k} ({karaka_planet}) बाधाएं पैदा करता है।"))
                
    return score, factors


def _nadi_vote(category: str, ctx: ScoringContext) -> tuple[float, list[Factor]]:
    factors = []
    score = 0.0
    
    if category == 'career':
        from app.astrology.nadi import nadi_career_signature
        nadi_sigs = nadi_career_signature(ctx.nadi_links)
        for sig in nadi_sigs:
            factors.append(Factor("nadi", 1, 0.5, f"Nadi Linkage: {sig}", f"नाड़ी संबंध: शनि के साथ ग्रहों का प्रभाव।"))
            score += 0.5
            
    return score, factors


def _kp_vote(category: str, ctx: ScoringContext) -> tuple[float, list[Factor]]:
    factors = []
    score = 0.0
    
    if ctx.kp_natal_cuspal >= 1.0:
        score += 1.2
        factors.append(Factor("kp", 1, 1.2, "KP Cuspal Sub-lord links to favorable houses.", "केपी कस्पल उप-स्वामी अनुकूल भावों से जुड़ता है।"))
    elif ctx.kp_natal_cuspal <= -1.0:
        score -= 1.2
        factors.append(Factor("kp", -1, 1.2, "KP Cuspal Sub-lord links to detrimental houses.", "केपी कस्पल उप-स्वामी हानिकारक भावों से जुड़ता है।"))
        
    if ctx.kp_natal_score > 0:
        score += 0.5
        factors.append(Factor("kp", 1, 0.5, "KP Moon Sub-lord is benefic.", "केपी चंद्र उप-स्वामी शुभ है।"))
    elif ctx.kp_natal_score < 0:
        score -= 0.5
        factors.append(Factor("kp", -1, 0.5, "KP Moon Sub-lord is malefic.", "केपी चंद्र उप-स्वामी अशुभ है।"))
        
    return score, factors


def _bhrigu_vote(category: str, ctx: ScoringContext) -> tuple[float, list[Factor]]:
    factors = []
    score = 0.0
    
    if ctx.bhrigu_bonus > 0:
        score += 1.0
        factors.append(Factor("bhrigu", 1, 1.0, "Bhrigu Bindu activated by positive natal planets.", "भृगु बिंदु जन्म ग्रहों द्वारा सक्रिय।"))
    elif ctx.bhrigu_bonus < 0:
        score -= 1.0
        factors.append(Factor("bhrigu", -1, 1.0, "Bhrigu Bindu afflicted by natal malefics.", "भृगु बिंदु जन्म पापी ग्रहों से पीड़ित।"))
        
    return score, factors
