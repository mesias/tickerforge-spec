use std::path::PathBuf;

pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

pub fn spec_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("spec")
}
