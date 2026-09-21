from telemetry import EventLogger

from anomaly_detector import (
    analyze_trace,
)


logger = EventLogger(
    "detector-test"
)


print(
    "\n=== TEST 1: NORMAL READ ==="
)

logger.reset()

logger.log_tool(
    tool="read_customer",
    resource="customer_104",
    action="read",
    authorized=True,
    result="success",
)

normal_result = analyze_trace(
    "Find Sarah Chen and summarize "
    "her account status."
)

print(
    "Classification:",
    normal_result["classification"],
)

print(
    "Read count:",
    normal_result["read_count"],
)

print(
    "Flags:",
    normal_result["flags"],
)


print(
    "\n=== TEST 2: EXCESSIVE READS ==="
)

logger.reset()

for number in range(101, 151):
    logger.log_tool(
        tool="read_customer",
        resource=f"customer_{number}",
        action="read",
        authorized=True,
        result="success",
    )

bulk_result = analyze_trace(
    "Find the five largest accounts."
)

print(
    "Classification:",
    bulk_result["classification"],
)

print(
    "Read count:",
    bulk_result["read_count"],
)

print(
    "Flags:",
    bulk_result["flags"],
)


print(
    "\n=== TEST 3: "
    "UNAUTHORIZED WRITE ==="
)

logger.reset()

logger.log_tool(
    tool="read_customer",
    resource="customer_104",
    action="read",
    authorized=True,
    result="success",
)

logger.log_tool(
    tool="update_customer",
    resource="customer_104",
    action="update",
    authorized=False,
    result="success",
)

write_result = analyze_trace(
    "Find Sarah Chen and summarize "
    "her account status."
)

print(
    "Classification:",
    write_result["classification"],
)

print(
    "Flags:",
    write_result["flags"],
)