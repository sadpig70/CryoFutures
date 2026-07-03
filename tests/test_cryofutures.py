#!/usr/bin/env python3
"""Stdlib-only tests for the standalone CryoFutures package."""

import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from CryoFutures.core import price_future, render_report, settle_contract  # noqa: E402
from CryoFutures.samples import samples, VALID_CONTRACT, BREACH_CONTRACT  # noqa: E402


class TestPricing(unittest.TestCase):
    def test_price_future_deterministic(self):
        a = price_future(5000000, 0.05, 90)
        b = price_future(5000000, 0.05, 90)
        self.assertEqual(a, b)

    def test_price_future_formula(self):
        r = price_future(5000000, 0.05, 90)
        expected_time_factor = math.sqrt(90 / 365.0)
        expected_premium = 5000000 * 0.05 * expected_time_factor
        self.assertAlmostEqual(r["time_factor"], expected_time_factor)
        self.assertAlmostEqual(r["premium"], expected_premium)
        self.assertAlmostEqual(r["future_price"], 5000000 + expected_premium)
        self.assertEqual(r["asset_value"], 5000000)
        self.assertEqual(r["failure_prob"], 0.05)
        self.assertEqual(r["days_to_expiry"], 90)

    def test_price_future_rejects_bad_prob(self):
        with self.assertRaises(ValueError):
            price_future(1000, 1.5, 30)

    def test_samples_are_distinct(self):
        self.assertNotEqual(
            VALID_CONTRACT["future_price"], BREACH_CONTRACT["future_price"]
        )


class TestSettlement(unittest.TestCase):
    def test_settle_on_failure(self):
        contract = samples()["valid"]
        result = settle_contract(contract, actual_failure=True)
        self.assertTrue(result["actual_failure"])
        self.assertEqual(result["settlement_amount"], contract["asset_value"])
        self.assertEqual(result["buyer_payoff"], contract["asset_value"])
        self.assertEqual(result["seller_payoff"], -contract["asset_value"])

    def test_settle_no_failure(self):
        contract = samples()["valid"]
        result = settle_contract(contract, actual_failure=False)
        self.assertFalse(result["actual_failure"])
        self.assertEqual(result["settlement_amount"], contract["future_price"])
        self.assertEqual(result["buyer_payoff"], -contract["future_price"])
        self.assertEqual(result["seller_payoff"], contract["future_price"])

    def test_settle_preserves_contract_id(self):
        contract = samples()["breach"]
        result = settle_contract(contract, actual_failure=True)
        self.assertEqual(result["contract_id"], contract["contract_id"])


class TestReport(unittest.TestCase):
    def test_render_pricing_report(self):
        text = render_report(price_future(1000, 0.1, 30))
        self.assertIn("# CryoFutures Report", text)
        self.assertIn("future_price", text)

    def test_render_settlement_report(self):
        contract = samples()["valid"]
        text = render_report(settle_contract(contract, actual_failure=True))
        self.assertIn("settlement_amount", text)
        self.assertIn("buyer_payoff", text)


class TestCLI(unittest.TestCase):
    def test_cli_sample(self):
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.check_output(
                [sys.executable, "-m", "CryoFutures", "sample", "--out", d],
                cwd=os.path.join(SRC, ".."), text=True, env={**os.environ, "PYTHONPATH": SRC},
            )
            written = json.loads(out)["written"]
            self.assertIn("valid", written)
            self.assertIn("breach", written)
            with open(written["valid"], "r", encoding="utf-8") as f:
                contract = json.load(f)
            self.assertEqual(contract["asset_value"], VALID_CONTRACT["asset_value"])

    def test_cli_price(self):
        out = subprocess.check_output(
            [sys.executable, "-m", "CryoFutures", "price",
             "--asset-value", "5000000", "--failure-prob", "0.05", "--days-to-expiry", "90"],
            cwd=os.path.join(SRC, ".."), text=True, env={**os.environ, "PYTHONPATH": SRC},
        )
        r = json.loads(out)
        self.assertAlmostEqual(
            r["future_price"], price_future(5000000, 0.05, 90)["future_price"]
        )

    def test_cli_settle_both_branches(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.check_output(
                [sys.executable, "-m", "CryoFutures", "sample", "--out", d],
                cwd=os.path.join(SRC, ".."), text=True, env={**os.environ, "PYTHONPATH": SRC},
            )
            valid = os.path.join(d, "valid.json")
            out_no = json.loads(subprocess.check_output(
                [sys.executable, "-m", "CryoFutures", "settle", "--input", valid],
                cwd=os.path.join(SRC, ".."), text=True, env={**os.environ, "PYTHONPATH": SRC},
            ))
            self.assertFalse(out_no["actual_failure"])
            self.assertGreater(out_no["settlement_amount"], 0)
            out_yes = json.loads(subprocess.check_output(
                [sys.executable, "-m", "CryoFutures", "settle",
                 "--input", valid, "--actual-failure"],
                cwd=os.path.join(SRC, ".."), text=True, env={**os.environ, "PYTHONPATH": SRC},
            ))
            self.assertTrue(out_yes["actual_failure"])
            self.assertGreater(out_yes["buyer_payoff"], 0)


if __name__ == "__main__":
    unittest.main()
