# TradeProof Escrow

A testnet-only invoice-escrow workflow for the Ignyte Stablecoin Commerce Stack Challenge.

> **Prototype scope:** synthetic parties and invoices, Arc Testnet, and test-USDC only. It is not a production payment product, custody service, KYC/AML system, credit decision, or real-money settlement service.

## Status

The initial domain layer is implemented and tested:

- deterministic canonical invoice hashing;
- fail-closed local escrow lifecycle (`DRAFT → FUNDED → COMPLETED` or `REFUNDED`);
- delivery-proof matching and expiry-refund guards.

The frontend, backend deployment, and separately verified Arc Testnet evidence are in progress.

## Local checks

```bash
PYTHONPATH=src pytest -q
```

## Submission boundary

This is a separate Ignyte submission. It does not modify, replace, or resubmit the OutcomeRail / Encode hackathon project.
