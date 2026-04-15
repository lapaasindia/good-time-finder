import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from app.core.models import Person, GeoLocation, TimeRange
from app.services.life_predictor import LifePredictorService
from scripts.backtest_personalities import PERSONALITIES
import app.services.life_predictor as lp

# Monkey patch compute_composite_score in life_predictor module
global_features = []

original_compute = lp.compute_composite_score

def mocked_compute(category, rule_score, shadbala_bonus=0, gochara_score=0, dasha_bonus=0, yoga_score=0, ashtakavarga_bonus=0, tara_score=0, chandra_bala_score=0, avastha_score=0, pushkara_bonus_score=0, sudarshana_score=0, jaimini_score=0, arudha_score=0, gulika_penalty=0, badhaka_penalty=0, bhrigu_bonus=0, kp_score=0):
    feats = {
        "rule": rule_score,
        "shadbala": shadbala_bonus,
        "gochara": gochara_score,
        "dasha": dasha_bonus,
        "yoga": yoga_score,
        "ashtakavarga": ashtakavarga_bonus,
        "tara": tara_score,
        "chandra_bala": chandra_bala_score,
        "avastha": avastha_score,
        "pushkara": pushkara_bonus_score,
        "sudarshana": sudarshana_score,
        "jaimini": jaimini_score,
        "arudha": arudha_score,
        "gulika": gulika_penalty,
        "badhaka": badhaka_penalty,
        "bhrigu": bhrigu_bonus,
        "kp": kp_score
    }
    global_features.append(feats)
    return original_compute(category, rule_score, shadbala_bonus, gochara_score, dasha_bonus, yoga_score, ashtakavarga_bonus, tara_score, chandra_bala_score, avastha_score, pushkara_bonus_score, sudarshana_score, jaimini_score, arudha_score, gulika_penalty, badhaka_penalty, bhrigu_bonus, kp_score)

lp.compute_composite_score = mocked_compute

def run():
    service = LifePredictorService()
    dataset = []
    
    for p_data in PERSONALITIES:
        b_dt = datetime.strptime(p_data['birth']['dt'], "%Y-%m-%d %H:%M")
        person = Person(
            name=p_data['name'],
            birth_datetime=b_dt,
            birth_location=GeoLocation(
                latitude=p_data['birth']['lat'],
                longitude=p_data['birth']['lon'],
                timezone=p_data['birth']['tz']
            )
        )
        
        for event in p_data['events']:
            if not event.get('nature'): continue
            if event['nature'] == 'Neutral': continue  # Skip neutral for optimizer
            
            e_dt = datetime.strptime(event['date'], "%Y-%m-%d")
            time_range = TimeRange(
                start=e_dt - timedelta(days=3),
                end=e_dt + timedelta(days=3)
            )
            
            desc_lower = event['desc'].lower()
            if any(w in desc_lower for w in ['passed away', 'died', 'death', 'killed', 'suicide', 'assassin', 'illness', 'cancer', 'health', 'hospital', 'lung', 'deaf', 'injured', 'injury', 'crash', 'disappear', 'radiation', 'als', 'hiv', 'cocaine', 'drug', 'asylum', 'ear', 'helicopter']):
                category = 'health'
            elif any(w in desc_lower for w in ['married', 'marriage', 'wedding', 'divorce', 'separation', 'wife', 'husband', 'muse', 'megxit']):
                category = 'marriage'
            elif any(w in desc_lower for w in ['sentenced', 'imprisonment', 'testimony', 'trial', 'arrested', 'case', 'convicted', 'prison', 'guillotine', 'executed']):
                category = 'legal'
            elif any(w in desc_lower for w in ['founded', 'ipo', 'ceo', 'chairman', 'president', 'pm', 'elected', 'election', 'chancellor', 'pope', 'governor', 'inaugur', 'business', 'company', 'promoted', 'appointed', 'patent', 'contract', 'resigned', 'fired', 'stepped down', 'took over', 'launched', 'pivot', 'joined', 'became', 'role', 'term', 'left', 'terminated', 'dismissal', 'dismissed', 'retired', 'retirement', 'defected', 'captain', 'red card', 'lost election', 'decision']):
                category = 'career'
            elif any(w in desc_lower for w in ['nobel', 'oscar', 'award', 'prize', 'knighted', 'gold medal', 'champion', 'title', 'record', 'win', 'won', 'premiere', 'release', 'published', 'completed', 'symphony', 'world cup', 'olympics', 'hall of fame', 'comeback']):
                category = 'career'
            elif any(w in desc_lower for w in ['bankrupt', 'financial', 'crisis', 'crash', 'money', 'wealth', 'fortune', 'trading', 'investment', 'lehman']):
                category = 'finance'
            else:
                category = 'general'
            
            global_features.clear()
            service.predict(person, person.birth_location, time_range, category)
            
            if global_features:
                avg_feats = {}
                for k in global_features[0].keys():
                    avg_feats[k] = sum(f[k] for f in global_features) / len(global_features)
                
                dataset.append({
                    "name": p_data['name'],
                    "event": event['desc'],
                    "expected": event['nature'],
                    "category": category,
                    "features": avg_feats
                })

    with open(os.path.join(os.path.dirname(__file__), "optimization_dataset.json"), "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Extracted features for {len(dataset)} events.")

if __name__ == "__main__":
    run()
