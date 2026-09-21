from seed_data import reset_data

from telemetry import (
    EventLogger,
    load_trace,
)

from tools import (
    search_customers,
    read_customer,
    update_customer,
)


reset_data()


logger = EventLogger(
    "tools-test"
)

logger.reset()


print("\n--- SEARCH TEST ---")

matches = search_customers(
    "Sarah Chen",
    logger,
)

print(matches)


print("\n--- READ TEST ---")

customer = read_customer(
    "customer_104",
    logger,
)

print(customer)


print("\n--- UPDATE TEST ---")

updated_customer = update_customer(
    "customer_104",
    {
        "review_note": "Test note"
    },
    logger,
    explicitly_authorized=True,
)

print(
    updated_customer["review_note"]
)


print("\n--- TRACE TEST ---")

events = load_trace()

print(
    f"Total recorded events: {len(events)}"
)

for event in events:
    print(
        event["tool"],
        "->",
        event["resource"],
        "->",
        event["result"],
    )


reset_data()

print(
    "\nSynthetic data reset after test."
)