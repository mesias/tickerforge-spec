//! Bundled [`spec/`] tree for [`tickerforge`](https://github.com/mesias/tickerforge-rs).
//!
//! [`spec/`]: https://github.com/mesias/tickerforge-spec/tree/main/spec

use std::path::PathBuf;

/// Root directory of the canonical spec (`exchanges/`, `contracts/`, `schemas/`, …).
///
/// This matches the layout shipped in the Python `tickerforge-spec-data` package.
pub fn default_spec_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("spec")
}
