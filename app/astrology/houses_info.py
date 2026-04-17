"""
House (Bhava) Meanings and Analysis — Bilingual Hindi + English.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class HouseInfo:
    house: int
    name_en: str
    name_hi: str
    domain_en: str
    domain_hi: str
    body_parts_en: str
    body_parts_hi: str
    karaka: str

HOUSE_DATA = {
    1: HouseInfo(1, "1st House (Lagna/Ascendant)", "प्रथम भाव (लग्न)", 
        "Self, physical body, appearance, health, temperament, ego, general life direction.",
        "स्वयं, शारीरिक शरीर, रूप, स्वास्थ्य, स्वभाव, अहंकार, जीवन की दिशा।",
        "Head, brain, face", "सिर, मस्तिष्क, चेहरा", "Sun"),
    2: HouseInfo(2, "2nd House (Dhana/Wealth)", "द्वितीय भाव (धन)",
        "Wealth, accumulated assets, family, speech, early education, food habits.",
        "धन, संचित संपत्ति, परिवार, वाणी, प्रारंभिक शिक्षा, खान-पान की आदतें।",
        "Face, right eye, teeth, tongue, throat", "चेहरा, दाहिनी आंख, दांत, जीभ, गला", "Jupiter, Mercury"),
    3: HouseInfo(3, "3rd House (Sahaja/Siblings)", "तृतीय भाव (सहज/पराक्रम)",
        "Courage, younger siblings, short journeys, communication, skills, hobbies.",
        "साहस, छोटे भाई-बहन, छोटी यात्राएं, संचार, कौशल, शौक।",
        "Neck, shoulders, arms, hands, right ear", "गर्दन, कंधे, बांहें, हाथ, दाहिना कान", "Mars, Mercury"),
    4: HouseInfo(4, "4th House (Bandhu/Mother/Comforts)", "चतुर्थ भाव (सुख/माता)",
        "Mother, home, properties, vehicles, inner peace, homeland, primary education.",
        "माता, घर, संपत्ति, वाहन, आंतरिक शांति, मातृभूमि, प्राथमिक शिक्षा।",
        "Chest, lungs, heart", "छाती, फेफड़े, हृदय", "Moon, Mercury"),
    5: HouseInfo(5, "5th House (Putra/Children/Intellect)", "पंचम भाव (संतान/विद्या)",
        "Children, intellect, romance, creativity, speculation, past life karma (Poorva Punya).",
        "संतान, बुद्धि, रोमांस, रचनात्मकता, सट्टा, पूर्व जन्म के कर्म (पूर्व पुण्य)।",
        "Stomach, liver, upper abdomen", "पेट, यकृत, ऊपरी पेट", "Jupiter"),
    6: HouseInfo(6, "6th House (Ari/Enemies/Disease)", "षष्ठ भाव (शत्रु/रोग/ऋण)",
        "Enemies, debts, diseases, litigation, daily work, maternal uncle, pets.",
        "शत्रु, ऋण, रोग, मुकदमेबाजी, दैनिक कार्य, मामा, पालतू जानवर।",
        "Intestines, lower abdomen, kidneys", "आंतें, निचला पेट, गुर्दे", "Mars, Saturn"),
    7: HouseInfo(7, "7th House (Yuvati/Spouse/Partnership)", "सप्तम भाव (विवाह/साझेदारी)",
        "Spouse, marriage, business partnerships, public image, open enemies, foreign travel.",
        "जीवनसाथी, विवाह, व्यापारिक साझेदारी, सार्वजनिक छवि, खुले शत्रु, विदेश यात्रा।",
        "Pelvic region, reproductive organs", "श्रोणि क्षेत्र, प्रजनन अंग", "Venus"),
    8: HouseInfo(8, "8th House (Randhra/Longevity/Obstacles)", "अष्टम भाव (आयु/मृत्यु)",
        "Longevity, sudden events, death, transformation, occult, inheritance, unearned wealth.",
        "आयु, अचानक घटनाएं, मृत्यु, परिवर्तन, गुप्त विद्या, विरासत, बिना कमाया धन।",
        "Excretory organs, external genitalia", "उत्सर्जन अंग, जननांग", "Saturn"),
    9: HouseInfo(9, "9th House (Dharma/Fortune/Father)", "नवम भाव (भाग्य/धर्म)",
        "Dharma, religion, luck, father, guru, higher education, long journeys.",
        "धर्म, भाग्य, पिता, गुरु, उच्च शिक्षा, लंबी यात्राएं।",
        "Thighs, hips", "जांघें, कूल्हे", "Jupiter, Sun"),
    10: HouseInfo(10, "10th House (Karma/Profession)", "दशम भाव (कर्म/करियर)",
        "Profession, career, status, authority, fame, government, public life.",
        "पेशा, करियर, स्थिति, अधिकार, प्रसिद्धि, सरकार, सार्वजनिक जीवन।",
        "Knees, joints", "घुटने, जोड़", "Sun, Mercury, Jupiter, Saturn"),
    11: HouseInfo(11, "11th House (Labha/Gains)", "एकादश भाव (आय/लाभ)",
        "Gains, income, fulfillment of desires, elder siblings, social network, friends.",
        "लाभ, आय, इच्छाओं की पूर्ति, बड़े भाई-बहन, सामाजिक नेटवर्क, मित्र।",
        "Calves, ankles, left ear", "पिंडलियां, टखने, बायां कान", "Jupiter"),
    12: HouseInfo(12, "12th House (Vyaya/Losses/Moksha)", "द्वादश भाव (व्यय/मोक्ष)",
        "Losses, expenditure, foreign settlement, hospitals, prisons, moksha (liberation), bed comforts.",
        "हानि, व्यय, विदेश में बसना, अस्पताल, जेल, मोक्ष, शयनकक्ष का सुख।",
        "Feet, toes, left eye", "पैर, पैर की उंगलियां, बाईं आंख", "Saturn, Ketu, Venus"),
}
