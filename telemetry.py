import json
from datetime import datetime, timezone
from pathlib import Path


class EventLogger:
    def __init__(
        self,
        session_id,
        trace_path="traces/session.jsonl",
    ):
        self.session_id = session_id
        self.trace_path = Path(trace_path)

        self.trace_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def reset(self):
        self.trace_path.write_text(
            "",
            encoding="utf-8",
        )

    def log_tool(
        self,
        tool,
        resource,
        action,
        authorized,
        result,
        metadata=None,
    ):
        event = {
            "timestamp": (
                datetime
                .now(timezone.utc)
                .isoformat()
            ),
            "session_id": self.session_id,
            "tool": tool,
            "resource": resource,
            "action": action,
            "authorized": authorized,
            "result": result,
        }

        if metadata:
            event["metadata"] = metadata

        with self.trace_path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(event) + "\n"
            )

        return event


def load_trace(
    trace_path="traces/session.jsonl",
):
    path = Path(trace_path)

    if not path.exists():
        return []

    events = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if line:
                events.append(
                    json.loads(line)
                )

    return events