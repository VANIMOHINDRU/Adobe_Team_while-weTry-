import json

def parse_persona(path):
    with open(path, 'r', encoding='utf-8') as f:
        persona = json.load(f)

    return {
        "role": persona.get("role", "Unknown Role"),
        "specialization": persona.get("specialization", ""),
        "focus_areas": persona.get("focus_areas", [])
    }
