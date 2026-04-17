"""
Planet (Graha) Meanings, Relationships, and Nature — Bilingual Hindi + English.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PlanetInfo:
    planet: str
    name_hi: str
    nature_en: str
    nature_hi: str
    significations_en: str
    significations_hi: str
    friends: list[str]
    enemies: list[str]
    neutral: list[str]

PLANET_DATA = {
    "Sun": PlanetInfo("Sun", "सूर्य (Surya)", 
        "Soul, Ego, Father, Authority, Government, Leadership, Vitality.",
        "आत्मा, अहंकार, पिता, अधिकार, सरकार, नेतृत्व, जीवन शक्ति।",
        "King, power, bones, heart, right eye, copper, ruby, east.",
        "राजा, शक्ति, हड्डियां, हृदय, दाहिनी आंख, तांबा, माणिक, पूर्व।",
        ["Moon", "Mars", "Jupiter"], ["Saturn", "Venus", "Rahu", "Ketu"], ["Mercury"]),
        
    "Moon": PlanetInfo("Moon", "चंद्र (Chandra)",
        "Mind, Emotions, Mother, Public, Intuition, Fluids, Changeability.",
        "मन, भावनाएं, माता, जनता, अंतर्ज्ञान, तरल पदार्थ, परिवर्तनशीलता।",
        "Queen, water, blood, left eye, silver, pearl, north-west.",
        "रानी, जल, रक्त, बाईं आंख, चांदी, मोती, उत्तर-पश्चिम।",
        ["Sun", "Mercury"], ["Rahu", "Ketu"], ["Mars", "Jupiter", "Venus", "Saturn"]),
        
    "Mars": PlanetInfo("Mars", "मंगल (Mangal)",
        "Courage, Energy, Siblings, Real Estate, Logic, War, Ambition.",
        "साहस, ऊर्जा, भाई-बहन, अचल संपत्ति, तर्क, युद्ध, महत्वाकांक्षा।",
        "Commander, blood marrow, muscles, land, copper, coral, south.",
        "सेनापति, मज्जा, मांसपेशियां, भूमि, तांबा, मूंगा, दक्षिण।",
        ["Sun", "Moon", "Jupiter"], ["Mercury", "Rahu", "Ketu"], ["Venus", "Saturn"]),
        
    "Mercury": PlanetInfo("Mercury", "बुध (Budha)",
        "Intellect, Speech, Business, Writing, Logic, Education, Nerves.",
        "बुद्धि, वाणी, व्यापार, लेखन, तर्क, शिक्षा, नसें।",
        "Prince, skin, nervous system, trade, green, emerald, north.",
        "राजकुमार, त्वचा, तंत्रिका तंत्र, व्यापार, हरा, पन्ना, उत्तर।",
        ["Sun", "Venus"], ["Moon"], ["Mars", "Jupiter", "Saturn"]),
        
    "Jupiter": PlanetInfo("Jupiter", "गुरु/बृहस्पति (Guru)",
        "Wisdom, Religion, Wealth, Children, Expansion, Optimism, Higher Knowledge.",
        "ज्ञान, धर्म, धन, संतान, विस्तार, आशावाद, उच्च ज्ञान।",
        "Minister, fat, liver, gold, yellow sapphire, north-east.",
        "मंत्री, वसा, यकृत, सोना, पुखराज, उत्तर-पूर्व।",
        ["Sun", "Moon", "Mars"], ["Mercury", "Venus"], ["Saturn", "Rahu", "Ketu"]),
        
    "Venus": PlanetInfo("Venus", "शुक्र (Shukra)",
        "Love, Beauty, Spouse, Luxury, Arts, Vehicles, Pleasure.",
        "प्रेम, सौंदर्य, जीवनसाथी, विलासिता, कला, वाहन, आनंद।",
        "Minister, reproductive system, semen, silver/diamond, south-east.",
        "मंत्री, प्रजनन प्रणाली, वीर्य, चांदी/हीरा, दक्षिण-पूर्व।",
        ["Mercury", "Saturn", "Rahu", "Ketu"], ["Sun", "Moon"], ["Mars", "Jupiter"]),
        
    "Saturn": PlanetInfo("Saturn", "शनि (Shani)",
        "Discipline, Hard Work, Delays, Sorrow, Longevity, Servants, Karma.",
        "अनुशासन, कड़ी मेहनत, देरी, दुख, आयु, सेवक, कर्म।",
        "Servant, teeth, bones, chronic disease, iron, blue sapphire, west.",
        "सेवक, दांत, हड्डियां, जीर्ण रोग, लोहा, नीलम, पश्चिम।",
        ["Mercury", "Venus", "Rahu"], ["Sun", "Moon", "Mars"], ["Jupiter", "Ketu"]),
        
    "Rahu": PlanetInfo("Rahu", "राहु (Rahu)",
        "Materialism, Illusion, Foreigners, Sudden Events, Obsession, Technology.",
        "भौतिकवाद, भ्रम, विदेशी, अचानक घटनाएं, जुनून, तकनीक।",
        "Outcast, poison, phobias, unseen diseases, lead, hessonite, south-west.",
        "बहिष्कृत, विष, भय, अदृश्य रोग, सीसा, गोमेद, दक्षिण-पश्चिम।",
        ["Venus", "Saturn"], ["Sun", "Moon", "Mars", "Jupiter"], ["Mercury"]),
        
    "Ketu": PlanetInfo("Ketu", "केतु (Ketu)",
        "Spirituality, Detachment, Moksha, Intuition, Deep Research, Occult.",
        "आध्यात्मिकता, वैराग्य, मोक्ष, अंतर्ज्ञान, गहरा शोध, गुप्त विद्या।",
        "Ascetic, viral diseases, hidden matters, cat's eye, no specific direction.",
        "तपस्वी, वायरल रोग, छिपे हुए मामले, लहसुनिया, कोई विशिष्ट दिशा नहीं।",
        ["Mars", "Venus", "Saturn"], ["Sun", "Moon"], ["Mercury", "Jupiter"]),
}
