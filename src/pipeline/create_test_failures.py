
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "orders_test.csv"


def create_test_failures():
    with SOURCE_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        orders = list(reader)

    if len(orders) < 4:
        raise ValueError("At least four orders are required for this test.")

    # Failure 1: Duplicate an existing order ID
    orders[1]["order_id"] = orders[0]["order_id"]

    # Failure 2: Remove a required value
    orders[2]["product"] = ""

    # Failure 3: Make the order total incorrect
    orders[3]["total_amount"] = str(
        int(orders[3]["total_amount"]) + 100
    )

    # Failure 4: Use an unsupported payment status
    orders[4]["payment_status"] = "UNKNOWN"

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)

    print("Created a test dataset with deliberate data problems.")
    print(f"Test file: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_test_failures()
