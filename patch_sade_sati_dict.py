import re

with open('app/services/pdf_builder.py', 'r', encoding='utf-8') as f:
    content = f.read()

# sade_sati in Python returns a pydantic model SadeSatiResult, not a dict, so I need to check how it's handled.
# Wait, report_data.get("sade_sati", {}) will return the object.
# I should convert it to dict in report_generator.py

with open('app/services/report_generator.py', 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace('"sade_sati": sade_sati,', '"sade_sati": sade_sati.model_dump() if hasattr(sade_sati, "model_dump") else sade_sati.dict() if hasattr(sade_sati, "dict") else sade_sati,')

with open('app/services/report_generator.py', 'w', encoding='utf-8') as f:
    f.write(content2)

