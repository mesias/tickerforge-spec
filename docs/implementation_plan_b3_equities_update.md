# Implementation Plan: Update B3 Equities Specification

This document outlines the changes required to update the B3 cash equities specification in the next version of `tickerforge-spec`. The updates resolve bugs/typos, update legacy tickers affected by mergers and corporate actions, and expand the list of covered equities to include missing highly liquid B3 (Ibovespa) constituents.

---

## Proposed Changes

All edits will target the [b3.yaml](file:///home/amesias/Dev/tickerforge/tickerforge-spec/spec/equities/b3.yaml) specification file.

### 1. Typos and Structural Bugs

* **Correct `SBSP3` (Sabesp)**:
  * Currently, Sabesp is incorrectly defined as `SABP11` (which is actually a debenture that matured in Feb 2025).
  * **Change**: Rename the symbol `SABP11` to `SBSP3` and correct its description.

* **Add `MGLU3` (Magazine Luiza)**:
  * Currently, `MGLU3` is declared as an option underlying in `options.yaml` but is completely missing from `b3.yaml`.
  * **Change**: Add the definition for `MGLU3`.

### 2. Corporate Actions & Mergers

* **Update `BRFS3` to `MBRF3` (MBRF Global Foods)**:
  * Following the merger of Marfrig (`MRFG3`) and BRF (`BRFS3`) in September 2025, `BRFS3` is no longer active.
  * **Change**: Replace `BRFS3` with the new ticker `MBRF3` and update the description.

* **Update `NTCO3` to `NATU3` (Natura Cosméticos)**:
  * Following the corporate simplification in mid-2025, Natura's ticker was changed from `NTCO3` back to its original ticker `NATU3`.
  * **Change**: Replace `NTCO3` with `NATU3` and update the description.

* **Update `CCRO3` to `MOTV3` (Motiva)**:
  * CCR S.A. rebranded to Motiva and changed its ticker to `MOTV3` in May 2025.
  * **Change**: Replace `CCRO3` with `MOTV3` and update the description.

* **Add `BRAV3` (Brava Energia)**:
  * Formed by the merger of 3R Petroleum (`RRRP3`) and Enauta (`ENAT3`).
  * **Change**: Add `BRAV3` to the specification.

* **Add `AZZA3` (Azzas 2154)**:
  * Formed by the merger of Arezzo (`ARZZ3`) and Grupo Soma (`SOMA3`).
  * **Change**: Add `AZZA3` to the specification.

### 3. Add Common Share Classes
For major companies where both preferred (PN) and common (ON) shares are highly traded, add the ON class (the PN class is already defined).
* **Add `PETR3`** (Petrobras Ordinary Shares)
* **Add `BBDC3`** (Bradesco Ordinary Shares)

### 4. Add Missing Liquid B3 (Ibovespa) Constituents
Add the following 34 highly liquid equities currently missing from the specification:
* `VBBR3`, `RDOR3`, `DIRR3`, `USIM5`, `CURY3`, `COGN3`, `ENGI11`, `PSSA3`, `SMFT3`, `HYPE3`, `VIVA3`, `AURE3`, `GOAU4`, `CEAB3`, `ALOS3`, `POMO4`, `PCAR3`, `YDUQ3`, `RECV3`, `BEEF3`, `TAEE11`, `MRVE3`, `CXSE3`, `CMIN3`, `CPFE3`, `ISAE4` (formerly `TRPL4`), `IRBR3`, `CVCB3`, `BRAP4`, `RAIZ4`, `IGTI11`, `BRKM5`, `FLRY3`, `SLCE3`.

---

## Detailed Specifications to Add

The new entries will utilize the standard B3 trading session hours (10:00 to 17:00 America/Sao_Paulo):

```yaml
# Examples of new entries to be appended to spec/equities/b3.yaml

  - symbol: SBSP3
    exchange: B3
    type: equity
    description: Cia de Saneamento Basico do Estado de Sao Paulo Ordinary Shares
    currency: BRL
    tick_size: 0.01
    contract_multiplier: 100.00
    sessions:
      regular:
        start: "10:00"
        end: "17:00"

  - symbol: MGLU3
    exchange: B3
    type: equity
    description: Magazine Luiza SA Ordinary Shares
    currency: BRL
    tick_size: 0.01
    contract_multiplier: 100.00
    sessions:
      regular:
        start: "10:00"
        end: "17:00"

  - symbol: MBRF3
    exchange: B3
    type: equity
    description: MBRF Global Foods Company SA Ordinary Shares
    currency: BRL
    tick_size: 0.01
    contract_multiplier: 100.00
    sessions:
      regular:
        start: "10:00"
        end: "17:00"

  - symbol: NATU3
    exchange: B3
    type: equity
    description: Natura Cosmeticos SA Ordinary Shares
    currency: BRL
    tick_size: 0.01
    contract_multiplier: 100.00
    sessions:
      regular:
        start: "10:00"
        end: "17:00"

  - symbol: MOTV3
    exchange: B3
    type: equity
    description: Motiva Infraestrutura de Mobilidade SA Ordinary Shares
    currency: BRL
    tick_size: 0.01
    contract_multiplier: 100.00
    sessions:
      regular:
        start: "10:00"
        end: "17:00"
```

---

## Verification and Testing Plan

To ensure all new entries are valid and do not cause parsing regressions:

1. **Pre-commit Validation**:
   * Run the pre-commit checks or YAML linter if configured:
     ```bash
     pre-commit run --all-files
     ```

2. **Python Spec Verification**:
   * Execute Python unit tests in `tickerforge-py` to ensure the newly added equities parse correctly and adhere to the schema:
     ```bash
     pytest tests/
     ```

3. **Rust Spec Verification**:
   * Run cargo test in `tickerforge-rs` to ensure the specification is successfully parsed and integrated into the Rust binary:
     ```bash
     cargo test
     ```
