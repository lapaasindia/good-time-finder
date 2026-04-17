import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from app.core.models import Person, GeoLocation, TimeRange
from app.services.life_predictor import LifePredictorService
from scripts.backtest_personalities import PERSONALITIES
import app.core.ranking as ranking
import app.services.life_predictor as lp

# Monkey patch batch_composite_scores in both namespaces
global_features = []

original_compute = ranking.batch_composite_scores

def mocked_compute(category, feature_rows):
    feature_names = [
        "rule", "shadbala", "gochara", "dasha", "yoga", "ashtakavarga", "panchang", "tara", "chandra_bala", "avastha",
        "pushkara", "sudarshana", "jaimini", "arudha", "gulika", "badhaka", "bhrigu", "kp", "kp_cuspal", "double_transit",
        "gochara_house_specific", "planet_focus"
    ]
    for row in feature_rows:
        feats = dict(zip(feature_names, row))
        global_features.append(feats)
    return original_compute(category, feature_rows)

ranking.batch_composite_scores = mocked_compute
lp.batch_composite_scores = mocked_compute
lp.USE_ML_MODEL = False
ranking.USE_ML_MODEL = False

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
            
            
            print(f"Processing event: {p_data['name']} - {event['desc']} (Category: {category})")
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
