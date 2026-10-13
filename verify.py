"""Recompute the published four-key forecast hash without changing its format.

Usage: python3 verify.py reveals/<forecast_id>.json
The hash is sha256 over json.dumps({forecast_id, issued_for_map_date,
resolves_on_map_date, cells}, sort_keys=True) with Python's default
separators. Compare the printed value with the row in receipts.csv.
"""
import hashlib
import json
from pathlib import Path
import sys


def forecast_hash(payload):
    blob = json.dumps(
        {key: payload[key] for key in (
            "forecast_id", "issued_for_map_date", "resolves_on_map_date", "cells"
        )},
        sort_keys=True,
        allow_nan=False,
    )
    return hashlib.sha256(blob.encode()).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 verify.py reveals/<forecast_id>.json")
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(forecast_hash(payload))
