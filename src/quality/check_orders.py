
import csv
import json
import argparse
import uuid

from pathlib import Path
from datetime import datetime, timezone


# Find project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Store historical incident reports
REPORT_DIR = PROJECT_ROOT / "reports" / "incidents"

# Required CSV columns
REQUIRED_FIELDS = [
    "order_id",
    "product",
    "quantity",
    "unit_price",
    "total_amount",
    "payment_status",
]

NUMERIC_FIELDS = ["quantity", "unit_price", "total_amount"]

VALID_STATUSES = {"PAID", "PENDING", "FAILED"}


def check_orders(input_file):
    """Validate orders and generate detailed incident reports."""

    # 1. Check whether input file exists
    if not input_file.exists():
        raise FileNotFoundError(
            f"Order data not found: {input_file}"
        )

    # 2. Read CSV data
    with input_file.open(
        "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames or any(
            field not in reader.fieldnames
            for field in REQUIRED_FIELDS
        ):
            raise ValueError(
                "CSV is missing one or more required columns."
            )

        orders = list(reader)

    incidents = []

    # 3. Helper function to record incidents
    def add_incident(
        category,
        severity,
        order_id,
        row_number,
        message,
        row_numbers=None,
        affected_field=None,
        expected_value=None,
        actual_value=None,
        suggested_resolution=None
    ):
        incidents.append({
            "incident_id": str(uuid.uuid4()),
            "category": category,
            "severity": severity,
            "order_id": order_id,
            "row_number": row_number,
            "row_numbers": row_numbers,
            "affected_field": affected_field,
            "expected_value": expected_value,
            "actual_value": actual_value,
            "suggested_resolution": suggested_resolution,
            "message": message,
        })

    # --------------------------------------------------
    # 4. Detect duplicate order IDs
    # --------------------------------------------------

    id_rows = {}

    for line_number, row in enumerate(orders, start=2):

        order_id = row["order_id"].strip()

        if order_id:
            if order_id not in id_rows:
                id_rows[order_id] = []

            id_rows[order_id].append(line_number)

    for order_id, row_numbers in id_rows.items():

        if len(row_numbers) > 1:

            add_incident(
                category="DUPLICATE_ORDER_ID",
                severity="HIGH",
                order_id=order_id,
                row_number=None,
                row_numbers=row_numbers,
                affected_field="order_id",
                expected_value="Unique order ID",
                actual_value=order_id,
                suggested_resolution=(
                    "Investigate all affected rows and determine "
                    "whether duplicate records should be removed "
                    "or assigned unique order IDs."
                ),
                message=(
                    f"Order ID appears {len(row_numbers)} times "
                    f"in rows {', '.join(map(str, row_numbers))}."
                )
            )

    # --------------------------------------------------
    # 5. Validate individual records
    # --------------------------------------------------

    for line_number, order in enumerate(orders, start=2):

        order_id = order["order_id"].strip() or "UNKNOWN"

        # Check missing values
        missing_fields = []

        for field in REQUIRED_FIELDS:

            if not order[field].strip():

                missing_fields.append(field)

                add_incident(
                    category="MISSING_VALUE",
                    severity="MEDIUM",
                    order_id=order_id,
                    row_number=line_number,
                    affected_field=field,
                    actual_value=order[field],
                    suggested_resolution=(
                        f"Investigate the missing {field} value "
                        "and obtain the correct value from "
                        "the source system."
                    ),
                    message=f"Missing value in {field}."
                )

        # Check numeric values
        numeric_values = {}
        invalid_numeric_fields = []

        for field in NUMERIC_FIELDS:

            raw_value = order[field].strip()

            # Empty values are already reported as missing
            if not raw_value:
                continue

            try:
                numeric_values[field] = int(raw_value)

            except ValueError:
                invalid_numeric_fields.append(field)

                add_incident(
                    category="INVALID_NUMERIC_VALUE",
                    severity="HIGH",
                    order_id=order_id,
                    row_number=line_number,
                    affected_field=field,
                    expected_value="Valid integer",
                    actual_value=raw_value,
                    suggested_resolution=(
                        f"Check the {field} value and replace "
                        "it with a valid integer."
                    ),
                    message=(
                        f"Invalid numeric value in {field}: "
                        f"{raw_value}."
                    )
                )

        # Skip calculations if required numeric values
        # are missing or invalid
        if missing_fields or invalid_numeric_fields:
            continue

        quantity = numeric_values["quantity"]
        unit_price = numeric_values["unit_price"]
        total_amount = numeric_values["total_amount"]

        # Check quantity
        if quantity <= 0:

            add_incident(
                category="INVALID_QUANTITY",
                severity="HIGH",
                order_id=order_id,
                row_number=line_number,
                affected_field="quantity",
                expected_value="Greater than 0",
                actual_value=quantity,
                suggested_resolution=(
                    "Verify the order quantity in the source data."
                ),
                message="Quantity must be positive."
            )

        # Check unit price
        if unit_price < 0:

            add_incident(
                category="INVALID_UNIT_PRICE",
                severity="HIGH",
                order_id=order_id,
                row_number=line_number,
                affected_field="unit_price",
                expected_value="Greater than or equal to 0",
                actual_value=unit_price,
                suggested_resolution=(
                    "Verify the product price against "
                    "the source pricing data."
                ),
                message="Unit price cannot be negative."
            )

        # Check total amount
        expected_total = quantity * unit_price

        if total_amount != expected_total:

            add_incident(
                category="TOTAL_MISMATCH",
                severity="HIGH",
                order_id=order_id,
                row_number=line_number,
                affected_field="total_amount",
                expected_value=expected_total,
                actual_value=total_amount,
                suggested_resolution=(
                    "Verify quantity and unit price, "
                    "then recalculate total_amount."
                ),
                message=(
                    f"Expected {expected_total}, "
                    f"found {total_amount}."
                )
            )

        # Check payment status
        status = order["payment_status"].strip()

        if status not in VALID_STATUSES:

            add_incident(
                category="INVALID_PAYMENT_STATUS",
                severity="MEDIUM",
                order_id=order_id,
                row_number=line_number,
                affected_field="payment_status",
                expected_value=sorted(VALID_STATUSES),
                actual_value=status,
                suggested_resolution=(
                    "Verify the payment status against "
                    "the allowed payment status values."
                ),
                message=(
                    f"Unsupported payment status: {status}."
                )
            )

    # --------------------------------------------------
    # 6. Build final incident report
    # --------------------------------------------------

    report = {
        "report_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": input_file.name,
        "rows_inspected": len(orders),
        "total_incidents": len(incidents),
        "status": "FAILED" if incidents else "PASSED",
        "incidents": incidents,
    }

    # --------------------------------------------------
    # 7. Save historical JSON report
    # --------------------------------------------------

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = (
        REPORT_DIR / f"report_{report['report_id']}.json"
    )

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    # --------------------------------------------------
    # 8. Display report summary
    # --------------------------------------------------

    print("\n=== TRACEFLOW AI: INCIDENT REPORT ===")
    print(f"Dataset: {input_file.name}")
    print(f"Rows inspected: {len(orders)}")
    print(f"Total incidents: {len(incidents)}")
    print(f"Status: {report['status']}")
    print(f"Report saved to: {report_file}")


# --------------------------------------------------
# Main program execution
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="TraceFlow AI - Data Quality Checker"
    )

    parser.add_argument(
        "input_file",
        help="Path to the order CSV file"
    )

    args = parser.parse_args()

    input_file = Path(args.input_file)

    if not input_file.is_absolute():
        input_file = PROJECT_ROOT / input_file

    check_orders(input_file)
