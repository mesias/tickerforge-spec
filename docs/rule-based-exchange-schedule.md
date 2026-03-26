# Rule-Based Exchange Schedule Spec

## Problem

Both implementations delegate session detection to third-party backends (`exchange_calendars` BVMF in Python, `bdays` BrazilExchange in Rust). These backends:

- Disagree with each other on edge-case holidays (Dec 24/31, Black Consciousness Day, Corpus Christi)
- Cannot represent half-day sessions (Ash Wednesday opens at 13:00)
- Are version-pinned: a library upgrade can silently change which days are sessions
- Force FX futures (DOL, WDO, DI1) to be excluded from Rust tests due to calendar mismatches

The `sessions` field in `exchanges/*.yaml` is parsed but never used for logic.

## Design: Rules, Not Dates

B3 holidays follow a small set of **repeating patterns**. Instead of listing every date for every year, the spec defines **rules** that both implementations evaluate at runtime:

| Rule type       | Example                                 | Resolves to                                     |
| --------------- | --------------------------------------- | ----------------------------------------------- |
| `fixed`         | `{ month: 12, day: 25 }`                | Dec 25 every year                               |
| `easter_offset` | `{ offset: -47 }`                       | Carnival Tuesday (47 days before Easter Sunday) |
| `nth_weekday`   | `{ month: 1, weekday: monday, nth: 3 }` | MLK Day (3rd Monday of January)                 |
| `last_weekday`  | `{ month: 5, weekday: monday }`         | Memorial Day (last Monday of May)               |

Each rule supports optional `from_year` / `to_year` for conditional applicability (e.g., Black Consciousness Day becoming a national holiday).

Genuine one-off exceptions (e.g., emergency closures) go in a minimal `overrides` list with explicit dates -- but the vast majority of holidays need zero per-year maintenance.

## Spec Structure

One YAML file per exchange under `spec/schedules/`:

```
tickerforge-spec/
  spec/
    schedules/
      b3.yaml
      cme.yaml
    schemas/
      schedule_schema.yaml
```

### spec/schedules/b3.yaml -- B3

```yaml
exchange: B3
timezone: America/Sao_Paulo

holidays:
  fixed:
    - { month: 1, day: 1, name: "Confraternização Universal" }
    - { month: 4, day: 21, name: "Tiradentes" }
    - { month: 5, day: 1, name: "Dia do Trabalho" }
    - { month: 9, day: 7, name: "Independência do Brasil" }
    - { month: 10, day: 12, name: "Nossa Senhora Aparecida" }
    - { month: 11, day: 2, name: "Finados" }
    - { month: 11, day: 15, name: "Proclamação da República" }
    - { month: 11, day: 20, name: "Consciência Negra", from_year: 2024 }
    - { month: 12, day: 24, name: "Véspera de Natal" }
    - { month: 12, day: 25, name: "Natal" }
    - { month: 12, day: 31, name: "Véspera de Ano Novo" }

  easter_offset:
    - { offset: -48, name: "Carnaval (segunda-feira)" }
    - { offset: -47, name: "Carnaval (terça-feira)" }
    - { offset: -2, name: "Sexta-feira Santa" }
    - { offset: 60, name: "Corpus Christi" }

  overrides:
    - { date: "2023-11-20", action: add, name: "Consciência Negra" }

early_closes:
  easter_offset:
    - { offset: -46, name: "Quarta-feira de Cinzas", open: "13:00" }
```

### spec/schedules/cme.yaml -- CME

```yaml
exchange: CME
timezone: America/Chicago

holidays:
  fixed:
    - { month: 1, day: 1, name: "New Year's Day" }
    - { month: 7, day: 4, name: "Independence Day" }
    - { month: 12, day: 25, name: "Christmas Day" }

  nth_weekday:
    - { month: 1, weekday: monday, nth: 3, name: "Martin Luther King Jr. Day" }
    - { month: 2, weekday: monday, nth: 3, name: "Presidents' Day" }
    - { month: 9, weekday: monday, nth: 1, name: "Labor Day" }
    - { month: 11, weekday: thursday, nth: 4, name: "Thanksgiving Day" }

  last_weekday:
    - { month: 5, weekday: monday, name: "Memorial Day" }

  easter_offset:
    - { offset: -2, name: "Good Friday" }
```

## How Implementations Resolve Holidays

For a given year:

1. Compute Easter Sunday for the year (Computus algorithm)
2. For each rule in `holidays.fixed`: skip if year < `from_year` or year > `to_year`, emit `date(year, month, day)`
3. For each rule in `holidays.easter_offset`: emit `easter_sunday + offset` days
4. For each rule in `holidays.nth_weekday`: emit nth occurrence of weekday in month
5. For each rule in `holidays.last_weekday`: emit last occurrence of weekday in month
6. Apply overrides: `action: add` inserts the date, `action: remove` deletes it
7. Filter out weekends (already non-sessions)
8. Result: set of holiday dates for that year
9. Sessions = weekdays - holidays

Both Python and Rust execute the exact same algorithm against the exact same YAML, producing identical session sets.

## Implementation Details

### tickerforge-py

- **`tickerforge/schedule.py`**: `ExchangeSchedule` loads rules, evaluates via `dateutil.easter.easter(year)`, caches per-year. `SpecCalendar` wraps it to match the `exchange_calendars` interface (`sessions_in_range`, `first_session`, `last_session`).
- **`tickerforge/calendars.py`**: `get_calendar()` returns `SpecCalendar` when a schedule YAML exists; falls back to `exchange_calendars` otherwise.
- **`tickerforge/spec_loader.py`**: `load_spec()` discovers `spec/schedules/*.yaml` and registers them via `register_schedules()`.

### tickerforge-rs

- **`src/schedule.rs`**: `ExchangeSchedule` with Computus Easter (~15 lines), `holidays_for_year() -> BTreeSet<NaiveDate>`, `is_session()`, `sessions_in_range()`.
- **`src/calendars.rs`**: `ExchangeCalendar` has a dual backend (`CalendarBackend::Spec` or `CalendarBackend::Bdays`); `register_schedules()` + preference for spec-driven schedules.
- **`src/spec_loader.rs`**: `load_spec()` discovers and registers schedule YAMLs.

### No changes required to expiration_rules

Both `expiration_rules.py` and `expiration_rules.rs` operate on `calendar.sessions_in_range` -- swapping the calendar backend is transparent.

## Why This Is Better

- **Zero per-year maintenance**: Adding a new year requires no YAML changes (unless an exchange creates a new holiday)
- **Both languages produce identical results**: Same rules, same algorithm, same output
- **Easy to verify**: `holidays_for_year(2026)` can be unit-tested against official exchange circulars
- **Extensible**: Adding a new exchange is one YAML file with ~10-20 rules
- **`overrides` covers edge cases**: Emergency closures or one-off exceptions still supported without polluting the rule set
