
import csv
import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

import src.quality.check_orders as checker


class TestOrderQualityChecker(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_folder = Path(self.temp_dir.name)

        # Create temporary CSV file
        self.csv_file = self.test_folder / "orders_test.csv"

        # Sample records containing four deliberate issues
        self.orders = [
            {
                "order_id": "ORD0001",
                "product": "Laptop",
                "quantity": "1",
                "unit_price": "55000",
                "total_amount": "55000",
                "payment_status": "PAID",
            },
            {
                "order_id": "ORD0001",
                "product": "Keyboard",
                "quantity": "1",
                "unit_price": "1500",
                "total_amount": "1500",
                "payment_status": "PAID",
            },
            {
                "order_id": "ORD0003",
                "product": "",
                "quantity": "3",
                "unit_price": "2500",
                "total_amount": "7500",
                "payment_status": "PAID",
            },
            {
                "order_id": "ORD0004",
                "product": "Monitor",
                "quantity": "1",
                "unit_price": "12000",
                "total_amount": "12100",
                "payment_status": "PAID",
            },
            {
                "order_id": "ORD0005",
                "product": "Mouse",
                "quantity": "1",
                "unit_price": "800",
                "total_amount": "800",
                "payment_status": "UNKNOWN",
            },
        ]

        self.fieldnames = [
            "order_id",
            "product",
            "quantity",
            "unit_price",
            "total_amount",
            "payment_status",
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_csv(self, orders):
        with self.csv_file.open(
            "w", newline="", encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.fieldnames
            )

            writer.writeheader()
            writer.writerows(orders)

    def run_checker(self):
        # Save test reports separately from project reports
        test_report_dir = self.test_folder / "reports"

        with patch.object(
            checker, "REPORT_DIR", test_report_dir
        ):
            checker.check_orders(self.csv_file)

        report_files = list(test_report_dir.glob("*.json"))

        self.assertEqual(len(report_files), 1)

        with report_files[0].open(
            "r", encoding="utf-8"
        ) as file:
            return json.load(file)

    def test_detects_four_data_quality_issues(self):
        self.create_csv(self.orders)

        report = self.run_checker()

        self.assertEqual(report["status"], "FAILED")
        self.assertEqual(report["rows_inspected"], 5)
        self.assertEqual(report["total_incidents"], 4)

    def test_duplicate_order_id_has_row_numbers(self):
        self.create_csv(self.orders)

        report = self.run_checker()

        duplicate = next(
            incident
            for incident in report["incidents"]
            if incident["category"] == "DUPLICATE_ORDER_ID"
        )

        self.assertEqual(
            duplicate["row_numbers"], [2, 3]
        )

    def test_total_mismatch_has_diagnostic_details(self):
        self.create_csv(self.orders)

        report = self.run_checker()

        mismatch = next(
            incident
            for incident in report["incidents"]
            if incident["category"] == "TOTAL_MISMATCH"
        )

        self.assertEqual(
            mismatch["affected_field"], "total_amount"
        )

        self.assertEqual(mismatch["expected_value"], 12000)
        self.assertEqual(mismatch["actual_value"], 12100)

        self.assertIsNotNone(
            mismatch["suggested_resolution"]
        )

    def test_clean_dataset_passes(self):
        clean_orders = [
            {
                "order_id": "ORD1001",
                "product": "Laptop",
                "quantity": "1",
                "unit_price": "55000",
                "total_amount": "55000",
                "payment_status": "PAID",
            },
            {
                "order_id": "ORD1002",
                "product": "Mouse",
                "quantity": "2",
                "unit_price": "800",
                "total_amount": "1600",
                "payment_status": "PENDING",
            },
        ]

        self.create_csv(clean_orders)

        report = self.run_checker()

        self.assertEqual(report["status"], "PASSED")
        self.assertEqual(report["total_incidents"], 0)


if __name__ == "__main__":
    unittest.main()
