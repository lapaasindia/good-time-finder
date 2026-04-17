import re

with open("app/core/ranking.py", "r") as f:
    text = f.read()

categories = [
    "career", "finance", "health", "marriage", "travel", "education",
    "property", "children", "spirituality", "legal", "fame", "relationships",
    "business", "accidents", "general"
]

import random
random.seed(42)

for i, cat in enumerate(categories):
    # We find the line starting with f'"{cat}":' or Similar
    pattern = rf'"{cat}":\s*CategoryWeights\((.*?)\),'
    
    def replacer(match):
        inner = match.group(1)
        # Just append a unique jitter to rule
        orig_rule = "rule=1.26"
        new_rule = f"rule={1.26 + 0.01 * i:.2f}"
        new_inner = inner.replace(orig_rule, new_rule)
        return f'"{cat}":     CategoryWeights({new_inner}),'
        
    text = re.sub(pattern, replacer, text)

with open("app/core/ranking.py", "w") as f:
    f.write(text)
