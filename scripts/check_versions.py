#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_cargo_version(content: str) -> str:
    match = re.search(r"^version\s*=\s*\"([^\"]+)\"", content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find version in Cargo.toml")
    return match.group(1).strip()


def pyproject_declares_dynamic_version(text: str) -> bool:
    m = re.search(r"^\s*dynamic\s*=\s*\[(.*?)\]\s*$", text, re.MULTILINE | re.DOTALL)
    if not m:
        return False
    inner = m.group(1).replace("\n", " ")
    return bool(re.search(r"['\"]version['\"]", inner))


def pyproject_hatch_version_uses_version_file(text: str) -> bool:
    if "[tool.hatch.version]" not in text:
        return False
    # Require path = "VERSION" (Hatch reads semver from this file)
    return bool(re.search(r'^\s*path\s*=\s*["\']VERSION["\']', text, re.MULTILINE))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    canonical = (root / "VERSION").read_text(encoding="utf-8").strip()

    cargo_root = (root / "Cargo.toml").read_text(encoding="utf-8")
    cargo_version = extract_cargo_version(cargo_root)

    pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8")
    if not pyproject_declares_dynamic_version(pyproject_text):
        print(
            "pyproject.toml must set [project] dynamic = [\"version\"] "
            "and read the version from VERSION via Hatch.",
            file=sys.stderr,
        )
        return 1
    if not pyproject_hatch_version_uses_version_file(pyproject_text):
        print(
            "pyproject.toml must define [tool.hatch.version] with path = \"VERSION\".",
            file=sys.stderr,
        )
        return 1

    if cargo_version != canonical:
        print("Version mismatch detected:", file=sys.stderr)
        print(f"  VERSION: {canonical}", file=sys.stderr)
        print(f"  Cargo.toml: {cargo_version}", file=sys.stderr)
        print("Run: python3 scripts/sync_cargo_version.py", file=sys.stderr)
        return 1

    print(f"Versions are consistent: {canonical}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
