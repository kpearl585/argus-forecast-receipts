"""Recompute a forecast hash from its revealed file.

Usage: python3 verify.py reveals/<forecast_id>.json
The hash is sha256 over json.dumps({forecast_id, issued_for_map_date,
resolves_on_map_date, cells}, sort_keys=True) with Python's default
separators. Compare the printed value with the row in receipts.csv.
"""
import hashlib
import json
import sys

d = json.load(open(sys.argv[1]))
blob = json.dumps({k: d[k] for k in ("forecast_id", "issued_for_map_date", "resolves_on_map_date", "cells")}, sort_keys=True)
print(hashlib.sha256(blob.encode()).hexdigest())
