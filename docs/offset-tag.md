# Offset Tag Syntax `SYMBOL[n]`

## Summary

Both the Python (`tickerforge-py`) and Rust (`tickerforge-rs`) implementations support an **offset tag** syntax for futures: a root symbol followed by a bracketed integer, e.g. `DOL[1]`, `WIN[2]`, `IND[-1]`.

The tag selects the *nth* contract from the tradeable-contract list for that root — forward (positive `n`), the front month itself (`0`), or backward into already-expired contracts (negative `n`). It is a parsing/generation-layer feature that relies on the contract data already defined in this spec (symbol, `ticker_format`, `contract_cycle`, expiration rule) and requires **no new YAML fields and no schema changes**. Every futures contract in the spec supports it automatically.

## Syntax

```
ROOT[n]
ROOT[n@roll]
ROOT[@roll]
```

- `ROOT` — a futures root symbol defined in `spec/contracts/<exchange>/futures.yaml` (e.g. `DOL`, `WIN`, `IND`, `WDO`, `DI1`, `BGI`).
- `n` — a signed integer offset. May be omitted entirely (plain `ROOT` is equivalent to `ROOT[0]`). If `@roll` is present and `n` is omitted, it defaults to `1` (the next contract).
- `@roll` — an optional condition tag indicating that the symbol is only valid on the last trading day of the expiring contract.

## Semantics

`n` is an **index into the tradeable-contract list**, not calendar-month arithmetic. For a given root and reference date, the implementation builds the ordered list of contracts that the root trades and indexes into it.

| Tag | Meaning |
|---|---|
| `ROOT` / `ROOT[0]` | Front month — the nearest still-tradeable contract. |
| `ROOT[1]` | The next tradeable contract after the front month. |
| `ROOT[2]` | Two contracts out. |
| `ROOT[-1]` | The most-recently-expired contract (the previous ticker that rolled off). |
| `ROOT[-2]` | The second most-recently-expired contract. |

`n = 0` and the plain root produce identical results. Out-of-range indices (e.g. `DOL[999]`, `DOL[-999]`) and unknown roots (e.g. `ZZZ[1]`) raise a `ValueError` (Python) or return an `Err` (Rust).

## Conditional Roll-Day Exception (`@roll`)

The `@roll` condition limits the parsing of the tag strictly to the **last trading day** (roll day) of the expiring front contract. On any other day, the notation is invalid and raises a parsing error.

- `SYMBOL[@roll]` / `SYMBOL[1@roll]` — next contract, valid only on the last trading day of the expiring contract.
- `SYMBOL[0@roll]` — current expiring contract, valid only on the last trading day.

### Roll Day Definitions
The roll day is computed dynamically based on the contract's expiration rules:
- **Currency Futures (DOL, WDO)**: These contracts roll off on their expiration day (the first business day of the contract month). The last trading day is therefore **1 business day before expiration**.
- **Index Futures (WIN, IND)**: These contracts remain tradeable through the expiration day. The last trading day is therefore **the expiration day itself**.

### Examples (DOL, around June/July 2026)
* **June 30, 2026** (Roll Day of July contract `DOLN26`):
  - `DOL[@roll]` resolves to `DOLQ26` (August contract)
  - `DOL[0@roll]` resolves to `DOLN26` (July contract)
* **June 29, 2026** (Non-Roll Day):
  - `DOL[@roll]` raises a `ValueError` / `Err`
  - `DOL[0@roll]` raises a `ValueError` / `Err`

## The `is_valid` flag
Parsed futures ticker objects contain a boolean flag (`is_valid`) indicating whether the parsed contract is currently tradeable/active in the market on the reference date.
- It is `true` if the contract has not yet expired (e.g., `DOLQ26` on July 1st, 2026).
- It is `false` if the contract has already expired (e.g., `DOLQ24` on July 1st, 2026).
- It is `null`/`None` if no reference date context is provided.


### Forward list (n >= 0)

The forward list is the set of `(year, month)` pairs from `as_of.year .. as_of.year + 4` whose contract is **still tradeable** on the reference date, ordered ascending. `n` indexes this list. "Still tradeable" follows the contract's existing expiration rule:

- `first_business_day` contracts (`DOL`, `WDO`, `DI1`) roll off on their last trading day (1 business day before expiration), so they are front-month eligible while `as_of < last_trading_day`.
- Other contracts (e.g. `WIN`, `IND`) remain tradeable through expiry day (`as_of <= expiration`).

### Expired list (n < 0)

For negative `n`, the implementation scans backward `as_of.year - 4 .. as_of.year`, collecting pairs that are **no longer tradeable** (`!still_tradeable`), ordered so the **most-recently-expired** contract is index `0`. `n = -1` selects `expired[0]`, `n = -2` selects `expired[1]`, and so on.

## Uniform across cycle types

The offset is an index into the *tradeable-contract list*, so it works the same way regardless of how often a contract trades:

- **Monthly** cycles (`DOL`, `WDO`, `DI1`) — `[1]` is the very next calendar month in the cycle.
- **Bimonthly** cycles (`WIN`, `IND` trade Feb / Apr / Jun / Aug / Oct / Dec) — `[1]` jumps to the **next cycle month**, not +1 calendar month. E.g. with `WIN` front month = June (`WINM26`), `WIN[1]` is August (`WINQ26`), not July.

No per-contract configuration is needed; the cycle is read from the existing `contract_cycle` field.

## Futures only

The bracket tag applies to **futures only**. Options already encode the full contract month in their ticker (e.g. `DOLF26C005200`, `PETRA35`), so there is no `DOLK26C5000[1]` form. Passing a bracket tag to an option root is not supported.

## No YAML / schema changes

This is a documented-only convention. The bracket syntax is resolved at parse/generation time from the existing contract metadata. There are:

- no new fields in `spec/contracts/**`,
- no changes to `spec/schemas/**`,
- no changes to `spec/exchanges/**`.

Every futures contract defined in the spec supports `SYMBOL[n]` automatically.

## Examples (B3 calendar, around 2026-06-29)

These examples are grounded in `spec/tests/b3/futures_resolve.csv`.

| Input | Reference date | Resolves to | Why |
|---|---|---|---|
| `DOL` / `DOL[0]` | 2026-06-29 | `DOLN26` | Front month is July (DOL trades every month; June expired on Jun 1). |
| `DOL[1]` | 2026-06-29 | `DOLQ26` | Next tradeable DOL contract after July is August. |
| `WIN` / `WIN[0]` | 2026-06-29 | `WINQ26` | After WIN June expiry (Jun 17), the front month rolls to August. |
| `WIN[1]` | 2026-06-29 | `WINV26` | Next bimonthly cycle month after August is October. |
| `IND[0]` | 2026-06-29 | `INDQ26` | IND shares WIN's bimonthly cycle; front month is August. |
| `IND[-1]` | 2026-06-29 | `INDM26` | Most-recently-expired IND contract — June, which rolled off on Jun 17. |

Contrast the bimonthly behavior: `WIN[1]` from an August front month lands on **October** (`WINV26`), skipping July and September, because WIN does not trade those months. A monthly contract like `DOL[1]` from July lands on the adjacent month, August (`DOLQ26`).

## Implementation references

Parsing and generation behavior is implemented in the language repos; this spec repository only **defines and documents** the convention.

- **Python**: `tickerforge-py/tickerforge/ticker_parser.py` (bracket parsing in `parse_ticker`), `tickerforge-py/tickerforge/ticker_generator.py` (`generate_ticker_for_contract` with signed offset).
- **Rust**: `tickerforge-rs/src/ticker_parser.rs` (`parse_tagged_root` in `parse_any_inner`), `tickerforge-rs/src/ticker_generator.rs` (`generate_ticker_for_contract_signed`).

See each project's `docs/offset-tag.md` for language-specific API details and usage examples.
