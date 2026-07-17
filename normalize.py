import json

def load_events(jsonl_path):
    with open(jsonl_path) as file:
        events = []
        parsed_count = 0
        failed_count = 0
        for line in file:
            try:
                events.append(json.loads(line))
                parsed_count += 1
            except json.JSONDecodeError:
                failed_count += 1
        print("parsed: " + str(parsed_count) + ", failed: " + str(failed_count))
    return events

print(load_events("data/sample_events.jsonl"))