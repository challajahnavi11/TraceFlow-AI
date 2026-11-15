
import csv
import random
from pathlib import Path

# Make the generated dataset reproducible
random.seed(42)

# Find the root directory of our project
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define where the raw data will be stored
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"


def generate_orders(number_of_orders=100):
    """Generate fictional e-commerce order records."""

    products = {
        "Laptop": 55000,
        "Headphones": 2500,
        "Keyboard": 1500,
        "Mouse": 800,
        "Monitor": 12000,
    }

    payment_statuses = ["PAID", "PENDING", "FAILED"]
    orders = []

    for order_number in range(1, number_of_orders + 1):
        product = random.choice(list(products.keys()))
        quantity = random.randint(1, 3)
        unit_price = products[product]

        order = {
            "order_id": f"ORD{order_number:04d}",
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": quantity * unit_price,
            "payment_status": random.choice(payment_statuses),
        }

        orders.append(order)

    return orders


def save_orders(orders):
    """Save the generated orders to a CSV file."""

    if not orders:
        raise ValueError("Cannot save an empty order dataset.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=orders[0].keys()
        )
        writer.writeheader()
        writer.writerows(orders)

    print(f"Generated {len(orders)} orders successfully!")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    orders = generate_orders()
    save_orders(orders)
