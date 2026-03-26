# Release Process

This repository publishes **`tickerforge-spec-data`** in two forms from the **same tag**:

| Job | Artifact |
|-----|----------|
| `release_pypi` | Python wheel/sdist → **PyPI** |
| `release_crates` | Rust crate (root `Cargo.toml`, `spec/` included) → **crates.io** |

The canonical spec files live only under the repository root `spec/`; the Python wheel bundles them via Hatch (`force-include`) at build time. The Rust crate lists `spec/**/*` in `[package].include` so `cargo publish` ships the same tree.

The root `VERSION` file is the release authority.

## Prerequisites

- `spec/` is up to date
- `VERSION`, `pyproject.toml`, root `Cargo.toml`, and `rust/Cargo.toml` versions all match (`python scripts/check_versions.py`)
- GitHub **Environments**: `release` with PyPI trusted publishing (OIDC) and a **`CRATES_IO_TOKEN`** secret for crates.io

## Steps

1. Update root `VERSION` (semantic versioning).
2. Bump `version` in `pyproject.toml`, root `Cargo.toml`, and `rust/Cargo.toml` to match.
3. Run `python scripts/check_versions.py`.
4. Commit changes.
5. Create release tag:
   - `git tag vX.Y.Z` (must match `VERSION`, e.g. `VERSION` `1.2.3` → tag `v1.2.3`)
   - `git push origin vX.Y.Z`
6. GitHub Actions `release.yml` runs **validate**, then **release_pypi** and **release_crates** in parallel.

## Notes

- The `rust/` manifest is for local/CI `cargo check --manifest-path rust/Cargo.toml` and has `publish = false`. The **published** Rust package is the **repository root** crate (`cargo publish` at the repo root).
- If only packaging metadata changes, keep `VERSION` aligned and still tag a release when publishing.
