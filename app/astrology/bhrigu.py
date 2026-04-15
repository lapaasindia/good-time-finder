import math

def calculate_bhrigu_bindu(moon_long: float, rahu_long: float) -> float:
    """Calculate the Bhrigu Bindu (Destiny Point).
    It is the mathematical midpoint between Rahu and the Moon.
    Returns the longitude in degrees [0, 360)."""
    
    # Distance from Rahu to Moon in zodiacal order
    dist = (moon_long - rahu_long) % 360
    
    # Midpoint
    bb = (rahu_long + dist / 2) % 360
    return bb

def bhrigu_transit_score(
    bb_long: float,
    transit_longitudes: dict[str, float]
) -> float:
    """Calculate score based on transits over the Bhrigu Bindu.
    When a major benefic (Jupiter) transits BB, big positive event.
    When a major malefic (Saturn, Rahu, Ketu) transits BB, big challenge.
    Returns a score modifier in [-1.5, 1.5]."""
    score = 0.0
    
    # Only slow-moving planets trigger major destiny events over BB.
    orbs = {
        "Jupiter": 3.0,  # degrees orb
        "Saturn": 2.0,
        "Rahu": 2.0,
        "Ketu": 2.0
    }
    
    for planet, orb in orbs.items():
        t_long = transit_longitudes.get(planet)
        if t_long is None:
            continue
            
        # Shortest distance on the 360 circle
        dist = abs((t_long - bb_long + 180) % 360 - 180)
        
        if dist <= orb:
            intensity = 1.0 - (dist / orb)  # 1.0 at exact conjunction, 0.0 at edge of orb
            
            if planet == "Jupiter":
                score += 1.5 * intensity
            elif planet in ["Saturn", "Rahu", "Ketu"]:
                score -= 1.5 * intensity
                
    return round(score, 3)
