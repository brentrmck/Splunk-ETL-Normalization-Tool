# Splunk ETL Normalization Tool

A Python batch utility that takes messy JSON objects from different sources and
turns them into clean, deduplicated, JSON log entries.

## The problem

Log data from 40+ sources (legacy systems, cloud APIs, databases, third-party
vendors) lands in a staging area before being sent to Splunk. Every source
has its own conventions: field names vary (`level` vs `severity`, `service` vs `app`),
timestamps arrive in different formats, events may be duplicated across
sources, and some lines are outright malformed. Cleaning this up by hand before
ingestion is slow and error-prone, this tool automates the process.

## What it does

A five-stage pipeline: **load → normalize → deduplicate → validate → emit**

- Parses JSON object input and survives bad data. Malformed lines are counted
  and reported with line numbers.
- Required fields:
  - timestamp
  - log_level
  - service
  - message
- Optional fields:
  - user_id
  - extras
- Maps field aliases onto one schema (`ts`/`ts_ms`/`time` → `timestamp`,
  `severity`/`level` → `log_level`, `app`/`source` → `service`, `msg` → `message`, `userid` → `user_id`)
- Normalizes timestamps to ISO 8601 UTC, whether they arrive as ISO strings,
  US-style dates, or epoch milliseconds (timestamps without a timezone are
  assumed UTC)
- Normalizes log_level to `ERROR` / `WARN` / `INFO` / `DEBUG`
- Deduplicates events that describe the same occurrence, even when the two
  copies use different field names and timestamp formats
- Never throws data away: fields that don't map to the schema are preserved
  under 'extras' rather than at the top level of the event, they are not dropped
- Writes clean JSON Lines to `output/`, ready for Splunk (or anything else)
  to ingest

## Example

Two incoming events that are actually the same occurrence, in two different shapes:

 **Input JSON Objects:** 

{"timestamp": "2024-01-15T14:23:45Z", "level": "ERROR", "service": "auth-api", "message": "User login failed", "user_id": 12345, "region": "us-east-1"}

{"ts": "01/15/2024 14:23:45", "severity": "error", "source": "auth-api", "msg": "User login failed", "userid": 12345, "region": "us-east-1"}

**Output Normalized Event:**

{"timestamp": "2024-01-15T14:23:45Z", "log_level": "ERROR", "service": "auth-api", "message": "User login failed", "user_id": 12345, 'extras': {'region': 'us-east-1'}}

## Design principles
- Correctness over speed. 
- Daily batch runs of 50K–200K events with a 5m budget
- Failures are visible. Bad lines are reported, counted, and summarized so that nothing fails silently.
- Unrecognized fields are still passed through instead of being discarded.
- Tool-agnostic output. Built with Splunk in mind, yet outputs plain JSON Lines that any consumer can read.

## Status
Fault-tolerant JSONL loader with parse/failure reporting - **Complete**

Field name normalization - **Complete**

JSON Order structure (timestamp first ... extras last) - **Complete**

Level value normalization - **Complete**

Timestamp value normalization - **In Progress**

Deduplication

Validation and run summary

Output writer
