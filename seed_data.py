import json
from pathlib import Path


DATA_PATH = Path("synthetic_data/customers.json")


def build_customers():
    customers = []

    statuses = [
        "Active",
        "Active",
        "Active",
        "Review",
        "Active",
    ]

    plans = [
        "Starter",
        "Growth",
        "Enterprise",
    ]

    for customer_number in range(101, 151):
        annual_value = 12000 + (customer_number - 100) * 3750

        record = {
            "customer_id": f"customer_{customer_number}",
            "name": (
                "Sarah Chen"
                if customer_number == 104
                else f"Synthetic Customer {customer_number}"
            ),
            "company": (
                "Northstar Labs"
                if customer_number == 104
                else f"Demo Company {customer_number}"
            ),
            "account_status": statuses[
                (customer_number - 101) % len(statuses)
            ],
            "plan": plans[
                (customer_number - 101) % len(plans)
            ],
            "annual_value": annual_value,
            "risk_level": (
                "Medium"
                if customer_number % 4 == 0
                else "Low"
            ),
            "review_note": "",
        }

        customers.append(record)

    return customers


def reset_data():
    DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DATA_PATH.write_text(
        json.dumps(
            build_customers(),
            indent=2,
        ),
        encoding="utf-8",
    )

    return DATA_PATH


if __name__ == "__main__":
    path = reset_data()

    print(
        f"Created {path} with "
        f"{len(build_customers())} synthetic customers."
    )