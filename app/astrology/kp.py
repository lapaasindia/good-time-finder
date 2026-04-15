import swisseph as swe
from datetime import datetime
import pytz

# KP Sub-lord calculation
# Each nakshatra (13°20' or 800') is divided into 9 sub-parts, proportional to the Vimshottari Dasha years.
# Total Dasha years = 120.

DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

def kp_sublord(longitude: float) -> tuple[str, str, str]:
    longitude = longitude % 360
    
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
    
    nak_idx = int(longitude // (360 / 27))
    star_lord = DASHA_ORDER[nak_idx % 9]
    
    nak_start_deg = nak_idx * (360 / 27)
    rem_deg = longitude - nak_start_deg
    
    start_idx = DASHA_ORDER.index(star_lord)
    
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
    if not planet_longs: return 0.0
    
    moon_long = planet_longs.get("Moon")
    if not moon_long: return 0.0
    
    _, _, moon_sub_lord = kp_sublord(moon_long)
    
    score = 0.0
    if moon_sub_lord in ["Jupiter", "Venus", "Mercury", "Moon"]:
        score += 0.2
    elif moon_sub_lord in ["Saturn", "Rahu", "Ketu", "Mars"]:
        score -= 0.2
        
    return score

def true_kp_cuspal_score(
    category: str,
    birth_dt: datetime,
    lat: float,
    lon: float,
    natal_longs: dict[str, float],
    natal_houses: dict[str, int]
) -> float:
    cat_to_primary = {
        'career': 10, 'finance': 2, 'business': 7, 'fame': 10,
        'marriage': 7, 'relationships': 7, 'health': 1, 'accidents': 8,
        'education': 4, 'property': 4, 'children': 5, 'spirituality': 9,
        'legal': 6, 'travel': 9, 'general': 1
    }
    
    cat_to_supporting = {
        'career': [2, 6, 10, 11], 'finance': [2, 6, 11], 'business': [2, 7, 10, 11],
        'fame': [1, 10, 11], 'marriage': [2, 7, 11], 'relationships': [2, 5, 7, 11],
        'health': [1, 5, 11], 'accidents': [8, 12, 6], 'education': [4, 9, 11],
        'property': [4, 11, 12], 'children': [2, 5, 11], 'spirituality': [9, 12],
        'legal': [6, 8, 12], 'travel': [3, 9, 12], 'general': [1, 9, 11]
    }
    
    primary = cat_to_primary.get(category, 1)
    supporting = cat_to_supporting.get(category, [1, 9, 11])
    
    utc_dt = birth_dt.astimezone(pytz.UTC)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    try:
        cusps, _ = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    except:
        try:
            cusps, _ = swe.houses_ex(jd, lat, lon, b'E', swe.FLG_SIDEREAL)
        except:
            return 0.0
            
    if len(cusps) > primary:
        cusp_long = cusps[primary]
    else:
        return 0.0
        
    _, _, cusp_sl = kp_sublord(cusp_long)
    if not cusp_sl: return 0.0
        
    sl_natal_long = natal_longs.get(cusp_sl)
    if sl_natal_long is None: return 0.0
        
    _, sl_star_lord, _ = kp_sublord(sl_natal_long)
    star_lord_house = natal_houses.get(sl_star_lord)
    
    score = 0.0
    if star_lord_house in supporting:
        score += 1.0
        
    detrimental = [6, 8, 12]
    if category in ['health', 'accidents', 'legal']:
        detrimental = [6, 8, 12] # Sickness, loss, hospital
        
    if star_lord_house in detrimental and star_lord_house not in supporting:
        score -= 1.0
        
    if category in ['accidents', 'legal']:
        # If it triggers the event, it is a BAD prediction (score < 0)
        score = -score
            
    return score
