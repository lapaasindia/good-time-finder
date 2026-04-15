from enum import Enum


class EventNature(str, Enum):
    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"


class EventTag(str, Enum):
    GENERAL = "general"
    TRAVEL = "travel"
    MARRIAGE = "marriage"
    CAREER = "career"
    FINANCE = "finance"
    HEALTH = "health"
    EDUCATION = "education"
    PROPERTY = "property"
    CHILDREN = "children"
    SPIRITUALITY = "spirituality"
    LEGAL = "legal"
    FAME = "fame"
    RELATIONSHIPS = "relationships"
    BUSINESS = "business"
    ACCIDENTS = "accidents"
    MEDICAL = "medical"
    AGRICULTURE = "agriculture"
    PERSONAL = "personal"


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
