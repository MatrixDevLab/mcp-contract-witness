import json
import unittest
from pathlib import Path

import witness


ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "fixtures"


class WitnessTests(unittest.TestCase):
    def compare(self, before: str, after: str) -> dict:
        return witness.compare(FIXTURES / before, FIXTURES / after)

    def test_reordered_json_and_tools_are_current(self):
        result = self.compare("base.json", "reordered.json")
        self.assertEqual(result["state"], "current")
        self.assertEqual(result["changed_dimensions"], [])

    def test_description_changes_metadata_and_catalog(self):
        result = self.compare("base.json", "description-change.json")
        self.assertEqual(result["state"], "changed")
        self.assertEqual(result["changed_dimensions"], ["metadata", "catalog"])

    def test_input_and_output_changes_are_typed(self):
        input_result = self.compare("base.json", "input-change.json")
        output_result = self.compare("base.json", "output-change.json")
        self.assertEqual(input_result["changed_dimensions"], ["input_schema", "catalog"])
        self.assertEqual(output_result["changed_dimensions"], ["output_schema", "catalog"])

    def test_membership_change_affects_identity_and_catalog(self):
        result = self.compare("base.json", "tool-added.json")
        self.assertEqual(result["changed_dimensions"], ["identity", "input_schema", "output_schema", "metadata", "catalog"])

    def test_protocol_change_is_incompatible(self):
        result = self.compare("base.json", "protocol-change.json")
        self.assertEqual(result["state"], "incompatible")
        self.assertIn("protocol_era", result["changed_dimensions"])

    def test_malformed_and_incomplete_are_unknown(self):
        malformed = self.compare("base.json", "malformed.json")
        incomplete = self.compare("base.json", "incomplete.json")
        self.assertEqual(malformed["state"], "unknown")
        self.assertEqual(incomplete["state"], "unknown")
        self.assertIn("unsupported", malformed["reason"])
        self.assertIn("inputSchema", incomplete["reason"])

    def test_output_is_byte_stable(self):
        first = json.dumps(self.compare("base.json", "input-change.json"), indent=2, sort_keys=True)
        second = json.dumps(self.compare("base.json", "input-change.json"), indent=2, sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
