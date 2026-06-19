# Implementation Plan - Automate Version Tagging and Release (Option A)

This plan details the changes required to automate version tagging and package publication when merging to the default branch (`develop` or `main`) across all three TickerForge source repositories.

## Proposed Changes

### 1. `tickerforge-spec`

#### [MODIFY] [.github/workflows/release.yml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/.github/workflows/release.yml)
- Change trigger from tags (`v*`) to pushes on `develop` or `main` branches.
- Add a `tag` job that checks if a tag matching `v<VERSION>` already exists.
- If it does not exist, create and push it using `GITHUB_TOKEN` (requiring `contents: write` permissions).
- Conditionalize `release_pypi`, `release_crates`, and `github_release` jobs to only execute if a new tag was created.

---

### 2. `tickerforge-py`

#### [MODIFY] [.github/workflows/release.yml](file:///home/amesias/Dev/tickerforge/tickerforge-py/.github/workflows/release.yml)
- Change trigger from tags (`v*`) to pushes on `main` branch.
- Add the `tag` job to check/create the tag.
- Conditionalize `release_pypi` and `github_release` jobs.

---

### 3. `tickerforge-rs`

#### [MODIFY] [.github/workflows/release.yml](file:///home/amesias/Dev/tickerforge/tickerforge-rs/.github/workflows/release.yml)
- Change trigger from tags (`v*`) to pushes on `main` branch.
- Add the `tag` job to check/create the tag.
- Conditionalize `publish-crate` and `github_release` jobs.

## Verification Plan

- Push the updated workflows to the `feature/add-b3-futures` branches on all repositories.
- The user can verify by merging the branches into their respective default branches, which should automatically create the `v0.1.8` tag and release the packages.
