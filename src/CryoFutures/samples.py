#!/usr/bin/env python3
"""Deterministic sample contracts for CryoFutures."""

import copy
import json

from .core import price_future


def _contract(contract_id, buyer, seller, asset_value, failure_prob, days_to_expiry):
    priced = price_future(asset_value, failure_prob, days_to_expiry)
    return {
        "contract_id": contract_id,
        "buyer": buyer,
        "seller": seller,
        **priced,
    }


VALID_CONTRACT = _contract(
    contract_id="CF-VALID-001",
    buyer="cryo-bank-alpha",
    seller="quantum-cool-exchange",
    asset_value=5000000,
    failure_prob=0.05,
    days_to_expiry=90,
)

BREACH_CONTRACT = _contract(
    contract_id="CF-BREACH-001",
    buyer="cryo-bank-alpha",
    seller="quantum-cool-exchange",
    asset_value=5000000,
    failure_prob=0.25,
    days_to_expiry=180,
)


def samples():
    return {
        "valid": copy.deepcopy(VALID_CONTRACT),
        "breach": copy.deepcopy(BREACH_CONTRACT),
    }


def write_samples(out_dir):
    import os

    os.makedirs(out_dir, exist_ok=True)
    written = {}
    for name, contract in samples().items():
        path = os.path.join(out_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contract, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        written[name] = path
    return written
