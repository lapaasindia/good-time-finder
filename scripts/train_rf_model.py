import json
import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score

def train():
    dataset_path = os.path.join(os.path.dirname(__file__), "optimization_dataset.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    feature_names = [
        "rule", "shadbala", "gochara", "dasha", "yoga", "ashtakavarga", "panchang", "tara", "chandra_bala", "avastha",
        "pushkara", "sudarshana", "jaimini", "arudha", "gulika", "badhaka", "bhrigu", "kp", "kp_cuspal", "double_transit",
        "gochara_house_specific", "planet_focus"
    ]

    X = []
    y = []

    for d in dataset:
        feats = d['features']
        expected = d['expected']
        if expected == "Good":
            y.append(1)
        elif expected == "Bad":
            y.append(0)
        else:
            continue
            
        row = [feats.get(fn, 0.0) for fn in feature_names]
        X.append(row)

    X = np.array(X, dtype=np.float64)
    y = np.array(y)

    print(f"Loaded {len(X)} samples with {X.shape[1]} features.")

    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X, y)
    
    preds = rf.predict(X)
    acc = accuracy_score(y, preds)
    print(f"Training Accuracy: {acc*100:.2f}%")
    
    cv_scores = cross_val_score(RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42), X, y, cv=5)
    print(f"Cross-Validation Accuracy: {np.mean(cv_scores)*100:.2f}%")

    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "rf_life_predictor.pkl")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(rf, f)
        
    print(f"Saved model to {model_path}")

if __name__ == "__main__":
    train()
