#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


def extract(pattern: str, content: str, label: str) -> str:
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find version in {label}")
    return match.group(1).strip()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    canonical = (root / "VERSION").read_text(encoding="utf-8").strip()

    python_toml = (root / "packaging" / "python" / "pyproject.toml").read_text(encoding="utf-8")
    python_version = extract(r'^version\s*=\s*"([^"]+)"', python_toml, "packaging/python/pyproject.toml")

    cargo_toml = (root / "packaging" / "rust" / "Cargo.toml").read_text(encoding="utf-8")
    rust_version = extract(r'^version\s*=\s*"([^"]+)"', cargo_toml, "packaging/rust/Cargo.toml")

    versions = {
        "VERSION": canonical,
        "python": python_version,
        "rust": rust_version,
    }
    if len(set(versions.values())) != 1:
        print("Version mismatch detected:")
        for key, value in versions.items():
            print(f"  {key}: {value}")
        return 1

    print(f"Versions are consistent: {canonical}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
