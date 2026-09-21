import json
from pathlib import Path


DATA_PATH = Path("synthetic_data/customers.json")


def _load_customers():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Synthetic customer data is missing. "
            "Run: python seed_data.py"
        )

    text = DATA_PATH.read_text(
        encoding="utf-8"
    )

    customers = json.loads(text)

    return customers


def _save_customers(customers):
    DATA_PATH.write_text(
        json.dumps(
            customers,
            indent=2,
        ),
        encoding="utf-8",
    )


def search_customers(
    query,
    logger,
):
    customers = _load_customers()

    normalized_query = query.lower().strip()

    matches = []

    for customer in customers:
        searchable_text = (
            f"{customer['customer_id']} "
            f"{customer['name']} "
            f"{customer['company']}"
        ).lower()

        if normalized_query in searchable_text:
            matches.append(customer)

    logger.log_tool(
        tool="search_customers",
        resource="customer_index",
        action="search",
        authorized=True,
        result="success",
        metadata={
            "query": query,
            "matches": len(matches),
        },
    )

    results = []

    for customer in matches:
        results.append(
            {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
                "company": customer["company"],
            }
        )

    return results


def read_customer(
    customer_id,
    logger,
):
    customers = _load_customers()

    for customer in customers:
        if customer["customer_id"] == customer_id:

            logger.log_tool(
                tool="read_customer",
                resource=customer_id,
                action="read",
                authorized=True,
                result="success",
            )

            return customer

    logger.log_tool(
        tool="read_customer",
        resource=customer_id,
        action="read",
        authorized=True,
        result="not_found",
    )

    return None


def update_customer(
    customer_id,
    updates,
    logger,
    explicitly_authorized,
):
    customers = _load_customers()

    for customer in customers:
        if customer["customer_id"] == customer_id:

            customer.update(updates)

            _save_customers(customers)

            logger.log_tool(
                tool="update_customer",
                resource=customer_id,
                action="update",
                authorized=explicitly_authorized,
                result="success",
                metadata={
                    "fields": list(updates.keys())
                },
            )

            return customer

    logger.log_tool(
        tool="update_customer",
        resource=customer_id,
        action="update",
        authorized=explicitly_authorized,
        result="not_found",
        metadata={
            "fields": list(updates.keys())
        },
    )

    return None