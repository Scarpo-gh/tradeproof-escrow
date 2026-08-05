# TradeProof Escrow

A testnet-only invoice-escrow workflow for the Ignyte Stablecoin Commerce Stack Challenge.

> **Prototype scope:** synthetic parties and invoices, Arc Testnet, and test-USDC only. It is not a production payment product, custody service, KYC/AML system, credit decision, or real-money settlement service.

## Status

The working prototype includes:

- deterministic canonical invoice hashing;
- fail-closed local escrow lifecycle (`DRAFT → FUNDED → COMPLETED` or `REFUNDED`);
- delivery-proof matching and expiry-refund guards;
- a local browser/API demo that never accepts a wallet or credential;
- separate, verified Arc Testnet completion and expiry-refund jobs using bounded test-USDC.

See the [Arc Testnet evidence bundle](docs/evidence/arc-testnet-2026-08-05/README.md), [architecture](docs/ARCHITECTURE.md), and [Circle product feedback](docs/CIRCLE_PRODUCT_FEEDBACK.md).

## Local checks

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pytest httpx
PYTHONPATH=src .venv/bin/python -m pytest -q
```

## Submission boundary

This is a separate Ignyte submission. It does not modify, replace, or resubmit the OutcomeRail / Encode hackathon project.
