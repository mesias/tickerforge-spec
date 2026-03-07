# Add CME Exchange Support

**Repository:** https://github.com/mesias/tickerforge-spec

## Goal

Add support for the CME (Chicago Mercantile Exchange).

Follow the existing structure and conventions already used for B3.
Do not change the existing schema unless absolutely necessary.

## Tasks

### 1. Create a new exchange definition

File: `exchanges/cme.yaml`

Fields should follow the same structure used in `exchanges/b3.yaml`.

Exchange metadata:

- exchange: CME
- full_name: Chicago Mercantile Exchange
- country: US
- timezone: America/Chicago

### 2. Define core CME futures assets

Include some of the most important CME futures contracts:

**Equity index futures:**
- ES - S&P 500
- NQ - Nasdaq 100
- RTY - Russell 2000

**Interest rate futures:**
- ZN - 10-Year Treasury Note
- ZF - 5-Year Treasury Note

**Commodities:**
- CL - Crude Oil
- GC - Gold

**FX:**
- 6E - Euro FX
- 6J - Japanese Yen

Each asset must include: type, category, description, trading_hours.

Follow the same style used in B3.

### 3. Contracts specification

Create contract definitions in: `contracts/cme/futures.yaml`

If possible reuse existing contract_cycles and expiration_rules.

Only create new ones if CME requires different conventions.

Typical CME futures cycle: quarterly (H, M, U, Z).

### 4. If new expiration rules are needed

Add them to `schemas/contract_cycles.yaml`.

But avoid duplication if existing rules can be reused.

### 5. Tests

Create basic validation tests in `tests/cme/`.

Tests should confirm:
- contract cycles exist
- expiration rules exist
- assets reference valid cycles

## Constraints

- Follow KISS
- Reuse existing conventions
- Keep YAML human-readable
- Do not invent unnecessary fields
- Keep consistency with B3 files

Output only the new files and modifications.
