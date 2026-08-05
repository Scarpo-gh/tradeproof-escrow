"""Pure, no-broadcast Arc Testnet plan for the TradeProof demo."""

from __future__ import annotations

from typing import Any, Callable

ARC_TESTNET_CHAIN_ID = 5_042_002
ARC_REFERENCE_CONTRACT = "0x0747eef0706327138c69792bf28cd525089e4583"
ARC_TESTNET_USDC_INTERFACE = "0x3600000000000000000000000000000000000000"
EXECUTION_CONFIRMATION = "TRADEPROOF_TESTNET_EXECUTION_CONFIRMED"


class AuthorizationRequired(PermissionError):
    """Raised before a credentials client can be constructed."""


def require_execution_authorization(
    *, execute: bool, confirmation: str | None, client_factory: Callable[[], Any] | None = None
) -> None:
    """Validate explicit user approval without touching secrets or a network client."""
    del client_factory
    if execute is not True:
        raise AuthorizationRequired("testnet execution requires explicit --execute")
    if confirmation != EXECUTION_CONFIRMATION:
        raise AuthorizationRequired("testnet execution requires the literal confirmation token")


def _hash(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ValueError(f"{name} must be a lowercase 64-character SHA-256 hash")
    return "0x" + value


def _address(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 42 or not value.startswith("0x"):
        raise ValueError(f"{name} must be an EVM address")
    return value.lower()


def build_arc_testnet_plan(
    *,
    client: str,
    provider: str,
    evaluator: str,
    invoice_hash: str,
    delivery_proof_hash: str,
    expiry_epoch: int,
) -> dict[str, Any]:
    """Return a public, deterministic plan; it cannot create a Circle client or broadcast."""
    if not isinstance(expiry_epoch, int) or expiry_epoch <= 0:
        raise ValueError("expiry_epoch must be a positive integer")
    client = _address(client, "client")
    provider = _address(provider, "provider")
    evaluator = _address(evaluator, "evaluator")
    invoice_hash = _hash(invoice_hash, "invoice_hash")
    delivery_proof_hash = _hash(delivery_proof_hash, "delivery_proof_hash")

    return {
        "mode": "DRY_RUN_NO_BROADCAST",
        "chain_id": ARC_TESTNET_CHAIN_ID,
        "reference_contract": ARC_REFERENCE_CONTRACT,
        "test_usdc_interface": ARC_TESTNET_USDC_INTERFACE,
        "invoice_hash": invoice_hash,
        "delivery_proof_hash": delivery_proof_hash,
        "expiry_epoch": expiry_epoch,
        "actors": {"client": client, "provider": provider, "evaluator": evaluator},
        "steps": [
            {"name": "create_job_a", "actor": "client", "method": "createJob"},
            {"name": "set_budget_a", "actor": "provider", "method": "setBudget"},
            {"name": "approve_a", "actor": "client", "method": "approve"},
            {"name": "fund_a", "actor": "client", "method": "fund"},
            {"name": "submit_delivery_proof_a", "actor": "provider", "method": "submit"},
            {"name": "complete_a", "actor": "evaluator", "method": "complete"},
            {"name": "create_job_b", "actor": "client", "method": "createJob"},
            {"name": "set_budget_b", "actor": "provider", "method": "setBudget"},
            {"name": "approve_b", "actor": "client", "method": "approve"},
            {"name": "fund_b", "actor": "client", "method": "fund"},
            {"name": "claim_refund_b", "actor": "client", "method": "claimRefund"},
        ],
    }
