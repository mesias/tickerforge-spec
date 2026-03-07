# tickerforge-spec-data (Rust)

Rust crate containing the canonical TickerForge specification files.

## Install

```bash
cargo add tickerforge-spec-data
```

## Usage

```rust
use tickerforge_spec_data::{spec_root, version};

println!("{}", spec_root().display());
println!("{}", version());
```
