import json

def load_events(jsonl_path):
    with open(jsonl_path) as file:
        events = []
        for event in file:
            events.append(json.loads(event))
    return events
