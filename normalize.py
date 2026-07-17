import json

def load_events(jsonl_path):
    with open(jsonl_path) as file:
        events = []
        for line in file:
            events.append(json.loads(line))
    return events
