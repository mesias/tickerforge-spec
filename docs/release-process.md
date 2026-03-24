# Release Process

This repository publishes the **PyPI** package `tickerforge-spec-data`. The canonical spec files live only under the repository root `spec/`; the wheel bundles them via Hatch (`force-include`) at build time—no second checked-in copy.

The root `VERSION` file is the release authority.

## Prerequisites

- `spec/` is up to date
- `pyproject.toml` and `rust/Cargo.toml` versions match `VERSION` (`python scripts/check_versions.py`)

## Steps

1. Update root `VERSION` (semantic versioning).
2. Bump `version` in `pyproject.toml` and `rust/Cargo.toml` to match.
3. Run `python scripts/check_versions.py`.
4. Commit changes.
5. Create release tag:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`
6. GitHub Actions `release.yml` builds with `python -m build` and publishes `dist/` to PyPI.

## Rust crate

The `rust/` crate exists for `cargo check` in CI and points at `../spec` in a monorepo checkout. It is not published to crates.io (`publish = false`) until an embedding or packaging strategy for crates.io is defined.

## Notes

- If only packaging metadata changes, keep `VERSION` aligned and still tag a release when publishing to PyPI.
