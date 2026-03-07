#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _compare_recursive(source: Path, target: Path) -> tuple[list[str], list[str], list[str]]:
    source_entries = {path.relative_to(source) for path in source.rglob("*")}
    target_entries = {path.relative_to(target) for path in target.rglob("*")}

    left_only = sorted(str(item) for item in (source_entries - target_entries))
    right_only = sorted(str(item) for item in (target_entries - source_entries))

    diff_files: list[str] = []
    for rel in sorted(source_entries & target_entries):
        source_path = source / rel
        target_path = target / rel
        if source_path.is_file() and target_path.is_file():
            if source_path.read_bytes() != target_path.read_bytes():
                diff_files.append(str(rel))

    return left_only, right_only, diff_files


def sync_or_check(source: Path, target: Path, check_only: bool) -> int:
    if check_only:
        if not target.exists():
            print(f"Missing target directory: {target}")
            return 1
        left_only, right_only, diff_files = _compare_recursive(source, target)
        if left_only or right_only or diff_files:
            print(f"Out-of-sync assets: {target}")
            print(f"left_only={left_only}")
            print(f"right_only={right_only}")
            print(f"diff_files={diff_files}")
            return 1
        return 0

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    print(f"Synced {source} -> {target}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync canonical spec assets into packaging wrappers.")
    parser.add_argument("--check", action="store_true", help="Check mode; fail if assets are out of sync.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    canonical = root / "spec"
    py_target = root / "packaging" / "python" / "src" / "tickerforge_spec_data" / "spec"
    rust_target = root / "packaging" / "rust" / "spec"

    rc = 0
    rc |= sync_or_check(canonical, py_target, args.check)
    rc |= sync_or_check(canonical, rust_target, args.check)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
