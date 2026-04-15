import swisseph as swe

# KP Sub-lord calculation
# Each nakshatra (13°20' or 800') is divided into 9 sub-parts, proportional to the Vimshottari Dasha years.
# Total Dasha years = 120.

DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

def kp_sublord(longitude: float) -> tuple[str, str, str]:
    """Calculate Sign Lord, Star Lord (Nakshatra), and Sub Lord for a given longitude.
    Returns (Sign_Lord, Star_Lord, Sub_Lord)."""
    
    # 1. Sign Lord
    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    SIGN_LORDS = [
        "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
        "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
    ]
    sign_idx = int(longitude // 30)
    sign_lord = SIGN_LORDS[sign_idx]
    
    # 2. Star Lord (Nakshatra)
    nak_idx = int(longitude // (360 / 27))
    star_lord = DASHA_ORDER[nak_idx % 9]
    
    # 3. Sub Lord
    # Longitude within the Nakshatra
    nak_start_deg = nak_idx * (360 / 27)
    rem_deg = longitude - nak_start_deg
    
    # Starting planet for the sub-lords is the Star Lord itself.
    start_idx = DASHA_ORDER.index(star_lord)
    
    # Total extent of Nakshatra = 13.3333 degrees = 800 minutes
    # A sublord extent = (Dasha Years / 120) * 13.3333 degrees
    
    accumulated_deg = 0.0
    sub_lord = ""
    for i in range(9):
        lord = DASHA_ORDER[(start_idx + i) % 9]
        lord_extent = (DASHA_YEARS[lord] / 120.0) * (360 / 27)
        accumulated_deg += lord_extent
        if rem_deg <= accumulated_deg:
            sub_lord = lord
            break
            
    return sign_lord, star_lord, sub_lord

def kp_score(planet_longs: dict[str, float], lagna_long: float, category: str) -> float:
    """Very simplified KP rules based on Sub Lord. 
    Returns a score modifier [-0.5, 0.5].
    In real KP, sub-lords act as the ultimate decider of events."""
    if not planet_longs: return 0.0
    
    # Check Moon's sublord (very important in KP)
    moon_long = planet_longs.get("Moon")
    if not moon_long: return 0.0
    
    _, _, moon_sub_lord = kp_sublord(moon_long)
    
    score = 0.0
    # Good sub-lords for Moon generally give good results
    if moon_sub_lord in ["Jupiter", "Venus", "Mercury", "Moon"]:
        score += 0.2
    elif moon_sub_lord in ["Saturn", "Rahu", "Ketu", "Mars"]:
        score -= 0.2
        
    return score
