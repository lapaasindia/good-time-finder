"""
Dasha × Domain Matrix builder (Phase 5.4).

For the current Maha/Antar/Pratyantar dasha lords, scores each of the
10 life domains based on:
  a) Is the dasha lord a natural karaka for that domain?
  b) Lord's shadbala strength
  c) Lord's natal house placement relevance
"""
from __future__ import annotations


# Natural karakatva: which domains each planet naturally signifies
PLANET_KARAKATVA: dict[str, set[str]] = {
    "Sun":     {"career", "fame", "health", "spirituality"},
    "Moon":    {"health", "travel", "property", "children"},
    "Mars":    {"property", "legal", "career", "health"},
    "Mercury": {"education", "business", "finance", "career"},
    "Jupiter": {"education", "children", "spirituality", "finance"},
    "Venus":   {"marriage", "relationships", "finance", "travel"},
    "Saturn":  {"career", "legal", "property", "spirituality"},
    "Rahu":    {"career", "travel", "legal", "fame"},
    "Ketu":    {"spirituality", "health", "legal", "education"},
}

# Primary house for each domain
DOMAIN_PRIMARY_HOUSE: dict[str, int] = {
    "career": 10, "finance": 2, "marriage": 7, "health": 1,
    "education": 4, "children": 5, "property": 4, "spirituality": 9,
    "legal": 6, "travel": 9,
}

ALL_DOMAINS = list(DOMAIN_PRIMARY_HOUSE.keys())


def _lord_activation(
    planet: str | None,
    domain: str,
    shadbala: dict[str, float],
    natal_houses: dict[str, int],
) -> dict:
    """Score how strongly a dasha lord activates a specific domain."""
    if not planet:
        return {"planet": None, "activation": 0.0, "reason": "No dasha lord active."}

    score = 0.0
    reasons: list[str] = []

    # (a) Natural karaka match
    karakas = PLANET_KARAKATVA.get(planet, set())
    if domain in karakas:
        score += 1.5
        reasons.append(f"{planet} is natural karaka for {domain}")

    # (b) Shadbala strength of the lord
    strength = shadbala.get(planet, 1.0)
    if strength >= 1.3:
        score += 0.8
        reasons.append(f"{planet} has strong shadbala ({strength:.2f})")
    elif strength >= 1.0:
        score += 0.3
        reasons.append(f"{planet} has adequate shadbala ({strength:.2f})")
    elif strength < 0.8:
        score -= 0.5
        reasons.append(f"{planet} has weak shadbala ({strength:.2f})")

    # (c) House placement relevance
    house = natal_houses.get(planet)
    primary_house = DOMAIN_PRIMARY_HOUSE.get(domain, 1)
    if house == primary_house:
        score += 1.0
        reasons.append(f"{planet} occupies the primary house ({house}H) for {domain}")
    elif house and abs(house - primary_house) <= 1:
        score += 0.3
        reasons.append(f"{planet} occupies house {house}, adjacent to {domain}'s primary house")

    # Band label
    if score >= 2.0:
        band = "High"
    elif score >= 1.0:
        band = "Medium"
    elif score >= 0.0:
        band = "Low"
    else:
        band = "Nil"

    return {
        "planet": planet,
        "activation": round(score, 2),
        "band": band,
        "reasons": reasons,
    }


def build_dasha_domain_matrix(
    maha_lord: str | None,
    antar_lord: str | None,
    pratyantar_lord: str | None,
    shadbala: dict[str, float],
    natal_houses: dict[str, int],
) -> list[dict]:
    """
    Build a 10 × 3 matrix: for each of the 10 domains, compute activation
    levels from the current Maha, Antar, and Pratyantar dasha lords.

    Returns a list of 10 dicts, one per domain:
      {domain, maha: {planet, activation, band, reasons},
              antar: {...}, pratyantar: {...}, composite}
    """
    rows: list[dict] = []
    for domain in ALL_DOMAINS:
        maha_act = _lord_activation(maha_lord, domain, shadbala, natal_houses)
        antar_act = _lord_activation(antar_lord, domain, shadbala, natal_houses)
        prat_act = _lord_activation(pratyantar_lord, domain, shadbala, natal_houses)

        # Weighted composite: Maha 50%, Antar 30%, Pratyantar 20%
        composite = (
            maha_act["activation"] * 0.50
            + antar_act["activation"] * 0.30
            + prat_act["activation"] * 0.20
        )

        rows.append({
            "domain": domain,
            "maha": maha_act,
            "antar": antar_act,
            "pratyantar": prat_act,
            "composite": round(composite, 2),
        })

    # Sort by composite descending
    rows.sort(key=lambda r: r["composite"], reverse=True)
    return rows
