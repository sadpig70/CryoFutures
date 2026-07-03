#!/usr/bin/env python3
"""CLI for CryoFutures."""

import argparse
import json
import sys

from .core import price_future, render_report, settle_contract
from .samples import write_samples


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(doc, path=None):
    text = json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


def cmd_sample(args):
    written = write_samples(args.out)
    _dump_json({"written": written})
    return 0


def cmd_price(args):
    result = price_future(args.asset_value, args.failure_prob, args.days_to_expiry)
    _dump_json(result, args.out)
    return 0


def cmd_settle(args):
    contract = _load_json(args.input)
    result = settle_contract(contract, args.actual_failure)
    _dump_json(result, args.out)
    return 0


def cmd_report(args):
    doc = _load_json(args.input)
    text = render_report(doc)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="cryo-futures")
    sub = p.add_subparsers(dest="cmd", required=True)

    sample = sub.add_parser("sample", help="emit deterministic valid/breach contract fixtures")
    sample.add_argument("--out", default="examples")
    sample.set_defaults(func=cmd_sample)

    price = sub.add_parser("price", help="price a CryoFutures contract")
    price.add_argument("--asset-value", type=float, required=True)
    price.add_argument("--failure-prob", type=float, required=True)
    price.add_argument("--days-to-expiry", type=int, required=True)
    price.add_argument("--out")
    price.set_defaults(func=cmd_price)

    settle = sub.add_parser("settle", help="settle a priced contract against the realized failure")
    settle.add_argument("--input", required=True)
    settle.add_argument("--actual-failure", action="store_true",
                        help="the protected asset failed (seller pays buyer asset_value)")
    settle.add_argument("--out")
    settle.set_defaults(func=cmd_settle)

    report = sub.add_parser("report", help="render a Markdown report for a price or settlement result")
    report.add_argument("--input", required=True)
    report.add_argument("--out")
    report.set_defaults(func=cmd_report)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)
