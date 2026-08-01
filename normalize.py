import json
from datetime import datetime, timezone

alias_table = {
    "ts":"timestamp",
    "ts_ms":"timestamp",
    "time":"timestamp",
    "severity":"log_level",
    "level":"log_level",
    "app":"service",
    "source":"service",
    "msg":"message",
    "userid":"user_id"
}

required_field_names = [
    "timestamp",
    "log_level",
    "service",
    "message"
]

normalized_field_names = [
    "timestamp",
    "log_level",
    "service",
    "message",
    "user_id"
]

normalized_level_values = [
    "ERROR",
    "WARN",
    "INFO",
    "DEBUG"
]

timestamp_formats = [
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
]

output_timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"

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
    normalized_event = {"extras":{}}
    for key, value in raw_event.items():
        if key in alias_table:
            normalized_event[alias_table[key]] = value
        elif key in normalized_field_names:
            normalized_event[key] = value
        else:
            normalized_event["extras"][key] = value
    normalized_event_ordered = {}
    for field in normalized_field_names:
        if field in normalized_event:
            normalized_event_ordered[field] = normalized_event[field]
    normalized_event_ordered["extras"] = normalized_event["extras"]
    if "log_level" in normalized_event_ordered:
        normalized_event_ordered["log_level"] = str(normalized_event_ordered["log_level"]).upper()
    if "timestamp" in normalized_event_ordered:
        normalized_event_ordered["timestamp"] = normalize_timestamp(normalized_event_ordered["timestamp"])
    return normalized_event_ordered

def normalize_timestamp(timestamp):
    parsed_timestamp = None
    if isinstance(timestamp, (int, float)):
        seconds = int(timestamp) / 1000
        parsed_timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
    else:
        for ts_format in timestamp_formats:
            try:
                parsed_timestamp = datetime.strptime(timestamp, ts_format)
                break
            except ValueError:
                pass
    if parsed_timestamp is None:
        return timestamp
    formatted_timestamp = parsed_timestamp.strftime(output_timestamp_format)
    formatted_timestamp = formatted_timestamp[:-4] + "Z"
    return formatted_timestamp

def dedupe_events(normalized_events):
    seen_fingerprints = set()
    deduped_events = []
    duplicate_count = 0

    for event in normalized_events:
        fingerprint = json.dumps(event, sort_keys=True)
        if fingerprint not in seen_fingerprints:
            seen_fingerprints.add(fingerprint)
            deduped_events.append(event)
        else:
            duplicate_count += 1
    print(f"duplicates removed: {duplicate_count}")
    return deduped_events

def validate_events(normalized_event):
    validation_errors = []
    for field in required_field_names:
        if field not in normalized_event:
            validation_errors.append(f'Missing required field: {field}')
    return normalized_event

if __name__ == "__main__":
    normalized_events = []
    deduped_events = []
    for raw in load_events("data/sample_events.jsonl"):
        normalized_events.append(normalize_event(raw))
    deduped_events = dedupe_events(normalized_events)
    for event in deduped_events:
        validate_events(event)
        print(event)
