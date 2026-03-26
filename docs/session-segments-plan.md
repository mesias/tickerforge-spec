---
name: Session segments list
overview: Keep YAML `sessions` as a compact map keyed by band name; deserialize into ordered SessionSegment structs (name from key, start/end from value). Validate regular first; update Python/Rust models and loaders. b3/cme YAML shape largely unchanged.
todos:
  - id: spec-yaml-schema
    content: Tweak exchange_schema.yaml if needed; optional afternoon example in spec YAML
    status: pending
  - id: py-models-loader
    content: SessionSegment + list sessions; dict-to-list conversion; validation; merge
    status: pending
  - id: rust-models-loader
    content: SessionSegment + Vec; map deserialize or convert in loader; synthetic_contract
    status: pending
  - id: tests-docs
    content: Fix spec_loading tests; README note on sessions list + YAML map
    status: pending
isProject: false
---

# Session segments: YAML map, struct `name` from key

## YAML (authoring) — keep the readable map form

Spec files stay **easy to read** and **less verbose** than a list of `{name: ...}` blocks:

```yaml
sessions:
  regular:
    start: "09:00"
    end: "18:25"
```

Split day (multiple windows; pauses are implicit between bands):

```yaml
sessions:
  regular:
    start: "09:00"
    end: "12:00"
  afternoon:
    start: "13:00"
    end: "18:25"
```

**No wholesale rewrite** of [`b3.yaml`](../spec/exchanges/b3.yaml) / [`cme.yaml`](../spec/exchanges/cme.yaml) beyond optional documentation/example rows; the **shape is already** this map style today.

## Runtime model (Python / Rust)

- Introduce **`SessionSegment`** with **`name`**, **`start`**, **`end`**.
- **`Asset.sessions`** and **`ContractSpec.sessions`**: **`list[SessionSegment]`** / **`Vec<SessionSegment>`** (ordered).
- **`name`** is **not** duplicated in YAML: it is **the key** from the mapping (`regular`, `afternoon`, …) copied into the struct at load time.

## Ordering and validation

- **`regular` must be present** and must be the **first** segment in the ordered list.
- **List order for non-`regular` keys:** prefer **YAML mapping order** when the parser preserves it (Python `yaml.safe_load` with PyYAML keeps order; Rust: use order-preserving deserialization, e.g. `serde_yaml::Mapping` → iterate, or `indexmap::IndexMap`, or build `Vec` with rule: emit `regular` first if present, then remaining keys in stable order).
- **Semantics:** multiple segments = ordered windows; **implicit pauses** between `segments[i].end` and `segments[i+1].start`.

## JSON schema ([`exchange_schema.yaml`](../spec/schemas/exchange_schema.yaml))

- Keep **`sessions`** as an **object** whose values are `{ start, end }` (current schema intent).
- Optionally document that **keys** are session names and the first **must** be `regular` (machine validation in loaders).

## Python (`tickerforge-py/tickerforge/models.py` + `spec_loader.py`)

- Define `SessionSegment` and `sessions: list[SessionSegment]`.
- **Conversion:** `model_validator(mode="before")` on `Asset` (or normalize in `_load_exchanges` before `Asset(**)`): if `sessions` is a `dict`, convert to `[SessionSegment(name=k, **v) for k, v in ...]` preserving dict insertion order (PyYAML 3.7+).
- Validate first segment `name.lower() == "regular"`.
- Merge into `ContractSpec` copies the **list**.
- Helpers: `regular_session()` → `sessions[0]`; `regular_session_start_end()` unchanged in behavior.

## Rust (`tickerforge-rs/src/models.rs` + `spec_loader.rs`)

- `SessionSegment { name, start, end }`; `Vec<SessionSegment>` on `Asset` / `ContractSpec`.
- **Deserialize** `sessions` from YAML map: either **custom `Deserialize` for a newtype** wrapping conversion map→vec, or deserialize raw `serde_yaml::Value` / `Mapping` in `load_exchanges` and map keys to `SessionSegment` before constructing `Asset`.
- Post-merge validation: first segment name is `regular` (case-insensitive).
- `synthetic_contract`: `sessions: vec![]`.

## Tests / docs

- Update `spec_loading` tests in tickerforge-rs / tickerforge-py if assertions touched session shape.
- Short README note: YAML is a map; API exposes ordered `sessions` with `name` filled from keys.

No change to `TickerForge` / trading-symbol APIs beyond `ContractSpec.sessions` type change.
