"""
Nadi-style Nakshatra-based predictions.

Each of the 27 Nakshatras carries inherent qualities that shape a person's
temperament, life themes, health tendencies, and spiritual inclinations.
This module provides per-nakshatra personality profiles, strengths, challenges,
and career/relationship guidance based on classical Nadi Jyotish texts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NakshatraProfile:
    nakshatra: str
    ruling_planet: str
    deity: str
    symbol: str
    guna: str  # Sattva / Rajas / Tamas
    nature: str  # Deva / Manushya / Rakshasa
    element: str
    personality: str
    strengths: list[str]
    challenges: list[str]
    career_hints: list[str]
    health_areas: list[str]
    spiritual_theme: str


NAKSHATRA_PROFILES: dict[str, NakshatraProfile] = {
    "Ashwini": NakshatraProfile(
        nakshatra="Ashwini", ruling_planet="Ketu", deity="Ashwini Kumaras",
        symbol="Horse Head", guna="Sattva", nature="Deva", element="Earth",
        personality="Quick-acting, healing, pioneering. The native is energetic, impatient, and drawn to medicine or speed-related activities.",
        strengths=["Fast learner", "Natural healer", "Courageous initiative", "Youthful energy"],
        challenges=["Impulsiveness", "Difficulty completing projects", "Restlessness"],
        career_hints=["Medicine/healing", "Sports/racing", "Emergency services", "Entrepreneurship"],
        health_areas=["Head/brain", "Upper body", "Nervous system"],
        spiritual_theme="Awakening and rapid spiritual progress through selfless healing.",
    ),
    "Bharani": NakshatraProfile(
        nakshatra="Bharani", ruling_planet="Venus", deity="Yama",
        symbol="Yoni (womb)", guna="Rajas", nature="Manushya", element="Earth",
        personality="Intense, creative, transformative. The native deals with themes of birth, death, and rebirth throughout life.",
        strengths=["Creative power", "Endurance", "Loyalty", "Artistic talent"],
        challenges=["Extremism", "Jealousy", "Moral conflicts", "Overindulgence"],
        career_hints=["Arts/entertainment", "Law/justice", "Psychology", "Fertility/childcare"],
        health_areas=["Reproductive system", "Lower abdomen", "Kidneys"],
        spiritual_theme="Transformation through acceptance of life's dualities — creation and destruction.",
    ),
    "Krittika": NakshatraProfile(
        nakshatra="Krittika", ruling_planet="Sun", deity="Agni",
        symbol="Razor/Flame", guna="Rajas", nature="Rakshasa", element="Fire",
        personality="Sharp, purifying, authoritative. The native has a critical eye, strong willpower, and a need for truth.",
        strengths=["Sharp intellect", "Purification ability", "Leadership", "Determination"],
        challenges=["Harsh speech", "Overcritical", "Anger issues", "Isolation"],
        career_hints=["Military/defence", "Cooking/culinary arts", "Fire services", "Surgery"],
        health_areas=["Digestion", "Eyes", "Fever-related ailments"],
        spiritual_theme="Purification of ego through the fire of self-discipline and tapas.",
    ),
    "Rohini": NakshatraProfile(
        nakshatra="Rohini", ruling_planet="Moon", deity="Brahma",
        symbol="Chariot/Ox Cart", guna="Rajas", nature="Manushya", element="Earth",
        personality="Attractive, sensual, creative. The native is drawn to beauty, luxury, and material comfort. Very fertile and productive energy.",
        strengths=["Beauty/charm", "Material abundance", "Artistic sense", "Fertility"],
        challenges=["Possessiveness", "Material attachment", "Jealousy", "Stubbornness"],
        career_hints=["Fashion/beauty", "Agriculture", "Real estate", "Banking/finance"],
        health_areas=["Throat", "Neck", "Reproductive organs"],
        spiritual_theme="Finding the divine in material creation — beauty as a path to God.",
    ),
    "Mrigashira": NakshatraProfile(
        nakshatra="Mrigashira", ruling_planet="Mars", deity="Soma (Moon)",
        symbol="Deer Head", guna="Tamas", nature="Deva", element="Earth",
        personality="Curious, searching, gentle yet restless. The native is always seeking — knowledge, love, or truth.",
        strengths=["Research ability", "Gentle nature", "Curiosity", "Adaptability"],
        challenges=["Indecisiveness", "Fickleness", "Suspicion", "Nervous energy"],
        career_hints=["Research/academia", "Writing", "Travel industry", "Textiles"],
        health_areas=["Nose/sinuses", "Shoulders", "Upper body joints"],
        spiritual_theme="The spiritual search — the soul's eternal quest for its true home.",
    ),
    "Ardra": NakshatraProfile(
        nakshatra="Ardra", ruling_planet="Rahu", deity="Rudra",
        symbol="Teardrop/Diamond", guna="Tamas", nature="Manushya", element="Water",
        personality="Intense, intellectual, storm-like. The native experiences powerful transformations and emotional upheavals that lead to growth.",
        strengths=["Intellectual power", "Research ability", "Determination", "Empathy through suffering"],
        challenges=["Destructive tendencies", "Emotional storms", "Critical nature", "Arrogance"],
        career_hints=["Technology/IT", "Research", "Pharmaceuticals", "Electrical engineering"],
        health_areas=["Lungs", "Nervous system", "Asthma", "Mental health"],
        spiritual_theme="Destruction of ego through Rudra's storms — rebirth through suffering.",
    ),
    "Punarvasu": NakshatraProfile(
        nakshatra="Punarvasu", ruling_planet="Jupiter", deity="Aditi",
        symbol="Bow/Quiver", guna="Sattva", nature="Deva", element="Water",
        personality="Optimistic, renewing, philosophical. The native bounces back from adversity with renewed hope and wisdom.",
        strengths=["Resilience", "Optimism", "Philosophical mind", "Generosity"],
        challenges=["Over-idealism", "Simplistic thinking", "Complacency", "Indecisiveness"],
        career_hints=["Teaching", "Publishing", "Counselling", "Import/export"],
        health_areas=["Chest", "Stomach", "Ear infections"],
        spiritual_theme="Return to the source — the soul's journey back to its divine origin.",
    ),
    "Pushya": NakshatraProfile(
        nakshatra="Pushya", ruling_planet="Saturn", deity="Brihaspati",
        symbol="Cow Udder/Lotus", guna="Tamas", nature="Deva", element="Water",
        personality="Nourishing, conservative, dutiful. Considered the most auspicious nakshatra — the native is caring, wise, and community-oriented.",
        strengths=["Nourishing nature", "Wisdom", "Patience", "Community service"],
        challenges=["Rigidity", "Stubbornness", "Over-sacrifice", "Depression"],
        career_hints=["Government", "Education", "Dairy/agriculture", "Charitable work"],
        health_areas=["Chest/lungs", "Stomach", "Skin conditions"],
        spiritual_theme="Selfless service (Seva) as the highest spiritual path.",
    ),
    "Ashlesha": NakshatraProfile(
        nakshatra="Ashlesha", ruling_planet="Mercury", deity="Nagas (Serpents)",
        symbol="Coiled Serpent", guna="Sattva", nature="Rakshasa", element="Water",
        personality="Hypnotic, shrewd, mystical. The native has penetrating insight, occult interests, and a magnetic personality.",
        strengths=["Intuition", "Strategic mind", "Mystical ability", "Kundalini potential"],
        challenges=["Manipulation", "Distrust", "Poison tongue", "Emotional coldness"],
        career_hints=["Occult sciences", "Pharmacy", "Psychology", "Intelligence/espionage"],
        health_areas=["Joints", "Nervous system", "Poison-related ailments"],
        spiritual_theme="Kundalini awakening — mastery of the serpent power within.",
    ),
    "Magha": NakshatraProfile(
        nakshatra="Magha", ruling_planet="Ketu", deity="Pitris (Ancestors)",
        symbol="Royal Throne", guna="Tamas", nature="Rakshasa", element="Water",
        personality="Regal, authoritative, ancestral. The native carries strong past-life merit, leadership ability, and connection to lineage.",
        strengths=["Natural authority", "Ancestral blessings", "Charisma", "Tradition"],
        challenges=["Arrogance", "Caste/class consciousness", "Domination", "Attachment to status"],
        career_hints=["Politics", "Administration", "Heritage work", "Spiritual leadership"],
        health_areas=["Heart", "Spine", "Blood pressure"],
        spiritual_theme="Honouring the ancestors and fulfilling one's dharmic duty in the lineage.",
    ),
    "Purva Phalguni": NakshatraProfile(
        nakshatra="Purva Phalguni", ruling_planet="Venus", deity="Bhaga",
        symbol="Front legs of bed/Hammock", guna="Tamas", nature="Manushya", element="Water",
        personality="Pleasure-loving, artistic, social. The native seeks comfort, romance, and creative expression.",
        strengths=["Charm", "Artistic talent", "Social skills", "Generosity"],
        challenges=["Laziness", "Vanity", "Over-indulgence", "Superficiality"],
        career_hints=["Entertainment", "Hospitality", "Arts", "Event management"],
        health_areas=["Heart", "Reproductive system", "Back/spine"],
        spiritual_theme="Finding divine love through human relationships and creative expression.",
    ),
    "Uttara Phalguni": NakshatraProfile(
        nakshatra="Uttara Phalguni", ruling_planet="Sun", deity="Aryaman",
        symbol="Back legs of bed", guna="Rajas", nature="Manushya", element="Fire",
        personality="Responsible, helpful, contractual. The native excels in partnerships, agreements, and social contracts.",
        strengths=["Reliability", "Helpfulness", "Leadership", "Commitment"],
        challenges=["Over-giving", "Rigidity", "Controlling nature", "Burnout"],
        career_hints=["Social work", "HR/management", "Law", "Marriage counselling"],
        health_areas=["Digestive system", "Spine", "Hands/arms"],
        spiritual_theme="Service through sacred contracts and partnerships (dharmic agreements).",
    ),
    "Hasta": NakshatraProfile(
        nakshatra="Hasta", ruling_planet="Moon", deity="Savitar (Sun God)",
        symbol="Open Hand/Fist", guna="Rajas", nature="Deva", element="Fire",
        personality="Skillful, clever, resourceful. The native is gifted with hands — craftsmanship, healing touch, and manual dexterity.",
        strengths=["Craftsmanship", "Resourcefulness", "Humour", "Healing hands"],
        challenges=["Cunning", "Restlessness", "Thievery tendency", "Unscrupulousness"],
        career_hints=["Crafts/handwork", "Surgery", "Magic/illusion", "Manufacturing"],
        health_areas=["Hands/fingers", "Intestines", "Nervous system"],
        spiritual_theme="Manifesting the divine through skilled hands — creation as worship.",
    ),
    "Chitra": NakshatraProfile(
        nakshatra="Chitra", ruling_planet="Mars", deity="Vishwakarma",
        symbol="Bright Jewel", guna="Tamas", nature="Rakshasa", element="Fire",
        personality="Creative, beautiful, architectural. The native is drawn to design, beauty, and creating lasting structures.",
        strengths=["Aesthetic sense", "Architectural mind", "Charisma", "Courage"],
        challenges=["Vanity", "Self-centredness", "Argumentative", "Romantic complications"],
        career_hints=["Architecture/design", "Jewellery", "Fashion", "Engineering"],
        health_areas=["Kidneys", "Lower abdomen", "Bladder"],
        spiritual_theme="The cosmic architect — building temples of consciousness.",
    ),
    "Swati": NakshatraProfile(
        nakshatra="Swati", ruling_planet="Rahu", deity="Vayu (Wind God)",
        symbol="Coral/Young Plant", guna="Tamas", nature="Deva", element="Fire",
        personality="Independent, flexible, diplomatic. The native values freedom, is adaptable, and excels in business and trade.",
        strengths=["Independence", "Diplomacy", "Business acumen", "Flexibility"],
        challenges=["Indecisiveness", "Restlessness", "Gossip", "Superficial relationships"],
        career_hints=["Business/trade", "Diplomacy", "Travel", "Wind/air industries"],
        health_areas=["Kidneys", "Skin", "Urinary system"],
        spiritual_theme="Detachment and freedom — the soul learning to move like the wind.",
    ),
    "Vishakha": NakshatraProfile(
        nakshatra="Vishakha", ruling_planet="Jupiter", deity="Indra-Agni",
        symbol="Triumphal Arch/Potter's Wheel", guna="Sattva", nature="Rakshasa", element="Fire",
        personality="Goal-oriented, intense, transformative. The native pursues objectives with single-minded determination.",
        strengths=["Determination", "Focus", "Leadership", "Transformative power"],
        challenges=["Obsessiveness", "Jealousy", "Ruthlessness", "Infidelity"],
        career_hints=["Politics", "Military", "Research", "Religious leadership"],
        health_areas=["Arms", "Lower abdomen", "Prostate/reproductive"],
        spiritual_theme="Spiritual fire — the intensity of purpose directed toward moksha.",
    ),
    "Anuradha": NakshatraProfile(
        nakshatra="Anuradha", ruling_planet="Saturn", deity="Mitra",
        symbol="Lotus", guna="Sattva", nature="Deva", element="Fire",
        personality="Devoted, friendly, resilient. The native blooms like a lotus in muddy waters — finding beauty and friendship in adversity.",
        strengths=["Devotion", "Friendship", "Resilience", "Organisational ability"],
        challenges=["Jealousy in love", "Wandering away from home", "Suppressed emotions", "Health fluctuations"],
        career_hints=["Organisations/groups", "International relations", "Occult", "Mining"],
        health_areas=["Hips", "Bladder", "Stomach"],
        spiritual_theme="Bhakti (devotion) — loving the divine through friendship and surrender.",
    ),
    "Jyeshtha": NakshatraProfile(
        nakshatra="Jyeshtha", ruling_planet="Mercury", deity="Indra",
        symbol="Earring/Umbrella", guna="Sattva", nature="Rakshasa", element="Air",
        personality="Eldest, protective, authoritative. The native takes on responsibility early, often becoming the protector or chief.",
        strengths=["Authority", "Protective instinct", "Intelligence", "Courage"],
        challenges=["Hypocrisy", "Jealousy", "Isolation", "Misuse of power"],
        career_hints=["Military/police", "Administration", "Occult", "Journalism"],
        health_areas=["Colon", "Reproductive organs", "Muscular system"],
        spiritual_theme="The burden of leadership — learning humility through power.",
    ),
    "Mula": NakshatraProfile(
        nakshatra="Mula", ruling_planet="Ketu", deity="Nirriti (Goddess of Destruction)",
        symbol="Bunch of Roots", guna="Tamas", nature="Rakshasa", element="Air",
        personality="Root-seeking, destructive-then-constructive, philosophical. The native digs deep to find truth, often destroying the superficial.",
        strengths=["Deep research", "Philosophical mind", "Fearlessness", "Transformative power"],
        challenges=["Destructiveness", "Arrogance", "Root-level upheavals", "Health concerns"],
        career_hints=["Research", "Philosophy", "Medicine (root cause)", "Astrology"],
        health_areas=["Hips/thighs", "Sciatic nerve", "Feet"],
        spiritual_theme="Going to the root of existence — liberation through radical truth-seeking.",
    ),
    "Purva Ashadha": NakshatraProfile(
        nakshatra="Purva Ashadha", ruling_planet="Venus", deity="Apas (Water Deity)",
        symbol="Fan/Winnowing Basket", guna="Rajas", nature="Manushya", element="Air",
        personality="Invincible, purifying, social. The native has an 'undefeated' quality — able to cleanse and rejuvenate situations.",
        strengths=["Invincibility", "Purification ability", "Persuasion", "Philosophical depth"],
        challenges=["Over-confidence", "Inflexibility", "Pride", "Confrontational"],
        career_hints=["Law", "Shipping/water industries", "Motivational speaking", "Purification technologies"],
        health_areas=["Thighs", "Hips", "Arterial system"],
        spiritual_theme="The invincible spirit — winning the inner battle through purity.",
    ),
    "Uttara Ashadha": NakshatraProfile(
        nakshatra="Uttara Ashadha", ruling_planet="Sun", deity="Vishvedevas",
        symbol="Elephant Tusk/Small Bed", guna="Rajas", nature="Manushya", element="Air",
        personality="Universal, righteous, victorious. The native achieves lasting victory through dharma and universal principles.",
        strengths=["Righteousness", "Leadership", "Universal vision", "Endurance"],
        challenges=["Loneliness at the top", "Rigidity", "Workaholism", "Harsh standards"],
        career_hints=["Government", "Law/justice", "Defence", "Pioneer in any field"],
        health_areas=["Thighs/knees", "Skin", "Bones"],
        spiritual_theme="Dharmic victory — the final conquest through righteous action.",
    ),
    "Shravana": NakshatraProfile(
        nakshatra="Shravana", ruling_planet="Moon", deity="Vishnu",
        symbol="Three Footprints/Ear", guna="Rajas", nature="Deva", element="Air",
        personality="Listening, learning, connecting. The native excels through listening, learning, and disseminating knowledge.",
        strengths=["Listening ability", "Knowledge", "Connectivity", "Travel"],
        challenges=["Gossip", "Over-sensitivity", "Slander", "Rigid opinions"],
        career_hints=["Media/communication", "Teaching", "Music", "Counselling"],
        health_areas=["Ears", "Knees", "Skin conditions"],
        spiritual_theme="Listening to the divine word (Shabda Brahman) — knowledge as liberation.",
    ),
    "Dhanishta": NakshatraProfile(
        nakshatra="Dhanishta", ruling_planet="Mars", deity="Vasus",
        symbol="Drum/Flute", guna="Tamas", nature="Rakshasa", element="Ether",
        personality="Wealthy, musical, ambitious. The native is drawn to music, rhythm, and the accumulation of material and spiritual wealth.",
        strengths=["Musical talent", "Wealth creation", "Ambition", "Adaptability"],
        challenges=["Marital issues", "Over-ambition", "Selfishness", "Argumentative"],
        career_hints=["Music/rhythm", "Real estate", "Scientific research", "Sports"],
        health_areas=["Ankles", "Blood circulation", "Joints"],
        spiritual_theme="The cosmic rhythm — finding God through music and vibration.",
    ),
    "Shatabhisha": NakshatraProfile(
        nakshatra="Shatabhisha", ruling_planet="Rahu", deity="Varuna",
        symbol="Empty Circle/1000 Flowers", guna="Tamas", nature="Rakshasa", element="Ether",
        personality="Healing, secretive, mystical. The native has deep healing ability but often works alone, carrying a veil of mystery.",
        strengths=["Healing power", "Research ability", "Independence", "Mystical insight"],
        challenges=["Loneliness", "Secretiveness", "Addictions", "Harsh speech"],
        career_hints=["Medicine/pharmacy", "Space technology", "Aquatic sciences", "Occult healing"],
        health_areas=["Calves/shins", "Ankles", "Heart (circulatory)"],
        spiritual_theme="The veiled healer — piercing the illusion to find cosmic truth.",
    ),
    "Purva Bhadrapada": NakshatraProfile(
        nakshatra="Purva Bhadrapada", ruling_planet="Jupiter", deity="Aja Ekapada",
        symbol="Two-faced Man/Sword", guna="Sattva", nature="Manushya", element="Ether",
        personality="Intense, transformative, dual-natured. The native oscillates between extremes — worldly and spiritual, gentle and fierce.",
        strengths=["Spiritual depth", "Transformative power", "Intellectual brilliance", "Penance ability"],
        challenges=["Dual nature", "Cynicism", "Dark moods", "Financial instability"],
        career_hints=["Astrology/occult", "Philosophy", "Mortuary/death-related", "Charity"],
        health_areas=["Ankles", "Feet", "Liver"],
        spiritual_theme="The funeral pyre — burning away the old self for spiritual rebirth.",
    ),
    "Uttara Bhadrapada": NakshatraProfile(
        nakshatra="Uttara Bhadrapada", ruling_planet="Saturn", deity="Ahir Budhnya (Serpent of the Depths)",
        symbol="Back legs of funeral cot/Twins", guna="Sattva", nature="Manushya", element="Ether",
        personality="Deep, compassionate, restrained. The native has tremendous control, depth of wisdom, and a connection to the kundalini depths.",
        strengths=["Depth of character", "Compassion", "Discipline", "Wisdom"],
        challenges=["Laziness", "Withdrawal", "Excessive control", "Hidden anger"],
        career_hints=["Counselling", "Non-profit/charity", "Yoga/meditation", "Deep-sea/underground work"],
        health_areas=["Feet", "Toes", "Sleep-related issues"],
        spiritual_theme="The depths of the cosmic ocean — stillness and surrender leading to moksha.",
    ),
    "Revati": NakshatraProfile(
        nakshatra="Revati", ruling_planet="Mercury", deity="Pushan",
        symbol="Drum/Fish", guna="Sattva", nature="Deva", element="Ether",
        personality="Nourishing, guiding, final. The last nakshatra — the native is a nurturer, guide, and facilitator of safe passage.",
        strengths=["Nurturing", "Creativity", "Intuition", "Safe guidance"],
        challenges=["Over-sensitivity", "Victim mentality", "Naivety", "Low physical stamina"],
        career_hints=["Orphanage/foster care", "Travel/pilgrimage", "Creative arts", "Animal care"],
        health_areas=["Feet/ankles", "Stomach", "Sleep disorders"],
        spiritual_theme="The final journey — guiding souls across the cosmic ocean to liberation.",
    ),
}


def get_nakshatra_profile(nakshatra: str) -> NakshatraProfile | None:
    return NAKSHATRA_PROFILES.get(nakshatra)


def nakshatra_prediction_summary(nakshatra: str) -> dict | None:
    profile = get_nakshatra_profile(nakshatra)
    if not profile:
        return None
    return {
        "nakshatra": profile.nakshatra,
        "ruling_planet": profile.ruling_planet,
        "deity": profile.deity,
        "symbol": profile.symbol,
        "guna": profile.guna,
        "nature": profile.nature,
        "element": profile.element,
        "personality": profile.personality,
        "strengths": profile.strengths,
        "challenges": profile.challenges,
        "career_hints": profile.career_hints,
        "health_areas": profile.health_areas,
        "spiritual_theme": profile.spiritual_theme,
    }
