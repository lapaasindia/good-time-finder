"""
Personality profiles based on Lagna (Ascendant) and Moon sign.
Bilingual: Hindi + English.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PersonalityProfile:
    sign: str
    nature_en: str
    nature_hi: str
    career_en: str
    career_hi: str
    health_en: str
    health_hi: str
    relationship_en: str
    relationship_hi: str

ZODIAC_PROFILES = {
    "Aries": PersonalityProfile("Aries", 
        "Independent, energetic, courageous, impulsive, pioneering spirit.",
        "स्वतंत्र, ऊर्जावान, साहसी, आवेगी, अग्रणी भावना।",
        "Military, sports, engineering, leadership roles, entrepreneurship.",
        "सेना, खेल, इंजीनियरिंग, नेतृत्व की भूमिकाएं, उद्यमिता।",
        "Prone to head injuries, fevers, and inflammatory diseases. Need regular exercise.",
        "सिर की चोटों, बुखार और सूजन संबंधी बीमारियों की संभावना। नियमित व्यायाम की आवश्यकता।",
        "Passionate but can be impatient. Needs an active partner.",
        "भावुक लेकिन अधीर हो सकते हैं। एक सक्रिय साथी की आवश्यकता है।"),
        
    "Taurus": PersonalityProfile("Taurus",
        "Patient, reliable, stubborn, loves luxury, practical, grounded.",
        "धैर्यवान, विश्वसनीय, जिद्दी, विलासिता प्रेमी, व्यावहारिक, जमीन से जुड़े।",
        "Finance, arts, agriculture, banking, music, luxury goods.",
        "वित्त, कला, कृषि, बैंकिंग, संगीत, विलासिता की वस्तुएं।",
        "Throat and neck issues, thyroid, weight gain if inactive.",
        "गले और गर्दन की समस्याएं, थायराइड, निष्क्रिय होने पर वजन बढ़ना।",
        "Loyal and devoted, seeks stability and sensory comfort.",
        "वफादार और समर्पित, स्थिरता और संवेदी आराम चाहता है।"),
        
    "Gemini": PersonalityProfile("Gemini",
        "Versatile, intellectual, communicative, restless, curious.",
        "बहुमुखी, बौद्धिक, संचारी, बेचैन, जिज्ञासु।",
        "Writing, media, sales, IT, education, travel industry.",
        "लेखन, मीडिया, बिक्री, आईटी, शिक्षा, यात्रा उद्योग।",
        "Nervous exhaustion, respiratory issues, speech/hearing disorders.",
        "तंत्रिका थकावट, श्वसन संबंधी समस्याएं, वाणी/श्रवण विकार।",
        "Needs intellectual stimulation and varied conversations in love.",
        "बौद्धिक उत्तेजना और प्यार में विविध बातचीत की आवश्यकता है।"),
        
    "Cancer": PersonalityProfile("Cancer",
        "Emotional, nurturing, protective, moody, family-oriented.",
        "भावनात्मक, पोषण करने वाला, सुरक्षात्मक, मूडी, परिवार-उन्मुख।",
        "Healthcare, teaching, real estate, hospitality, psychology.",
        "स्वास्थ्य सेवा, शिक्षण, रियल एस्टेट, आतिथ्य, मनोविज्ञान।",
        "Stomach issues, digestive disorders, emotionally triggered illnesses.",
        "पेट की समस्याएं, पाचन विकार, भावनात्मक रूप से उत्पन्न बीमारियां।",
        "Deeply devoted, sensitive, seeks emotional security and home life.",
        "गहराई से समर्पित, संवेदनशील, भावनात्मक सुरक्षा और घरेलू जीवन चाहता है।"),
        
    "Leo": PersonalityProfile("Leo",
        "Confident, generous, dramatic, authoritative, proud, loyal.",
        "आत्मविश्वासी, उदार, नाटकीय, आधिकारिक, अभिमानी, वफादार।",
        "Management, politics, acting, entertainment, administration.",
        "प्रबंधन, राजनीति, अभिनय, मनोरंजन, प्रशासन।",
        "Heart issues, spine/back problems, blood pressure.",
        "हृदय की समस्याएं, रीढ़/पीठ की समस्याएं, रक्तचाप।",
        "Warm, passionate, loves to be admired and shower partner with gifts.",
        "गर्मजोशी से भरा, भावुक, प्रशंसित होना पसंद करता है और साथी को उपहारों से नहलाता है।"),
        
    "Virgo": PersonalityProfile("Virgo",
        "Analytical, meticulous, modest, critical, service-oriented.",
        "विश्लेषणात्मक, सूक्ष्म, विनम्र, आलोचक, सेवा-उन्मुख।",
        "Accounts, medicine, editing, data analysis, healing professions.",
        "लेखा, चिकित्सा, संपादन, डेटा विश्लेषण, उपचार पेशे।",
        "Intestinal issues, nervous stomach, anxiety-related health drops.",
        "आंतों की समस्याएं, तंत्रिका पेट, चिंता से संबंधित स्वास्थ्य गिरावट।",
        "Practical in love, shows affection through acts of service.",
        "प्यार में व्यावहारिक, सेवा कार्यों के माध्यम से स्नेह दिखाता है।"),
        
    "Libra": PersonalityProfile("Libra",
        "Diplomatic, artistic, social, indecisive, harmony-seeking.",
        "राजनयिक, कलात्मक, सामाजिक, अनिर्णायक, सद्भाव चाहने वाला।",
        "Law, design, diplomacy, public relations, arts, counseling.",
        "कानून, डिजाइन, कूटनीति, जनसंपर्क, कला, परामर्श।",
        "Kidney issues, lower back pain, sugar/blood imbalances.",
        "गुर्दे की समस्याएं, पीठ के निचले हिस्से में दर्द, चीनी/रक्त असंतुलन।",
        "Partnership is paramount; seeks balance, romance, and equality.",
        "साझेदारी सर्वोपरि है; संतुलन, रोमांस और समानता चाहता है।"),
        
    "Scorpio": PersonalityProfile("Scorpio",
        "Intense, secretive, passionate, transformative, magnetic.",
        "तीव्र, गुप्त, भावुक, परिवर्तनकारी, चुंबकीय।",
        "Research, occult, surgery, investigation, psychology, mining.",
        "शोध, गुप्त विद्या, शल्य चिकित्सा, जांच, मनोविज्ञान, खनन।",
        "Reproductive organ issues, excretory system, hidden diseases.",
        "प्रजनन अंग की समस्याएं, उत्सर्जन प्रणाली, छिपी हुई बीमारियां।",
        "Deep, possessive, deeply emotional and intensely loyal.",
        "गहरा, अधिकार जताने वाला, गहराई से भावनात्मक और तीव्रता से वफादार।"),
        
    "Sagittarius": PersonalityProfile("Sagittarius",
        "Optimistic, philosophical, adventurous, blunt, freedom-loving.",
        "आशावादी, दार्शनिक, साहसी, स्पष्टवादी, स्वतंत्रता प्रेमी।",
        "Teaching, law, travel, theology, publishing, sports.",
        "शिक्षण, कानून, यात्रा, धर्मशास्त्र, प्रकाशन, खेल।",
        "Hip/thigh issues, liver problems, obesity from over-indulgence.",
        "कूल्हे/जांघ की समस्याएं, यकृत की समस्याएं, अधिक भोग से मोटापा।",
        "Needs space and honesty; loves exploring the world with their partner.",
        "स्थान और ईमानदारी की आवश्यकता; साथी के साथ दुनिया की खोज करना पसंद है।"),
        
    "Capricorn": PersonalityProfile("Capricorn",
        "Disciplined, ambitious, cautious, pragmatic, responsible.",
        "अनुशासित, महत्वाकांक्षी, सतर्क, व्यावहारिक, जिम्मेदार।",
        "Corporate business, government, engineering, agriculture, management.",
        "कॉर्पोरेट व्यवसाय, सरकार, इंजीनियरिंग, कृषि, प्रबंधन।",
        "Knee problems, joint aches, dental issues, skin dryness.",
        "घुटने की समस्याएं, जोड़ों का दर्द, दांतों की समस्याएं, त्वचा का रूखापन।",
        "Takes time to open up; highly committed and values traditional structures.",
        "खुलने में समय लगता है; अत्यधिक प्रतिबद्ध और पारंपरिक संरचनाओं को महत्व देता है।"),
        
    "Aquarius": PersonalityProfile("Aquarius",
        "Progressive, humanitarian, eccentric, independent, intellectual.",
        "प्रगतिशील, मानवीय, विलक्षण, स्वतंत्र, बौद्धिक।",
        "Technology, social work, science, aviation, astrology, IT.",
        "प्रौद्योगिकी, सामाजिक कार्य, विज्ञान, विमानन, ज्योतिष, आईटी।",
        "Ankle sprains, circulatory issues, nervous disorders.",
        "टखने की मोच, संचार संबंधी समस्याएं, तंत्रिका विकार।",
        "Values friendship in love; needs intellectual connection and freedom.",
        "प्यार में दोस्ती को महत्व देता है; बौद्धिक संबंध और स्वतंत्रता की आवश्यकता है।"),
        
    "Pisces": PersonalityProfile("Pisces",
        "Compassionate, intuitive, dreamy, escapist, artistic.",
        "करुणामय, सहज, स्वप्निल, पलायनवादी, कलात्मक।",
        "Arts, medicine, spirituality, marine, photography, charity.",
        "कला, चिकित्सा, आध्यात्मिकता, समुद्री, फोटोग्राफी, दान।",
        "Foot problems, immune deficiencies, vulnerability to addictions.",
        "पैर की समस्याएं, प्रतिरक्षा की कमी, व्यसनों के प्रति भेद्यता।",
        "Highly romantic, self-sacrificing, seeks a soulmate connection.",
        "अत्यधिक रोमांटिक, आत्म-बलिदानी, जीवनसाथी (सोलमेट) के संबंध की तलाश में।"),
}
