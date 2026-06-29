# Offset Tag Syntax `SYMBOL[n]`

## Summary

Both the Python (`tickerforge-py`) and Rust (`tickerforge-rs`) implementations support an **offset tag** syntax for futures: a root symbol followed by a bracketed integer, e.g. `DOL[1]`, `WIN[2]`, `IND[-1]`.

The tag selects the *nth* contract from the tradeable-contract list for that root — forward (positive `n`), the front month itself (`0`), or backward into already-expired contracts (negative `n`). It is a parsing/generation-layer feature that relies on the contract data already defined in this spec (symbol, `ticker_format`, `contract_cycle`, expiration rule) and requires **no new YAML fields and no schema changes**. Every futures contract in the spec supports it automatically.

## Syntax

```
ROOT[n]
```

- `ROOT` — a futures root symbol defined in `spec/contracts/<exchange>/futures.yaml` (e.g. `DOL`, `WIN`, `IND`, `WDO`, `DI1`, `BGI`).
- `n` — a signed integer offset. May be omitted entirely (plain `ROOT` is equivalent to `ROOT[0]`).

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

### Forward list (n >= 0)

The forward list is the set of `(year, month)` pairs from `as_of.year .. as_of.year + 4` whose contract is **still tradeable** on the reference date, ordered ascending. `n` indexes this list. "Still tradeable" follows the contract's existing expiration rule:

- `DOL` / `WDO` are tradeable while `as_of < expiration`.
- Other contracts (e.g. `WIN`, `IND`, `DI1`) are tradeable while `as_of <= expiration`.

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
