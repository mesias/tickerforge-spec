# TickerForge Spec

[![CI](https://github.com/mesias/tickerforge-spec/actions/workflows/ci.yml/badge.svg)](https://github.com/mesias/tickerforge-spec/actions/workflows/ci.yml)

**TickerForge Spec** is the canonical specification and shared dataset used by TickerForge implementations across different programming languages.

The repository defines exchange metadata, contract rules, and test cases used to resolve financial asset tickers and derivatives contracts (futures and options).

It serves as the **source of truth** for all implementations of the TickerForge ecosystem.

---

# Purpose

Different languages may implement their own versions of TickerForge (Python, Rust, Go, etc.).

This repository ensures that all implementations share:

* The same exchange metadata
* The same contract rules (futures and options)
* The same symbol resolution logic
* The same validation test cases

This guarantees **consistent behavior across languages**.

---

# Repository Structure

```
tickerforge-spec/

VERSION

spec/
  exchanges/
    b3.yaml
    cme.yaml
  contracts/
    b3/
      futures.yaml
      options.yaml
    cme/
      futures.yaml
  tests/
    b3/
      futures_resolve.csv
      options_resolve.csv
      B3_2023_2028_WIN_IND_DOL_calendar_FIXED.csv.xz
    cme/
      futures_resolve.csv
  schemas/
    contract_cycles.yaml
    exchange_schema.yaml
    contracts_schema.yaml
    options_schema.yaml

pyproject.toml
tickerforge_spec_data/
  __init__.py

rust/
  Cargo.toml
  src/lib.rs

scripts/
  check_versions.py
```

The B3 multi-year calendar golden file is kept only as **`B3_2023_2028_WIN_IND_DOL_calendar_FIXED.csv.xz`** (semicolon-separated CSV, lzma-compressed)—no uncompressed twin is required in the repo.

---

# Exchanges Metadata

Exchange files define static information such as:

* timezone
* trading hours
* supported assets and product categories
* exchange identifiers

Example:

```yaml
exchange: B3
timezone: America/Sao_Paulo

assets:
  WIN:
    type: future
    category: index
    description: Mini Ibovespa Futures
    trading_hours:
      start: "09:00"
      end: "18:25"

  EQUITY_OPTIONS:
    type: option
    category: equity_option
    description: Options on listed equities (PETR4, VALE3, ...)
    trading_hours:
      start: "10:00"
      end: "18:25"
```

---

# Contract Rules — Futures

Futures contract rules describe how derivatives contracts are generated and resolved.

Each contract defines its cycle (which months it trades in) and an expiration rule.

Supported expiration rule types:

* `nearest_weekday_to_day` — closest weekday to a calendar day (e.g. WIN/IND: nearest Wednesday to the 15th)
* `first_business_day` — first business day of the contract month (e.g. DOL, WDO, DI1)
* `last_business_day` — last business day of the contract month (e.g. BGI)
* `fixed_day` — specific calendar day, next business day if holiday (e.g. CCM: 15th)
* `schedule` — dates vary per contract; consult exchange maturity calendar (e.g. ICF, CL, GC)

Example:

```yaml
contracts:
  - symbol: DOL
    exchange: B3
    ticker_format: "{symbol}{month_code}{yy}"
    contract_cycle:
      - F   # January
      - G   # February
      # ... all 12 months
    expiration_rule:
      type: first_business_day
```

These rules allow implementations to determine:

* front-month contracts
* expiration dates
* contract offsets

---

# Contract Rules — Options

Options contract rules describe how option tickers are resolved.

B3 has four categories of options, each with distinct ticker formats:

**Equity options** use a compact format where one letter encodes both the option type (call/put) and the expiration month:

* Calls: A (Jan) through L (Dec)
* Puts: M (Jan) through X (Dec)
* Ticker format: `{root}{month_code}{strike}` — e.g. `PETRA35` = Petrobras call, January, strike 35

**Index, dollar, and rate options** use futures-style month codes with an explicit call/put indicator:

* Ticker format: `{symbol}{month_code}{yy}{C|P}{strike}` — e.g. `DOLF26C005200`

Example:

```yaml
options:
  - type: equity
    exchange: B3
    option_style: american
    ticker_format: "{root}{month_code}{strike}"
    call_month_codes: [A, B, C, D, E, F, G, H, I, J, K, L]
    put_month_codes: [M, N, O, P, Q, R, S, T, U, V, W, X]
    expiration_rule:
      type: nth_weekday
      weekday: friday
      nth: 3
    underlyings:
      - PETR4
      - VALE3
```

---

# Shared Test Cases

Test cases ensure that all implementations produce identical results.

Test files use CSV format for easy maintenance and universal parsing.

**Futures** (`spec/tests/<exchange>/futures_resolve.csv`):

Columns: `symbol,date,offset,expected,comment`

```csv
symbol,date,offset,expected,comment
WIN,2026-06-01,0,WINM26,before June expiry (Jun 17) front month is June
DOL,2026-04-02,0,DOLK26,after Apr 1 expiry rolls to May
BGI,2026-06-01,0,BGIM26,after May expiry (May 29) front month is June
```

**Options** (`spec/tests/<exchange>/options_resolve.csv`):

Columns: `type,underlying,date,option_type,strike,offset,expected,comment`

```csv
type,underlying,date,option_type,strike,offset,expected,comment
equity,PETR4,2026-01-16,call,35,0,PETRA35,January call strike 35
equity,PETR4,2026-01-16,put,35,0,PETRM35,January put strike 35
dollar,DOL,2026-03-15,call,5200,0,DOLH26C005200,March call strike 5200
```

Implementations must load these tests and verify their resolver against them.

---

# Implementations

TickerForge implementations may exist in multiple languages.

Examples:

* tickerforge (Python)
* tickerforge-rs (Rust)
* tickerforge-go (Go)

All implementations should rely on this specification.

---

# Versioning and Releases

This repository uses a shared root `VERSION` file as release authority.

- Tag format: `vX.Y.Z`
- Python package (`tickerforge-spec-data` in root `pyproject.toml`) version must match `VERSION`
- Root `Cargo.toml` (published Rust crate) must match `VERSION`
- The `rust/` subdirectory crate is `publish = false` (CI/local `cargo check` only); its `version` is not kept in sync with releases

Release sequence:

1. Update `VERSION` and the `version` field in `pyproject.toml` and root `Cargo.toml`
2. Run `python scripts/check_versions.py`
3. Commit and tag `vX.Y.Z`
4. GitHub Actions `release.yml` publishes the Python wheel/sdist to PyPI (spec files are bundled at build time; there is no duplicate `spec/` copy in git)

---

# Design Principles

TickerForge Spec follows several principles:

* **Deterministic** — no dependency on external APIs
* **Exchange-aware** — rules are defined per exchange
* **Language-neutral** — YAML and CSV datasets usable by any language
* **Test-driven** — shared test cases ensure consistent behavior

---

# Contributing

Contributions are welcome.

Typical contributions include:

* new exchanges
* updated contract rules
* additional test cases
* corrections to metadata

Please ensure any change includes appropriate test cases.

---

# License

MIT License
