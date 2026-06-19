# Add Equities Specification to TickerForge

This plan outlines the steps required to add support for cash equities (e.g. `PETR4`, `VALE3`, `ITUB4`) to both the specifications, the Python parser library, and the Rust parser library.

## User Review Required

> [!WARNING]
> Since standard equities don't have expirations or cycles like futures/options, they will be modeled as an `EquitySpec` and parsed into a new variant `AnyParsedTicker::Equity`.
> I will define the exact `sessions` (e.g. `start: "10:00"`, `end: "17:00"`) for **each** of the 40+ assets directly in the YAML file as requested, ensuring a complete import of all information without relying on exchange-level fallbacks.

## Proposed Changes

---

### `tickerforge-spec`

#### [NEW] `spec/schemas/equities_schema.yaml`
Create a JSON Schema to validate the structure of equities definitions.
* Validates a root `equities` array.
* Requires `symbol`, `exchange`, `type`, and `sessions`.

#### [NEW] `spec/equities/b3.yaml`
Add a new file defining a comprehensive list of highly liquid B3 equities (the Ibovespa components). This will include `PETR4`, `VALE3`, `ITUB4`, `BBDC4`, `B3SA3`, `ABEV3`, `WEGE3`, `BBAS3`, `ELET3`, `RENT3`, `SUZB3`, `BPAC11`, `EQTL3`, `RADL3`, `PRIO3`, `ITSA4`, `BBSE3`, `JBSS3`, `VIVT3`, `HAPV3`, `CMIG4`, `KLBN11`, `SANB11`, `LREN3`, `CSNA3`, `GGBR4`, `ENEV3`, `CPLE6`, `TOTS3`, `EGIE3`, `TIMS3`, `CCRO3`, `SABP11`, `BRFS3`, `UGPA3`, `EMBR3`, `NTCO3`, `CYRE3`, `MULT3`, etc.
* Format will feature a top-level `equities` array.
* Each entry will specify its root symbol, exchange (`B3`), type (`equity`), description, and its explicit `sessions` open and close times (e.g. 10:00 to 17:00).

---

### `tickerforge-py`

#### [MODIFY] `tickerforge/models.py`
* Define a new `EquitySpec(BaseModel)` class to model the loaded equities, including the `sessions` field.

#### [MODIFY] `tickerforge/spec_loader.py`
* Add `equities: dict[str, EquitySpec]` to `SpecRepository`.
* Implement a new private function `_load_equities(spec_root: Path) -> list[EquitySpec]`.
* Update `load_spec()` to iterate through files in `spec/equities/`, loading them into the `SpecRepository`.

#### [NEW] `tests/test_equities.py`
* Implement Python unit tests validating that the equities load correctly, parsing a mock equity YAML and asserting session correctness to maintain >80% code coverage.

---

### `tickerforge-rs`

#### [MODIFY] `tickerforge-rs/src/models.rs`
* Add an `EquitySpec` struct that mirrors the Python implementation.
* Add `pub equities: HashMap<String, EquitySpec>` to `SpecRepository`.
* Add `ParsedEquityTicker` struct and add `Equity(ParsedEquityTicker)` variant to `AnyParsedTicker`.

#### [MODIFY] `tickerforge-rs/src/spec_loader.rs`
* Implement `load_equities` function to read from `spec/equities/**/*.yaml` and populate `SpecRepository.equities`.

#### [MODIFY] `tickerforge-rs/src/ticker_parser.rs`
* Update `parse_any_inner` to also match against `SpecRepository.equities` before falling back to returning an error. If the ticker is found in `equities`, it will return `AnyParsedTicker::Equity`.

## Verification Plan

### Automated Tests
* Run `pytest` with coverage in `tickerforge-py` to ensure unit tests maintain >= 80% coverage.
* Run `cargo test` in `tickerforge-rs` to verify Rust implementation compiles and accurately loads/parses equities.

### Manual Verification
* Execute a Python and Rust script attempting to parse `"PETR4"` and print its sessions.
