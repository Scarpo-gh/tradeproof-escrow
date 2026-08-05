# Arc Testnet lifecycle evidence — 2026-08-05

All data in this bundle belongs to **TradeProof Escrow** and uses new, synthetic testnet jobs. It does not reuse OutcomeRail transactions or evidence.

- Network: Arc Testnet (`5042002`)
- Reference contract: [`0x0747…4583`](https://testnet.arcscan.app/address/0x0747EEf0706327138c69792bF28Cd525089e4583)
- Settlement amount per job: **1 test-USDC**

## A. Delivery proof → completion

Job **168870** binds the synthetic invoice hash and its delivery-proof hash. The chain lifecycle completed successfully.

| Action | Tx |
|---|---|
| Create | [`01f529…2ba4`](https://testnet.arcscan.app/tx/0x01f529e8f7dc54e2f3f468ba80efe23c11fddf4c6da188193245c4fab1c02ba4) |
| Fund | [`19393a…aff5`](https://testnet.arcscan.app/tx/0x19393a723b84370c8103149589ba9b0a902aef12fea638cbf66cc9b00037aff5) |
| Submit delivery proof | [`cfa9ae…5edd`](https://testnet.arcscan.app/tx/0xcfa9ae6190974801aeb029a12ff14d7da4c2c9c858fee2d46bed7bb4a5935edd) |
| Complete | [`793f99…a28b`](https://testnet.arcscan.app/tx/0x793f99fa68c20dbeb2e0cba9342f5d733d1b97ed9a693c1f8e87c470e83aa28b) |

The completion receipt has status `0x1` and includes the expected `JobCompleted` event for job `168870`.

## B. Expiry → refund

Separate job **168872** was funded, allowed to expire, and refunded.

| Action | Tx |
|---|---|
| Create | [`760799…88dd`](https://testnet.arcscan.app/tx/0x7607997856f678d99c9805e9890aee6944c78a91fc649ca94302a6ae44b988dd) |
| Fund | [`3a80b0…edd9`](https://testnet.arcscan.app/tx/0x3a80b0c6461bb88701cfc75d5df31d25c0bc98f21749e978e5118750822cedd9) |
| Claim refund after expiry | [`db33fe…1338`](https://testnet.arcscan.app/tx/0xdb33fefc16c1101101cf99ca2a11580e04d6bf9990b91fee966f461eb6d81338) |

The refund receipt has status `0x1` and includes the expected `Refunded` event for job `168872`.

See [`arc-lifecycle.json`](arc-lifecycle.json) for all 11 public transaction hashes, block numbers, hashes, and verification details.
