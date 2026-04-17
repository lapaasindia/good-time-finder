"""
Synthesis Engine — The Core Narrative Constructor
Aggregates Parashari, Jaimini, Nadi, and KP scores to output a unified "Jury" prediction
for specific life domains.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class DomainSynthesis:
    domain_en: str
    domain_hi: str
    score: float  # Range -3.0 to +3.0
    summary_en: str
    summary_hi: str
    key_factors_en: list[str]
    key_factors_hi: list[str]

class SynthesisEngine:
    def __init__(
        self,
        planet_houses: dict[str, int],
        planet_signs: dict[str, str],
        lagna: str,
        shadbala: dict[str, float],
        drishti: tuple[dict[int, set[str]], dict[str, set[str]]],
        avasthas: dict[str, Any],
        nadi_links: dict[str, dict[str, list[str]]],
        chara_karakas: dict[str, str]
    ):
        self.planet_houses = planet_houses
        self.planet_signs = planet_signs
        self.lagna = lagna
        self.shadbala = shadbala
        self.house_aspects, self.planet_aspects = drishti
        self.avasthas = avasthas
        self.nadi_links = nadi_links
        self.chara_karakas = chara_karakas

    def _get_lord_of(self, house: int) -> str:
        from app.astrology.yogas import _lord_of_house
        return _lord_of_house(house, self.lagna, self.planet_signs)

    def synthesize_career(self) -> DomainSynthesis:
        """
        Analyzes the 10th house, 10th lord, Sun, Saturn, and Nadi career signatures.
        """
        score = 0.0
        factors_en = []
        factors_hi = []
        
        lord_10 = self._get_lord_of(10)
        
        # 1. Parashari Vote
        if lord_10:
            lord_str = self.shadbala.get(lord_10, 1.0)
            if lord_str >= 1.2:
                score += 1.0
                factors_en.append(f"Strong 10th Lord ({lord_10}) promises solid career foundation.")
                factors_hi.append(f"मजबूत दशमेश ({lord_10}) ठोस करियर की नींव का वादा करता है।")
            elif lord_str < 0.8:
                score -= 1.0
                factors_en.append(f"Weak 10th Lord ({lord_10}) indicates early career struggles.")
                factors_hi.append(f"कमजोर दशमेश ({lord_10}) प्रारंभिक करियर में संघर्ष का संकेत देता है।")

            # Check Avastha
            av = self.avasthas.get(lord_10)
            if av and av.score >= 0.5:
                score += 0.5
            elif av and av.score <= 0.2:
                score -= 0.5
                factors_en.append(f"10th Lord is in {av.state_en} Avastha, delaying full results.")
                factors_hi.append(f"दशमेश {av.state_hi} अवस्था में है, जिससे पूर्ण परिणामों में देरी हो रही है।")

        # Aspects on 10th House
        aspects_10 = self.house_aspects.get(10, set())
        if "Jupiter" in aspects_10:
            score += 1.0
            factors_en.append("Jupiter aspects 10th house: Grace and ethics in profession.")
            factors_hi.append("दशम भाव पर बृहस्पति की दृष्टि: पेशे में कृपा और नैतिकता।")
        if "Saturn" in aspects_10:
            factors_en.append("Saturn aspects 10th house: Hard work required, slow but steady rise.")
            factors_hi.append("दशम भाव पर शनि की दृष्टि: कड़ी मेहनत की आवश्यकता, धीमी लेकिन स्थिर प्रगति।")

        # 2. Nadi Vote
        from app.astrology.nadi import nadi_career_signature
        nadi_sigs = nadi_career_signature(self.nadi_links)
        for sig in nadi_sigs:
            factors_en.append(f"Nadi Linkage: {sig}")
            factors_hi.append(f"नाड़ी संबंध: शनि के साथ ग्रहों का प्रभाव विशेष करियर दिशा देता है।")
            score += 0.5

        # 3. Jaimini Vote
        amatyakaraka = None
        for p, k in self.chara_karakas.items():
            if k == "AmK":
                amatyakaraka = p
                break
        
        if amatyakaraka:
            ak_str = self.shadbala.get(amatyakaraka, 1.0)
            if ak_str >= 1.2:
                score += 1.0
                factors_en.append(f"Amatyakaraka ({amatyakaraka}) is very strong, indicating high status.")
                factors_hi.append(f"अमात्यकारक ({amatyakaraka}) बहुत मजबूत है, जो उच्च स्थिति का संकेत देता है।")

        # Final Narrative
        if score >= 2.0:
            summ_en = "Excellent career prospects. High likelihood of authoritative roles, public recognition, and steady growth."
            summ_hi = "करियर की उत्कृष्ट संभावनाएं। आधिकारिक भूमिकाओं, सार्वजनिक मान्यता और स्थिर विकास की उच्च संभावना।"
        elif score >= 0.0:
            summ_en = "Moderate career trajectory. Success comes through sustained effort and overcoming periodic obstacles."
            summ_hi = "मध्यम करियर ग्राफ। सफलता निरंतर प्रयास और समय-समय पर आने वाली बाधाओं को दूर करने से मिलती है।"
        else:
            summ_en = "Career may face significant turbulence or delays. Adaptation and patience are key."
            summ_hi = "करियर में महत्वपूर्ण उथल-पुथल या देरी का सामना करना पड़ सकता है। अनुकूलन और धैर्य कुंजी हैं।"

        return DomainSynthesis(
            domain_en="Career & Profession (Karma Bhava)",
            domain_hi="करियर और पेशा (कर्म भाव)",
            score=round(max(-3.0, min(3.0, score)), 2),
            summary_en=summ_en,
            summary_hi=summ_hi,
            key_factors_en=factors_en,
            key_factors_hi=factors_hi
        )

    def synthesize_wealth(self) -> DomainSynthesis:
        """
        Analyzes 2nd House, 11th House, Jupiter, Venus.
        """
        score = 0.0
        factors_en, factors_hi = [], []
        
        l2 = self._get_lord_of(2)
        l11 = self._get_lord_of(11)
        
        if l2 and self.shadbala.get(l2, 1.0) >= 1.1:
            score += 1.0
            factors_en.append("Strong 2nd Lord indicates good savings and family wealth.")
            factors_hi.append("मजबूत द्वितीयेश अच्छी बचत और पारिवारिक धन का संकेत देता है।")
            
        if l11 and self.shadbala.get(l11, 1.0) >= 1.1:
            score += 1.0
            factors_en.append("Strong 11th Lord indicates multiple income streams.")
            factors_hi.append("मजबूत एकादशेश आय के कई स्रोतों का संकेत देता है।")
            
        # Aspects on 2nd and 11th
        if "Jupiter" in self.house_aspects.get(2, set()) or "Jupiter" in self.house_aspects.get(11, set()):
            score += 1.0
            factors_en.append("Jupiter's aspect on wealth houses ensures financial protection.")
            factors_hi.append("धन भावों पर बृहस्पति की दृष्टि वित्तीय सुरक्षा सुनिश्चित करती है।")

        if score >= 1.5:
            summ_en = "Strong wealth-generating combinations. You have the capacity to build significant assets."
            summ_hi = "धन उत्पन्न करने वाले मजबूत योग। आप महत्वपूर्ण संपत्ति बनाने की क्षमता रखते हैं।"
        elif score >= 0.0:
            summ_en = "Stable financial prospects. Wealth accumulation will be gradual."
            summ_hi = "स्थिर वित्तीय संभावनाएं। धन संचय क्रमिक होगा।"
        else:
            summ_en = "Financial fluctuations indicated. Strict budgeting and avoiding risky investments is advised."
            summ_hi = "वित्तीय उतार-चढ़ाव का संकेत है। सख्त बजट बनाना और जोखिम भरे निवेश से बचना उचित है।"

        return DomainSynthesis(
            domain_en="Wealth & Finances (Dhana & Labha Bhava)",
            domain_hi="धन और वित्त (धन और लाभ भाव)",
            score=round(max(-3.0, min(3.0, score)), 2),
            summary_en=summ_en,
            summary_hi=summ_hi,
            key_factors_en=factors_en,
            key_factors_hi=factors_hi
        )
        
    def synthesize_marriage(self) -> DomainSynthesis:
        score = 0.0
        factors_en, factors_hi = [], []
        
        l7 = self._get_lord_of(7)
        if l7 and self.shadbala.get(l7, 1.0) >= 1.1:
            score += 1.0
            factors_en.append("Strong 7th Lord indicates a stable foundation for marriage.")
            factors_hi.append("मजबूत सप्तमेश विवाह के लिए एक स्थिर नींव का संकेत देता है।")
            
        if "Venus" in self.shadbala and self.shadbala["Venus"] >= 1.1:
            score += 0.5
            factors_en.append("Strong Venus (Karaka for romance) promotes harmony.")
            factors_hi.append("मजबूत शुक्र (रोमांस का कारक) सद्भाव को बढ़ावा देता है।")
            
        if "Jupiter" in self.house_aspects.get(7, set()):
            score += 1.0
            factors_en.append("Jupiter aspects the 7th house, offering protection to marriage.")
            factors_hi.append("सप्तम भाव पर बृहस्पति की दृष्टि, विवाह को सुरक्षा प्रदान करती है।")
            
        if "Saturn" in self.house_aspects.get(7, set()) or "Mars" in self.house_aspects.get(7, set()):
            score -= 1.0
            factors_en.append("Malefic aspects on the 7th house may cause delays or friction.")
            factors_hi.append("सप्तम भाव पर पापी ग्रहों की दृष्टि देरी या घर्षण का कारण बन सकती है।")
            
        if score >= 1.5:
            summ_en = "Excellent relationship prospects. Marriage will bring luck, stability, and mutual growth."
            summ_hi = "रिश्ते की उत्कृष्ट संभावनाएं। विवाह भाग्य, स्थिरता और पारस्परिक विकास लाएगा।"
        elif score >= 0.0:
            summ_en = "Average marital prospects. Requires understanding and adjustment to maintain harmony."
            summ_hi = "विवाह की औसत संभावनाएं। सद्भाव बनाए रखने के लिए समझ और समायोजन की आवश्यकता है।"
        else:
            summ_en = "Challenging relationship dynamics indicated. Patience and choosing the right partner carefully is advised."
            summ_hi = "चुनौतीपूर्ण संबंध गतिशीलता का संकेत। धैर्य और सही साथी को सावधानी से चुनना उचित है।"
            
        return DomainSynthesis(
            domain_en="Marriage & Relationships (Kalatra Bhava)",
            domain_hi="विवाह और रिश्ते (कलत्र भाव)",
            score=round(max(-3.0, min(3.0, score)), 2),
            summary_en=summ_en,
            summary_hi=summ_hi,
            key_factors_en=factors_en,
            key_factors_hi=factors_hi
        )

    def synthesize_health(self) -> DomainSynthesis:
        score = 0.0
        factors_en, factors_hi = [], []
        
        l1 = self._get_lord_of(1)
        l6 = self._get_lord_of(6)
        
        if l1 and self.shadbala.get(l1, 1.0) >= 1.1:
            score += 1.5
            factors_en.append("Strong Lagna Lord ensures robust physical vitality and immunity.")
            factors_hi.append("मजबूत लग्नेश मजबूत शारीरिक जीवन शक्ति और प्रतिरक्षा सुनिश्चित करता है।")
        else:
            score -= 0.5
            factors_en.append("Weak Lagna Lord suggests a need to prioritize health and immunity.")
            factors_hi.append("कमजोर लग्नेश स्वास्थ्य और प्रतिरक्षा को प्राथमिकता देने की आवश्यकता का सुझाव देता है।")
            
        if l6 and self.shadbala.get(l6, 1.0) >= 1.2:
            score -= 0.5
            factors_en.append("Strong 6th Lord can bring formidable diseases or obstacles.")
            factors_hi.append("मजबूत षष्ठेश दुर्जेय रोग या बाधाएं ला सकता है।")
            
        if score >= 1.0:
            summ_en = "Generally excellent health and strong recuperative powers."
            summ_hi = "आमतौर पर उत्कृष्ट स्वास्थ्य और मजबूत पुनप्राप्ति शक्तियां।"
        elif score >= 0.0:
            summ_en = "Moderate health. Prone to seasonal ailments but recovers well."
            summ_hi = "मध्यम स्वास्थ्य। मौसमी बीमारियों की संभावना लेकिन अच्छी तरह से ठीक हो जाते हैं।"
        else:
            summ_en = "Health requires constant care. Preventive measures and a good lifestyle are mandatory."
            summ_hi = "स्वास्थ्य को निरंतर देखभाल की आवश्यकता है। निवारक उपाय और अच्छी जीवनशैली अनिवार्य है।"
            
        return DomainSynthesis(
            domain_en="Health & Well-being (Tanu Bhava)",
            domain_hi="स्वास्थ्य और भलाई (तनु भाव)",
            score=round(max(-3.0, min(3.0, score)), 2),
            summary_en=summ_en,
            summary_hi=summ_hi,
            key_factors_en=factors_en,
            key_factors_hi=factors_hi
        )

    def run_all(self) -> list[DomainSynthesis]:
        return [
            self.synthesize_career(),
            self.synthesize_wealth(),
            self.synthesize_marriage(),
            self.synthesize_health()
        ]
