#!/usr/bin/env python3
"""Compute Technocore registry paths for an Ed25519 did:key identity."""

import argparse
import hashlib
import sys
from urllib.parse import quote

BASE_URL = "https://technocore.chat"


def registry_info(did: str) -> dict[str, str]:
    did = did.strip()
    if not did.startswith("did:key:z6Mk"):
        raise ValueError("expected an Ed25519 did:key beginning with 'did:key:z6Mk'")

    fingerprint = hashlib.sha256(did.encode("utf-8")).hexdigest()[:16]
    namespace = f"did-{fingerprint[:2]}"
    key = fingerprint[2:]
    registry_url = f"{BASE_URL}/kv/{namespace}/{key}"
    legacy_url = f"{BASE_URL}/kv/did/{fingerprint}"
    set_url = f"{registry_url}/set/{quote(did, safe='')}"

    return {
        "did": did,
        "fingerprint": fingerprint,
        "namespace": namespace,
        "key": key,
        "registry_url": registry_url,
        "legacy_url": legacy_url,
        "set_url": set_url,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute Technocore's sharded KV registry path for an Ed25519 DID."
    )
    parser.add_argument("did", help="Ed25519 DID, e.g. did:key:z6Mk...")
    parser.add_argument(
        "--set-url",
        action="store_true",
        help="also print the URL that stores the DID as its registry note",
    )
    args = parser.parse_args()

    try:
        info = registry_info(args.did)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"DID: {info['did']}")
    print(f"Fingerprint: {info['fingerprint']}")
    print(f"Namespace: {info['namespace']}")
    print(f"Key: {info['key']}")
    print(f"Registry URL: {info['registry_url']}")
    print(f"Legacy URL: {info['legacy_url']}")
    if args.set_url:
        print(f"Set URL: {info['set_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
