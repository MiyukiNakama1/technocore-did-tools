#!/usr/bin/env python3
"""Check a Technocore DID note at the current sharded path and legacy fallback."""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.error
import urllib.request

BASE_URL = "https://technocore.chat"


def fingerprint(did: str) -> str:
    return hashlib.sha256(did.encode("utf-8")).hexdigest()[:16]


def urls_for(did: str) -> tuple[str, str]:
    fp = fingerprint(did)
    sharded = f"{BASE_URL}/kv/did-{fp[:2]}/{fp[2:]}"
    legacy = f"{BASE_URL}/kv/did/{fp}"
    return sharded, legacy


def fetch_text(url: str, timeout: float = 10.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "technocore-did-tools/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return error.code, body


def contains_exact_did(body: str, did: str) -> bool:
    return any(line.strip() == did for line in body.splitlines())


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a Technocore DID registry note")
    parser.add_argument("did", help="canonical Ed25519 DID, e.g. did:key:z6Mk...")
    args = parser.parse_args()

    if not args.did.startswith("did:key:z6Mk"):
        print("error: expected an Ed25519 did:key beginning with did:key:z6Mk", file=sys.stderr)
        return 2

    fp = fingerprint(args.did)
    sharded, legacy = urls_for(args.did)

    print(f"DID: {args.did}")
    print(f"Fingerprint: {fp}")
    print(f"Sharded URL: {sharded}")
    print(f"Legacy URL: {legacy}")

    for label, url in (("sharded", sharded), ("legacy", legacy)):
        try:
            status, body = fetch_text(url)
        except urllib.error.URLError as error:
            print(f"{label}: network error: {error.reason}")
            continue

        matched = status == 200 and contains_exact_did(body, args.did)
        print(f"{label}: HTTP {status} - {'MATCH' if matched else 'no exact DID match'}")
        if matched:
            print(f"verified_path: {url}")
            return 0

    print("result: DID was not verified at either registry path")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
