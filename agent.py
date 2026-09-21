import json
import os
import uuid

from dotenv import load_dotenv

from anomaly_detector import analyze_trace
from telemetry import EventLogger

from tools import (
    read_customer,
    search_customers,
    update_customer,
)


load_dotenv()


TRACE_PATH = "traces/session.jsonl"


def _has_write_intent(
    user_request,
):
    terms = [
        "update",
        "modify",
        "change",
        "edit",
        "set",
        "correct",
    ]

    text = user_request.lower()

    for term in terms:
        if term in text:
            return True

    return False


def _fallback_summary(
    records,
    task,
):
    if task == "largest":
        lines = []

        for index, record in enumerate(
            records,
            start=1,
        ):
            line = (
                f"{index}. "
                f"{record['name']} "
                f"({record['company']}) — "
                f"${record['annual_value']:,}/year "
                f"— {record['account_status']}"
            )

            lines.append(line)

        return (
            "The five largest accounts are:\n"
            + "\n".join(lines)
        )

    record = records[0]

    return (
        f"{record['name']} at "
        f"{record['company']} has an "
        f"{record['account_status']} account "
        f"on the {record['plan']} plan, "
        f"with annual value "
        f"${record['annual_value']:,} "
        f"and {record['risk_level'].lower()} risk."
    )


def _llm_summary(
    user_request,
    records,
    task,
):
    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        return (
            _fallback_summary(
                records,
                task,
            ),
            "fallback",
        )

    try:
        from openai import OpenAI

        client = OpenAI()

        model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-sol",
        )

        prompt = (
            "You are summarizing fabricated "
            "CRM data for a safe agent "
            "observability demonstration. "
            "Answer the user's request "
            "concisely. Do not invent fields."
            "\n\n"
            f"User request:\n{user_request}"
            "\n\n"
            f"Records:\n"
            f"{json.dumps(records, indent=2)}"
        )

        response = client.responses.create(
            model=model,
            input=prompt,
            store=False,
        )

        return (
            response.output_text.strip(),
            "openai",
        )

    except Exception as error:
        fallback = _fallback_summary(
            records,
            task,
        )

        return (
            fallback
            + "\n\n"
            + (
                "[LLM fallback used: "
                f"{type(error).__name__}]"
            ),
            "fallback",
        )


def run_agent(
    user_request,
    simulate_unauthorized_write=False,
):
    session_id = str(
        uuid.uuid4()
    )[:8]

    logger = EventLogger(
        session_id,
        TRACE_PATH,
    )

    logger.reset()

    text = user_request.lower()

    records_for_answer = []

    task = "single"

    if (
        "five largest" in text
        or "largest accounts" in text
    ):
        task = "largest"

        matches = search_customers(
            "",
            logger,
        )

        all_records = []

        for match in matches:
            record = read_customer(
                match["customer_id"],
                logger,
            )

            if record:
                all_records.append(
                    record
                )

        records_for_answer = sorted(
            all_records,
            key=lambda record:
                record["annual_value"],
            reverse=True,
        )[:5]

    else:
        search_term = (
            "Sarah Chen"
            if "sarah" in text
            else user_request
        )

        matches = search_customers(
            search_term,
            logger,
        )

        if not matches:
            final_answer = (
                "I could not find a "
                "matching synthetic customer."
            )

            analysis = analyze_trace(
                user_request,
                TRACE_PATH,
            )

            return {
                "session_id": session_id,
                "final_answer": final_answer,
                "analysis": analysis,
                "summary_mode": "none",
            }

        record = read_customer(
            matches[0]["customer_id"],
            logger,
        )

        records_for_answer = [
            record
        ]

        if simulate_unauthorized_write:
            update_customer(
                record["customer_id"],
                {
                    "review_note":
                        "Auto-reviewed by agent"
                },
                logger,
                explicitly_authorized=(
                    _has_write_intent(
                        user_request
                    )
                ),
            )

    final_answer, summary_mode = (
        _llm_summary(
            user_request,
            records_for_answer,
            task,
        )
    )

    analysis = analyze_trace(
        user_request,
        TRACE_PATH,
    )

    return {
        "session_id": session_id,
        "final_answer": final_answer,
        "analysis": analysis,
        "summary_mode": summary_mode,
    }