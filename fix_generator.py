import re

with open('app/services/report_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix import issue
content = content.replace("from app.astrology.gochara import gochara_score", "from app.astrology.gochara import gochara_score, _house_from_sign")

with open('app/services/report_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
