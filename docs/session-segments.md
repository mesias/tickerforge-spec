# Session Segments Specification

## Goal

Keep authoring simple in the YAML spec while giving consumers a deterministic, ordered session model.

## YAML Shape

Session windows are authored as a mapping keyed by segment name:

```yaml
sessions:
  regular:
    start: "09:00"
    end: "18:25"
```

Split sessions use additional keys in order:

```yaml
sessions:
  regular:
    start: "09:00"
    end: "12:00"
  afternoon:
    start: "13:00"
    end: "18:25"
```

This keeps the canonical YAML compact and readable without repeating the segment name inside each value object.

## Canonical Semantics

- Mapping keys are the segment names.
- Each value contains the time bounds for that segment.
- Consumers should preserve the YAML order.
- The first segment must be `regular`.
- Multiple segments represent ordered trading windows.
- Gaps between consecutive segments are implicit pauses in trading.

## Consumer Contract

Consumers may expose sessions using any internal data model, but the observable behavior should match these rules:

- A segment has `name`, `start`, and `end`.
- `name` is derived from the YAML key, not duplicated in the YAML value.
- Assets and merged contract views should preserve session order.
- Validation should reject session lists whose first segment is not `regular`.

## Schema Intent

In the canonical spec, `sessions` remains an object whose values contain `{ start, end }`.

That means:

- the spec stays language-neutral
- the schema reflects the authored YAML
- each consumer is free to convert the mapping into its preferred runtime representation

## Scope

This document defines the format and semantics of `sessions` in the spec.

Implementation details such as loader hooks, model types, or helper methods belong in consumer repositories rather than in `tickerforge-spec`.
