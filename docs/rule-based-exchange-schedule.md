# Rule-Based Exchange Schedule Specification

## Problem

Third-party calendar libraries are useful, but they are not the specification:

- They can disagree on edge-case holidays and special sessions.
- They may not model half-day or delayed-open sessions.
- Upgrading a dependency can silently change session behavior.
- They make cross-language parity harder to guarantee.

The canonical source of truth belongs in `tickerforge-spec`, not in language-specific calendar backends.

## Design

Instead of storing one date list per year, the spec stores a small set of recurring rules that consumers evaluate at runtime.

Supported rule families:

| Rule type       | Example                                 | Resolves to                                     |
| --------------- | --------------------------------------- | ----------------------------------------------- |
| `fixed`         | `{ month: 12, day: 25 }`                | Dec 25 every year                               |
| `easter_offset` | `{ offset: -47 }`                       | Carnival Tuesday (47 days before Easter Sunday) |
| `nth_weekday`   | `{ month: 1, weekday: monday, nth: 3 }` | MLK Day (3rd Monday of January)                 |
| `last_weekday`  | `{ month: 5, weekday: monday }`         | Memorial Day (last Monday of May)               |

Rules may include optional `from_year` and `to_year` bounds for conditional applicability.

One-off closures belong in `overrides` with explicit dates. The intent is to keep exceptional data minimal while making recurring exchange calendars deterministic and auditable.

## Spec Layout

Each exchange schedule lives under `spec/schedules/` and is validated by `spec/schemas/schedule_schema.yaml`.

```text
tickerforge-spec/
  spec/
    schedules/
      b3.yaml
      cme.yaml
    schemas/
      schedule_schema.yaml
```

## Schedule Shape

Example:

```yaml
exchange: B3
timezone: America/Sao_Paulo

holidays:
  fixed:
    - { month: 1, day: 1, name: "Confraternizacao Universal" }
    - { month: 12, day: 25, name: "Natal" }

  easter_offset:
    - { offset: -47, name: "Carnaval (terca-feira)" }
    - { offset: -2, name: "Sexta-feira Santa" }

  overrides:
    - { date: "2023-11-20", action: add, name: "Consciencia Negra" }

early_closes:
  easter_offset:
    - { offset: -46, name: "Quarta-feira de Cinzas", open: "13:00" }
```

Core fields:

- `exchange`: exchange identifier matching the rest of the spec
- `timezone`: IANA timezone name for schedule evaluation
- `holidays`: non-session rules
- `early_closes`: session rules that keep the date tradable but alter session timing

## Consumer Contract

For a given year, consumers should evaluate the schedule in this order:

1. Compute Easter Sunday for the year.
2. Materialize `holidays.fixed`, applying `from_year` and `to_year` filters when present.
3. Materialize `holidays.easter_offset`.
4. Materialize `holidays.nth_weekday`.
5. Materialize `holidays.last_weekday`.
6. Apply `overrides` in order.
7. Exclude weekend dates from holiday output.
8. Treat sessions as weekdays minus holidays.
9. Evaluate `early_closes` separately so those dates remain sessions with modified hours.

The spec defines the data contract and the evaluation semantics. It does not prescribe the internal class structure, cache strategy, or public API shape used by each implementation.

## Why This Lives In The Spec Repo

- It keeps exchange session logic deterministic and versioned with the canonical data.
- It gives every consumer the same input and the same expected behavior.
- It avoids per-year maintenance for recurring holiday patterns.
- It leaves room for implementation-specific adapters without making the spec repo language-aware.

Implementation notes belong in the consumer repositories. This document remains the language-neutral reference for `spec/schedules/*.yaml`.
