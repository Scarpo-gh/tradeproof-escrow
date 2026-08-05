# Circle Product Feedback

## Products used

- **USDC on Arc Testnet:** bounded test settlement budget for two synthetic invoice-escrow jobs.
- **Circle Developer-Controlled Wallets:** existing Arc Testnet wallets submitted named contract-execution calls to the predeployed ERC-8183 reference contract.

## Why we chose these products

TradeProof needs a dollar-denominated test settlement rail and a verifiable expiry/recovery path without handling a user wallet or real funds. Arc Testnet plus test-USDC made it possible to show a separate completion path and a separate refund path for a synthetic SME invoice workflow.

## What worked well

- Developer-Controlled Wallet contract execution returned a public transaction ID and Arc transaction hash for each named lifecycle step.
- Arc Testnet exposed a predictable, publicly verifiable transaction trail in Arcscan.
- The predeployed ERC-8183 reference contract allowed the prototype to demonstrate the lifecycle without deploying a custom escrow contract.

## What could be improved

- A minimal official SME invoice-escrow sample with `create → set budget → fund → delivery proof → complete/refund` would reduce time spent translating a generic job lifecycle into a trade-finance demonstration.
- A documented example for decoding the `JobCreated` event into the onchain job ID would make multi-step integrations easier to verify.

## Recommendation

Provide a small Circle/Arc reference demo that uses synthetic invoice and proof hashes, shows separate completion and expiry-refund jobs, and includes a ready-to-use evidence-bundle format for hackathon builders.
