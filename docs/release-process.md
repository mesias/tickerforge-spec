# Release Process

This repository publishes two artifacts from the same canonical spec source:

- PyPI package: `tickerforge-spec-data`
- crates.io crate: `tickerforge-spec-data`

Both must always match the root `VERSION`.

## Prerequisites

- `spec/` is up to date
- packaging assets are synced into:
  - `packaging/python/src/tickerforge_spec_data/spec`
  - `packaging/rust/spec`

## Steps

1. Update root `VERSION` (semantic versioning).
2. Update package manifests:
   - `packaging/python/pyproject.toml`
   - `packaging/rust/Cargo.toml`
3. Sync packaged assets:
   - `python scripts/sync_packaging_assets.py`
4. Run validation:
   - `python scripts/check_versions.py`
   - `python scripts/sync_packaging_assets.py --check`
5. Commit changes.
6. Create release tag:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`
7. GitHub Actions `release.yml` publishes to PyPI and crates.io.

## Notes

- If only packaging changes, keep `VERSION` aligned and still tag a release.
- If spec data changes, always sync assets before release.
