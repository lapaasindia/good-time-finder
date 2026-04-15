def double_transit_score(
    category: str,
    transit_longs: dict[str, float],
    natal_houses: dict[str, int],
    natal_lagna: str
) -> float:
    """
    K.N. Rao's Double Transit theory.
    A major event happens when BOTH transiting Jupiter and transiting Saturn 
    aspect or conjunct the relevant house or its lord simultaneously.
    """
    
    cat_to_house = {
        'career': 10, 'finance': 2, 'business': 7, 'fame': 10,
        'marriage': 7, 'relationships': 7, 'health': 1, 'accidents': 8,
        'education': 4, 'property': 4, 'children': 5, 'spirituality': 9,
        'legal': 6, 'travel': 9, 'general': 1
    }
    
    target_house = cat_to_house.get(category, 1)
    
    t_jup_long = transit_longs.get("Jupiter")
    t_sat_long = transit_longs.get("Saturn")
    
    if t_jup_long is None or t_sat_long is None:
        return 0.0
        
    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    t_jup_sign_idx = int(t_jup_long // 30)
    t_sat_sign_idx = int(t_sat_long // 30)
    lagna_idx = ZODIAC_SIGNS.index(natal_lagna)
    
    jup_house = ((t_jup_sign_idx - lagna_idx) % 12) + 1
    sat_house = ((t_sat_sign_idx - lagna_idx) % 12) + 1
    
    jup_aspects = [jup_house, (jup_house + 4) % 12 or 12, (jup_house + 6) % 12 or 12, (jup_house + 8) % 12 or 12]
    sat_aspects = [sat_house, (sat_house + 2) % 12 or 12, (sat_house + 6) % 12 or 12, (sat_house + 9) % 12 or 12]
    
    score = 0.0
    if target_house in jup_aspects and target_house in sat_aspects:
        score += 1.5
        
    if category in ['accidents', 'legal']:
        # double transit on 8th or 6th triggers the bad event.
        score = -score
        
    return score
