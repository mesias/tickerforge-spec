# Create tickerforge-spec

**Repository:** https://github.com/mesias/tickerforge-spec

## Goal

Create a new GitHub project named **tickerforge-spec**.

This repository will act as the canonical specification and shared dataset for TickerForge implementations in multiple programming languages.

TickerForge resolves financial asset tickers and derivatives contracts (futures and options). This repository must contain metadata, contract rules, and shared test cases used by implementations such as tickerforge (Python), tickerforge-rs (Rust), and others.

The repository should be language-agnostic and rely on YAML files.

## Project Structure

```
tickerforge-spec/

README.md
LICENSE
.gitignore

exchanges/
  b3.yaml

contracts/
  futures.yaml

tests/
  futures_resolve.yaml

schemas/
  exchange.schema.yaml
  contracts.schema.yaml
```

## Requirements

1. Use YAML files for all metadata and rules.

2. Exchange files must define:
   - exchange name
   - timezone
   - trading hours
   - supported assets

3. Contract rule files must define:
   - symbol
   - exchange
   - contract cycle
   - expiration rule

4. Test files must define resolution cases using this format:

```yaml
cases:
  - input:
      symbol: WIN
      date: 2026-06-01
      offset: 0
    expected: WINM26
```

5. Include example data for:
   - B3 exchange
   - WIN futures contract

6. Provide JSON/YAML schemas to validate the structure of:
   - exchange metadata
   - contract rules

## Constraints

The goal is to make this repository the **source of truth for tickerforge implementations**.

Keep the project simple but well-structured so that other languages can easily consume the datasets.
