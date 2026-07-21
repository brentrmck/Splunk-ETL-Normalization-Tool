import json

alias_table = {"ts":"timestamp",
"ts_ms":"timestamp",
"time":"timestamp",
"severity":"log_level",
"level":"log_level",
"app":"service",
"source":"service",
"msg":"message",
"userid":"user_id"
}

normalized_field_names = [
    "timestamp",
    "log_level",
    "service",
    "message",
    "user_id"
]

def load_events(jsonl_path):
    with open(jsonl_path) as file:
        events = []
        parsed_count, failed_count = 0, 0
        for line_number, line in enumerate(file, start=1):
            try:
                events.append(json.loads(line))
                parsed_count += 1
            except json.JSONDecodeError as e:
                failed_count += 1
                print(f"Exception on line {line_number}: {e}")
        print(f"parsed: {parsed_count} failed: {failed_count}")
    return events

def normalize_event(raw_event):
    normalized_event = {}
    normalized_event["extras"] = {}
    for key in raw_event:
        pass
        # if alias required:
        #    update to alias
        # elif already good:
        #    add directly
        # else:
        #    add to extras{} bag
    return normalized_event

#print(load_events("data/sample_events.jsonl"))

