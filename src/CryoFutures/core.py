#!/usr/bin/env python3
"""Deterministic quantum-cooling capacity futures pricing and settlement (stdlib only).

CryoFutures recombines ColdMkh (quantum cooling market) and FailureFutures
(fragile-asset futures): a buyer hedges a fragile cold-capacity asset by taking
a future whose premium grows with failure probability and time to expiry.
"""

import math


def price_future(asset_value, failure_prob, days_to_expiry, payout_amount=None):
    """Price a CryoFutures contract.

    time_factor   = sqrt(days_to_expiry / 365.0)
    payout_amount = asset_value when omitted
    premium       = payout_amount * failure_prob * time_factor
    future_price  = premium (legacy alias for CLI/report compatibility)
    """
    if asset_value < 0:
        raise ValueError("asset_value must be non-negative")
    if not 0.0 <= failure_prob <= 1.0:
        raise ValueError("failure_prob must be within [0, 1]")
    if days_to_expiry < 0:
        raise ValueError("days_to_expiry must be non-negative")
    if payout_amount is None:
        payout_amount = asset_value
    if payout_amount < 0:
        raise ValueError("payout_amount must be non-negative")

    time_factor = math.sqrt(days_to_expiry / 365.0)
    premium = payout_amount * failure_prob * time_factor
    return {
        "settlement_mode": "failure_protection",
        "asset_value": asset_value,
        "payout_amount": payout_amount,
        "failure_prob": failure_prob,
        "days_to_expiry": days_to_expiry,
        "time_factor": time_factor,
        "premium": premium,
        "future_price": premium,
    }


def settle_contract(contract, actual_failure):
    """Settle a priced CryoFutures contract against the realized failure outcome.

    actual_failure=True  -> seller pays buyer payout_amount.
    actual_failure=False -> no payout; buyer loses only the premium.
    """
    if not isinstance(contract, dict):
        raise TypeError("contract must be a dict")
    missing = [k for k in ("asset_value",) if k not in contract]
    if missing:
        raise ValueError("contract missing fields: " + ", ".join(missing))

    contract_id = contract.get("contract_id", "")
    asset_value = contract["asset_value"]
    premium = contract.get("premium", contract.get("future_price"))
    if premium is None:
        raise ValueError("contract missing fields: premium")
    payout_amount = contract.get("payout_amount", asset_value)

    if actual_failure:
        settlement_amount = payout_amount
        buyer_net = payout_amount - premium
        seller_net = premium - payout_amount
    else:
        settlement_amount = 0.0
        buyer_net = -premium
        seller_net = premium

    return {
        "contract_id": contract_id,
        "settlement_mode": "failure_protection",
        "actual_failure": actual_failure,
        "premium": premium,
        "payout_amount": payout_amount,
        "settlement_amount": settlement_amount,
        "buyer_net": buyer_net,
        "seller_net": seller_net,
        "buyer_payoff": buyer_net,
        "seller_payoff": seller_net,
    }


def render_report(result):
    """Render a deterministic Markdown report for a price or settlement result."""
    lines = ["# CryoFutures Report", ""]

    if "future_price" in result:
        lines += ["## Pricing", ""]
        if result.get("contract_id"):
            lines.append(f"- contract_id: {result['contract_id']}")
        if result.get("buyer"):
            lines.append(f"- buyer: {result['buyer']}")
        if result.get("seller"):
            lines.append(f"- seller: {result['seller']}")
        lines += [
            f"- settlement_mode: {result['settlement_mode']}",
            f"- asset_value: {result['asset_value']}",
            f"- payout_amount: {result['payout_amount']}",
            f"- failure_prob: {result['failure_prob']}",
            f"- days_to_expiry: {result['days_to_expiry']}",
            f"- time_factor: {result['time_factor']}",
            f"- premium: {result['premium']}",
            f"- future_price: {result['future_price']} (premium alias)",
        ]
    elif "settlement_amount" in result:
        lines += [
            "## Settlement",
            "",
            f"- contract_id: {result.get('contract_id', '')}",
            f"- settlement_mode: {result.get('settlement_mode', '')}",
            f"- actual_failure: {result['actual_failure']}",
            f"- premium: {result['premium']}",
            f"- payout_amount: {result['payout_amount']}",
            f"- settlement_amount: {result['settlement_amount']}",
            f"- buyer_net: {result['buyer_net']}",
            f"- seller_net: {result['seller_net']}",
        ]
    else:
        lines.append("(no recognizable result fields)")
    lines.append("")
    return "\n".join(lines)
