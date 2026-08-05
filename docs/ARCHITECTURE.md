# Architecture

## Scope

TradeProof Escrow is an educational Arc Testnet demonstration for a synthetic UAE-to-global SME invoice workflow. It does not custody user funds, connect a user wallet, make credit/KYC/AML decisions, or process a real invoice or payment.

## Flow

```text
Browser demo
  → FastAPI backend
    → canonical synthetic invoice JSON
      → SHA-256 invoice hash + delivery-proof hash
        → Arc Testnet ERC-8183 reference job
          → completion with a proof hash
          → or expiry followed by refund
```

## Components

| Component | Responsibility | Boundary |
|---|---|---|
| Browser UI | Collects synthetic invoice fields and displays the API response | Never accepts wallet credentials or private keys |
| FastAPI API | Validates invoice fields and makes a deterministic instruction hash | Stores demo jobs in memory only |
| Domain/state model | Guards state transitions and proof matching | No blockchain client or secret dependency |
| Arc preflight | Builds a public no-broadcast plan | Requires explicit execution confirmation before any client initialization |
| Circle execution adapter | Creates one named Arc Testnet contract call at a time | Loads the local credential file only after the execution guard passes |
| Arc reference contract | Provides the ERC-8183 test-USDC job lifecycle | Predeployed reference contract; no TradeProof contract deployment |

## Testnet evidence model

A tracked evidence bundle records a separate completion job and a separate expiry/refund job. Each entry includes only public transaction hashes, job IDs, canonical hashes, and Arcscan links. It excludes API keys, entity secrets, recovery material, private keys, wallet IDs, and raw credential files.
