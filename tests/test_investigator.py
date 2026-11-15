
import sys
import unittest
from pathlib import Path

# Make the investigator module available to the test file.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INVESTIGATOR_DIR = PROJECT_ROOT / "src" / "investigator"

sys.path.insert(0, str(INVESTIGATOR_DIR))

from root_cause_analyzer import analyze_incident, analyze_report


class TestIncidentAnalyzer(unittest.TestCase):

    def test_duplicate_order_id(self):
        incident = {
            "category": "DUPLICATE_ORDER_ID",
            "order_id": "ORD0001",
            "message": "Order ID appears 2 times.",
            "row_numbers": [2, 3]
        }

        result = analyze_incident(incident)

        self.assertEqual(result["incident_category"], "DUPLICATE_ORDER_ID")
        self.assertEqual(result["detection_confidence"], "HIGH")
        self.assertEqual(result["root_cause_confidence"], "LOW")
        self.assertTrue(result["requires_human_review"])
        self.assertTrue(result["evidence"])
        self.assertTrue(result["recommended_action"])

    def test_missing_value(self):
        incident = {
            "category": "MISSING_VALUE",
            "order_id": "ORD0003",
            "message": "Missing value in product.",
            "affected_field": "product"
        }

        result = analyze_incident(incident)

        self.assertEqual(result["incident_category"], "MISSING_VALUE")
        self.assertEqual(result["detection_confidence"], "HIGH")
        self.assertEqual(result["root_cause_confidence"], "LOW")
        self.assertTrue(result["requires_human_review"])
        self.assertIn("product", result["evidence"][1])

    def test_total_mismatch(self):
        incident = {
            "category": "TOTAL_MISMATCH",
            "order_id": "ORD0004",
            "message": "Expected 12000, found 12100.",
            "expected_value": 12000,
            "actual_value": 12100
        }

        result = analyze_incident(incident)

        self.assertEqual(result["incident_category"], "TOTAL_MISMATCH")
        self.assertEqual(result["detection_confidence"], "HIGH")
        self.assertEqual(result["root_cause_confidence"], "LOW")
        self.assertTrue(result["requires_human_review"])
        self.assertIn("Expected total: 12000", result["evidence"])
        self.assertIn("Actual total: 12100", result["evidence"])

    def test_invalid_payment_status(self):
        incident = {
            "category": "INVALID_PAYMENT_STATUS",
            "order_id": "ORD0005",
            "message": "Unsupported payment status: UNKNOWN.",
            "actual_value": "UNKNOWN",
            "expected_value": ["FAILED", "PAID", "PENDING"]
        }

        result = analyze_incident(incident)

        self.assertEqual(
            result["incident_category"],
            "INVALID_PAYMENT_STATUS"
        )
        self.assertEqual(result["detection_confidence"], "HIGH")
        self.assertEqual(result["root_cause_confidence"], "LOW")
        self.assertTrue(result["requires_human_review"])
        self.assertIn("Unexpected value: UNKNOWN", result["evidence"])

    def test_unknown_incident_category(self):
        incident = {
            "category": "UNKNOWN_CATEGORY",
            "order_id": "ORD9999"
        }

        result = analyze_incident(incident)

        self.assertEqual(result["detection_confidence"], "LOW")
        self.assertEqual(result["root_cause_confidence"], "LOW")
        self.assertIn(
            "No investigation rule exists",
            result["confidence_reason"]
        )
        self.assertTrue(result["requires_human_review"])

    def test_analyze_multiple_incidents(self):
        report = {
            "incidents": [
                {
                    "category": "DUPLICATE_ORDER_ID",
                    "order_id": "ORD0001",
                    "row_numbers": [2, 3]
                },
                {
                    "category": "MISSING_VALUE",
                    "order_id": "ORD0003",
                    "affected_field": "product"
                },
                {
                    "category": "TOTAL_MISMATCH",
                    "order_id": "ORD0004",
                    "expected_value": 12000,
                    "actual_value": 12100
                },
                {
                    "category": "INVALID_PAYMENT_STATUS",
                    "order_id": "ORD0005",
                    "actual_value": "UNKNOWN",
                    "expected_value": ["FAILED", "PAID", "PENDING"]
                }
            ]
        }

        results = analyze_report(report)

        self.assertEqual(len(results), 4)

        for result in results:
            self.assertEqual(result["detection_confidence"], "HIGH")
            self.assertEqual(result["root_cause_confidence"], "LOW")
            self.assertTrue(result["requires_human_review"])

    def test_empty_incident_report(self):
        report = {"incidents": []}

        results = analyze_report(report)

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
