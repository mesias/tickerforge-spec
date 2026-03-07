# TickerForge Spec

**TickerForge Spec** is the canonical specification and shared dataset used by TickerForge implementations across different programming languages.

The repository defines exchange metadata, contract rules, and test cases used to resolve financial asset tickers and derivatives contracts (such as futures and options).

It serves as the **source of truth** for all implementations of the TickerForge ecosystem.

---

# Purpose

Different languages may implement their own versions of TickerForge (Python, Rust, Go, etc.).

This repository ensures that all implementations share:

* The same exchange metadata
* The same contract rules
* The same symbol resolution logic
* The same validation test cases

This guarantees **consistent behavior across languages**.

---

# Repository Structure

```
tickerforge-spec/

exchanges/
  b3.yaml
  cme.yaml
  eurex.yaml

contracts/
  futures.yaml
  options.yaml

tests/
  futures_resolve.yaml
  options_resolve.yaml

schemas/
  exchange.schema.yaml
  contracts.schema.yaml
```

---

# Exchanges Metadata

Exchange files define static information such as:

* timezone
* trading hours
* supported assets
* exchange identifiers

Example:

```yaml
exchange: B3
timezone: America/Sao_Paulo

assets:
  WIN:
    type: future
    description: Mini Index Futures
    trading_hours:
      start: "09:00"
      end: "18:30"
```

---

# Contract Rules

Contract rules describe how derivatives contracts are generated and resolved.

Example:

```yaml
symbol: WIN
exchange: B3

contract_cycle:
  - G
  - J
  - M
  - Q
  - V
  - Z

expiration_rule: nearest_wednesday_15
```

These rules allow implementations to determine:

* front-month contracts
* expiration dates
* contract offsets

---

# Shared Test Cases

Test cases ensure that all implementations produce identical results.

Example:

```yaml
cases:
  - input:
      symbol: WIN
      date: 2026-06-01
      offset: 0
    expected: WINM26

  - input:
      symbol: WIN
      date: 2026-06-01
      offset: 1
    expected: WINQ26
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

# Design Principles

TickerForge Spec follows several principles:

* **Deterministic** — no dependency on external APIs
* **Exchange-aware** — rules are defined per exchange
* **Language-neutral** — YAML datasets usable by any language
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
