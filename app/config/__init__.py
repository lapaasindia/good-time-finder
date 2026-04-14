from __future__ import annotations

from pathlib import Path

import yaml

from app.core.enums import EventNature, EventTag
from app.core.models import EventDefinition

_CONFIG_PATH = Path(__file__).parent / "events.yaml"


def load_event_catalog() -> list[EventDefinition]:
    with _CONFIG_PATH.open() as f:
        raw = yaml.safe_load(f)

    events = []
    for item in raw:
        tags = [EventTag(t) for t in item.get("tags", [])]
        events.append(
            EventDefinition(
                name=item["name"],
                nature=EventNature(item["nature"]),
                description=item["description"].strip(),
                tags=tags,
                rule_key=item["rule_key"],
            )
        )
    return events
