//! This crate is intended for use from a checkout of the `tickerforge-spec` repository.
//! `spec_root()` points at the repository's `spec/` directory (`../spec` from this manifest).

use std::path::PathBuf;

/// Path to the canonical `spec/` tree when building inside the monorepo.
pub fn spec_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("spec")
}
