import json
import os
import random
from copy import deepcopy

# Load dataset
dataset_path = os.path.join(os.path.dirname(__file__), "optimization_dataset.json")
with open(dataset_path, "r") as f:
    dataset = json.load(f)

# Load actual base category weights
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.core.ranking import CATEGORY_WEIGHTS

def evaluate_weights(phase4_weights):
    correct = 0
    for d in dataset:
        cat = d['category']
        expected = d['expected']
        feats = d['features']
        
        cw = CATEGORY_WEIGHTS.get(cat, CATEGORY_WEIGHTS['general'])
        
        score = (
            feats['rule'] * cw.rule +
            feats['shadbala'] * cw.shadbala +
            feats['gochara'] * cw.gochara +
            feats['dasha'] * cw.dasha +
            feats['yoga'] * cw.yoga +
            feats['ashtakavarga'] * cw.ashtakavarga +
            
            feats['tara'] * phase4_weights['tara'] +
            feats['chandra_bala'] * phase4_weights['chandra_bala'] +
            feats['avastha'] * phase4_weights['avastha'] +
            feats['pushkara'] * phase4_weights['pushkara'] +
            feats['sudarshana'] * phase4_weights['sudarshana'] +
            feats['jaimini'] * phase4_weights['jaimini'] +
            feats['arudha'] * phase4_weights['arudha'] +
            feats['gulika'] * phase4_weights['gulika'] +
            feats['badhaka'] * phase4_weights['badhaka']
        )
        
        if expected == "Good" and score > 0.0:
            correct += 1
        elif expected == "Bad" and score < 0.0:
            correct += 1
            
    return correct / len(dataset)

baseline_weights = {
    "tara": 0.0, "chandra_bala": 0.0, "avastha": 0.0, "pushkara": 0.0,
    "sudarshana": 0.0, "jaimini": 0.0, "arudha": 0.0, "gulika": 0.0, "badhaka": 0.0
}
baseline_acc = evaluate_weights(baseline_weights)
print(f"Baseline Accuracy (Phase 4 Disabled): {baseline_acc*100:.2f}%")

best_weights = deepcopy(baseline_weights)
best_acc = baseline_acc
POPULATION = 100000

for i in range(POPULATION):
    test_weights = {}
    for k in best_weights.keys():
        # Allow small fine-tuning
        test_weights[k] = max(0.0, min(1.0, best_weights[k] + random.uniform(-0.1, 0.1)))
        
    acc = evaluate_weights(test_weights)
    
    if acc > best_acc:
        best_acc = acc
        best_weights = deepcopy(test_weights)

print(f"\nFinal Best Accuracy: {best_acc*100:.2f}% (Improved by {(best_acc - baseline_acc)*100:.2f}%)")
print("Optimal Weights for Phase 4 Modules:")
for k, v in best_weights.items():
    print(f"  {k}: {v:.3f}")
