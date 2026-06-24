# Implementation Plan: TickerForge Specification and Parser Updates for B3 Assets

Rename `contract_multiplier` to `contract_standard` (with library field `ctr_std` mapping to the parsed ticker's `ctr_std`) and introduce `contract_size` (with library field `ctr_size`) across all specifications and implementations. Additionally, update the `multi-clever-trader` configuration parser to populate the system's `tam_lote_min` / `lot_size` from the contract's `ctr_size` field.

## User Review Required

> [!IMPORTANT]
> - `contract_multiplier` will be completely renamed to `contract_standard` in the YAML specification files.
> - The parser library classes (`ContractSpec`, `OptionSpec`, `EquitySpec`) in both Python and Rust will expose:
>   * `ctr_std` as an **integer** (int in Python / u32 in Rust, mapped from `contract_standard`).
>   * `ctr_size` as a **float / f64** (mapped from `contract_size`).
> - The parsed ticker models (e.g. `ParsedTicker` / `ParsedFuturesTicker`) will replace the old `lot_size` field with `ctr_std` as an **integer** (int in Python / u32 in Rust). No type conversions will be applied.
> - In `multi-clever-trader`, the system's loaded config fields `tam_lote_min` and `lot_size` will be populated from the contract spec's `ctr_size` (which is a float / f64).

## Proposed Changes

### TickerForge Specification (`tickerforge-spec`)

#### [MODIFY] [contracts_schema.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/schemas/contracts_schema.yaml)
- Add `contract_standard` (integer type) and `contract_size` (number type) to the contracts item schema properties list.
- Rename references of `contract_multiplier` to `contract_standard`.

#### [MODIFY] [options_schema.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/schemas/options_schema.yaml)
- Rename `contract_multiplier` to `contract_standard` (integer type) in properties.

#### [MODIFY] [equities_schema.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/schemas/equities_schema.yaml)
- Rename `contract_multiplier` to `contract_standard` (integer type) in properties.

#### [MODIFY] [futures.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/contracts/b3/futures.yaml)
- Rename `contract_multiplier` to `contract_standard` for all contracts.
- Complete the B3 specs with proper `contract_size` (float) and `contract_standard` (integer) values:
  * `WIN`: `contract_size: 0.20`, `contract_standard: 1`
  * `IND`: `contract_size: 1.00`, `contract_standard: 5`
  * `ISP`: `contract_size: 50.00`, `contract_standard: 1`
  * `WSP`: `contract_size: 2.50`, `contract_standard: 1`
  * `WDO`: `contract_size: 10000.00`, `contract_standard: 1`
  * `DI1`: `contract_size: 100000.00`, `contract_standard: 1`
  * `BGI`: `contract_size: 330.00`, `contract_standard: 1`
  * `CCM`: `contract_size: 450.00`, `contract_standard: 1`
  * `ICF`: `contract_size: 100.00`, `contract_standard: 1`
  * `ETH`: `contract_size: 10.00`, `contract_standard: 1`
  * `ETR`: `contract_size: 0.1`, `contract_standard: 1`
  * `SOL`: `contract_size: 5.00`, `contract_standard: 5`
  * `BIT`: `contract_size: 0.01`, `contract_standard: 1`
  * `SJC`: `contract_size: 450.00`, `contract_standard: 1`
  * `SOY`: `contract_size: 34.00`, `contract_standard: 1`
  * `GLD`: `contract_size: 1.00`, `contract_standard: 1`

#### [MODIFY] [options.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/contracts/b3/options.yaml)
- Rename `contract_multiplier` to `contract_standard` for all option rules, setting them as integers (e.g. `100`, `1`, `5`).

#### [MODIFY] [b3.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/equities/b3.yaml)
- Rename `contract_multiplier` to `contract_standard` for all cash equities, setting them as integers (e.g. `100`).

---

### Python TickerForge (`tickerforge-py`)

#### [MODIFY] [models.py](file:///home/amesias/Dev/tickerforge/tickerforge-py/tickerforge/models.py)
- In `ContractSpec`, `OptionSpec`, and `EquitySpec` models:
  - Rename `lot_size` field (and its alias `contract_multiplier`) to `ctr_std` as an **integer** (`ctr_std: int | None = Field(None, alias="contract_standard")`).
  - Add new field `ctr_size` as a **float** (`ctr_size: float | None = Field(None, alias="contract_size")`).

#### [MODIFY] [ticker_parser.py](file:///home/amesias/Dev/tickerforge/tickerforge-py/tickerforge/ticker_parser.py)
- In `ParsedTicker`:
  - Rename the `lot_size: float` field to `ctr_std: int`.
  - Add `ctr_size: float | None = None`.
- In `_match_futures` and `_match_options`:
  - Populate `ctr_std=contract.ctr_std` (which is an `int`).
  - Populate `ctr_size=contract.ctr_size`.

#### [MODIFY] [test_ticker_parsing.py](file:///home/amesias/Dev/tickerforge/tickerforge-py/tests/test_ticker_parsing.py)
- Update lot size assertions in the test suite to assert the new `ctr_std` integer values (e.g. `parsed_bit.ctr_std == 1` since `ctr_std` is `1`).

---

### Rust TickerForge (`tickerforge-rs`)

#### [MODIFY] [models.rs](file:///home/amesias/Dev/tickerforge/tickerforge-rs/src/models.rs)
- Update `ContractSpec` and `EquitySpec` structs:
  - Add `pub ctr_std: Option<u32>` (aliased to `contract_standard`).
  - Add `pub ctr_size: Option<f64>` (aliased to `contract_size`).
  - Remove references/fields related to `lot_size` / `contract_multiplier`.
- Update `ParsedFuturesTicker` and `ParsedEquityTicker`:
  - Rename `lot_size` to `ctr_std` with type `Option<u32>`.
  - Add `ctr_size: Option<f64>`.

#### [MODIFY] [options_models.rs](file:///home/amesias/Dev/tickerforge/tickerforge-rs/src/options_models.rs)
- Update `OptionSpec` struct:
  - Add `pub ctr_std: Option<u32>` (aliased to `contract_standard`).
  - Add `pub ctr_size: Option<f64>` (aliased to `contract_size`).
- Update `ParsedOptionTicker`:
  - Rename `lot_size` to `ctr_std` with type `Option<u32>`.
  - Add `ctr_size: Option<f64>`.

#### [MODIFY] [ticker_parser.rs](file:///home/amesias/Dev/tickerforge/tickerforge-rs/src/ticker_parser.rs)
- In `_match_futures` and `_match_options`, populate `ctr_std: contract.ctr_std` and `ctr_size: contract.ctr_size`.

#### [MODIFY] [ticker_parsing.rs](file:///home/amesias/Dev/tickerforge/tickerforge-rs/tests/ticker_parsing.rs)
- Update expected `lot_size` assertions to check `ctr_std` as `Some(1)` (or other integer values).

---

### Multi-Clever-Trader (`multi-clever-trader`)

#### [MODIFY] [trader_config_yaml.py](file:///home/amesias/Dev/trader/multi-clever-trader/common/config_parser/trader_config_yaml.py)
- In `_apply_tickerforge_specs`, load `lot` from `ctr_size` (float) instead of `lot_size` (or fallback to it if `ctr_size` is not present).

---

## Verification Plan

### Automated Tests
- Run the full pytest suite in `tickerforge-py`:
  ```bash
  pytest tests/
  ```
- Ask the user to run Rust tests in `tickerforge-rs`:
  ```bash
  cargo test
  ```
