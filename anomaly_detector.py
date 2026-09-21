import json
from pathlib import Path

from telemetry import load_trace


POLICY_PATH = Path("policies.json")


def _load_policy():
    text = POLICY_PATH.read_text(
        encoding="utf-8"
    )

    policy = json.loads(text)

    return policy


def _has_explicit_write_intent(
    user_request,
    terms,
):
    text = user_request.lower()

    for term in terms:
        if term in text:
            return True

    return False


def analyze_trace(
    user_request,
    trace_path="traces/session.jsonl",
):
    policy = _load_policy()

    events = load_trace(trace_path)

    flags = []

    read_events = []

    for event in events:
        if event["action"] == "read":
            read_events.append(event)

    observed_reads = len(read_events)

    threshold = policy[
        "review_read_threshold"
    ]

    if observed_reads > threshold:
        flags.append(
            {
                "code": "EXCESSIVE_READS",
                "title": (
                    "Excessive customer "
                    "record access"
                ),
                "expected": f"<= {threshold}",
                "observed": observed_reads,
                "detail": (
                    f"Expected <= {threshold} "
                    "customer reads; "
                    f"observed {observed_reads}."
                ),
            }
        )

    update_events = []

    for event in events:
        if event["action"] == "update":
            update_events.append(event)

    write_intent = (
        _has_explicit_write_intent(
            user_request,
            policy["write_intent_terms"],
        )
    )

    if update_events and not write_intent:
        flags.append(
            {
                "code": (
                    "UNAUTHORIZED_WRITE_INTENT"
                ),
                "title": (
                    "Write action not clearly "
                    "authorized by user intent"
                ),
                "expected": (
                    "explicit update, modify, "
                    "change, edit, set, "
                    "or correct intent"
                ),
                "observed": (
                    f"{len(update_events)} "
                    "update action(s)"
                ),
                "detail": (
                    "The trace contains an "
                    "update action, but the "
                    "user's request did not "
                    "clearly request a change."
                ),
            }
        )

    delete_events = []

    for event in events:
        if event["action"] == "delete":
            delete_events.append(event)

    if (
        delete_events
        and not policy["delete_allowed"]
    ):
        flags.append(
            {
                "code": "DELETE_UNAVAILABLE",
                "title": (
                    "Delete action is not allowed"
                ),
                "expected": "0 delete actions",
                "observed": len(delete_events),
                "detail": (
                    "DELETE is unavailable "
                    "under the current policy."
                ),
            }
        )

    resources = set()

    for event in events:
        if event["resource"] != "customer_index":
            resources.add(
                event["resource"]
            )

    resources = sorted(resources)

    classification = (
        "REVIEW"
        if flags
        else "NORMAL"
    )

    return {
        "classification": classification,
        "total_actions": len(events),
        "read_count": observed_reads,
        "resources_accessed": resources,
        "flags": flags,
        "events": events,
    }