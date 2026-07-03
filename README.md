![CryoFutures](assets/CryoFutures_hero.png)

# CryoFutures

> Quantum cooling capacity futures exchange — price and settle failure-protection contracts for fragile cold-capacity assets.

## One-sentence pitch

`CryoFutures` answers: *What is a fair future price for hedging a fragile quantum-cooling asset, and who pays whom when the asset either survives or fails before expiry?*

## Why this matters

Quantum-cooling capacity is a scarce, fragile energy resource. Operators who depend on a cold-capacity asset face a real risk that the asset fails before a mission window closes. A failure-protection future lets a buyer pay a time- and probability-weighted premium today in exchange for a guaranteed payout if the asset fails, or a settled premium if it survives.

`CryoFutures` is a stdlib-only CLI and Python package that prices those contracts deterministically and settles them against the realized outcome.

## What it is not

- Not a live exchange or order-matching engine.
- Not a risk model beyond the stated closed-form premium.
- Not a settlement rail or custody system.
- Not a legal contract generator.

It prices a compact contract spec and settles it into a deterministic payoff document.

## Pricing model

```
time_factor   = sqrt(days_to_expiry / 365.0)
premium       = asset_value * failure_prob * time_factor
future_price  = asset_value + premium
```

## Settlement model

- `actual_failure=True`  → seller pays buyer `asset_value` (failure payout).
- `actual_failure=False` → buyer pays seller `future_price` (premium settled).

## Install / Run

Requires Python 3.10+ and no external packages.

From this project root:

```bash
python -m pip install -e .
python -m CryoFutures sample --out examples
python -m CryoFutures price --asset-value 5000000 --failure-prob 0.05 --days-to-expiry 90
python -m CryoFutures settle --input examples/valid.json
python -m CryoFutures settle --input examples/valid.json --actual-failure
python -m CryoFutures report --input examples/valid.json --out examples/valid.report.md
```

## CLI

| command  | purpose                                                       |
|----------|---------------------------------------------------------------|
| `sample` | emit deterministic `valid`/`breach` contract fixtures        |
| `price`  | price a future from asset value, failure prob, and tenor      |
| `settle` | settle a priced contract; `--actual-failure` toggles payout   |
| `report` | render a Markdown report for a price or settlement result     |

## Python API

```python
from CryoFutures import price_future, settle_contract, render_report

priced = price_future(asset_value=5_000_000, failure_prob=0.05, days_to_expiry=90)
print(priced["future_price"])

contract = {"contract_id": "CF-001", "buyer": "alpha", "seller": "exchange", **priced}
print(settle_contract(contract, actual_failure=True))
print(render_report(priced))
```

## Tests

From this project root:

```bash
python -m unittest discover -s tests -q
```

## License

MIT License — see [LICENSE](LICENSE).
