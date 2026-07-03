#!/usr/bin/env python3
"""Deterministic quantum-cooling capacity futures pricing and settlement (stdlib only).

CryoFutures recombines ColdMkh (quantum cooling market) and FailureFutures
(fragile-asset futures): a buyer hedges a fragile cold-capacity asset by taking
a future whose premium grows with failure probability and time to expiry.
"""

import math


def price_future(asset_value, failure_prob, days_to_expiry):
    """Price a CryoFutures contract.

    time_factor   = sqrt(days_to_expiry / 365.0)
    premium       = asset_value * failure_prob * time_factor
    future_price  = asset_value + premium
    """
    if asset_value < 0:
        raise ValueError("asset_value must be non-negative")
    if not 0.0 <= failure_prob <= 1.0:
        raise ValueError("failure_prob must be within [0, 1]")
    if days_to_expiry < 0:
        raise ValueError("days_to_expiry must be non-negative")

    time_factor = math.sqrt(days_to_expiry / 365.0)
    premium = asset_value * failure_prob * time_factor
    future_price = asset_value + premium
    return {
        "asset_value": asset_value,
        "failure_prob": failure_prob,
        "days_to_expiry": days_to_expiry,
        "time_factor": time_factor,
        "premium": premium,
        "future_price": future_price,
    }


def settle_contract(contract, actual_failure):
    """Settle a priced CryoFutures contract against the realized failure outcome.

    actual_failure=True  -> seller pays buyer asset_value (failure payout).
    actual_failure=False -> buyer pays seller future_price (premium settled).
    """
    if not isinstance(contract, dict):
        raise TypeError("contract must be a dict")
    missing = [k for k in ("asset_value", "future_price") if k not in contract]
    if missing:
        raise ValueError("contract missing fields: " + ", ".join(missing))

    contract_id = contract.get("contract_id", "")
    asset_value = contract["asset_value"]
    future_price = contract["future_price"]

    if actual_failure:
        settlement_amount = asset_value
        buyer_payoff = asset_value
        seller_payoff = -asset_value
    else:
        settlement_amount = future_price
        buyer_payoff = -future_price
        seller_payoff = future_price

    return {
        "contract_id": contract_id,
        "actual_failure": actual_failure,
        "settlement_amount": settlement_amount,
        "buyer_payoff": buyer_payoff,
        "seller_payoff": seller_payoff,
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
            f"- asset_value: {result['asset_value']}",
            f"- failure_prob: {result['failure_prob']}",
            f"- days_to_expiry: {result['days_to_expiry']}",
            f"- time_factor: {result['time_factor']}",
            f"- premium: {result['premium']}",
            f"- future_price: {result['future_price']}",
        ]
    elif "settlement_amount" in result:
        lines += [
            "## Settlement",
            "",
            f"- contract_id: {result.get('contract_id', '')}",
            f"- actual_failure: {result['actual_failure']}",
            f"- settlement_amount: {result['settlement_amount']}",
            f"- buyer_payoff: {result['buyer_payoff']}",
            f"- seller_payoff: {result['seller_payoff']}",
        ]
    else:
        lines.append("(no recognizable result fields)")
    lines.append("")
    return "\n".join(lines)
