"""Fail-closed Circle execution adapter for TradeProof's Arc Testnet demo."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import time
from typing import Any, Callable
from uuid import uuid4

from tradeproof.arc_preflight import EXECUTION_CONFIRMATION

CHAIN = "ARC-TESTNET"
REFERENCE_CONTRACT = "0x0747eef0706327138c69792bf28cd525089e4583"
USDC_INTERFACE = "0x3600000000000000000000000000000000000000"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
BUDGET_BASE_UNITS = "1000000"  # 1 synthetic test-USDC


class ExecutionGuardError(PermissionError):
    """Raised before a local credential file or Circle client is accessed."""


class TransactionFailedError(RuntimeError):
    """Raised when Circle returns a terminal failure state."""


@dataclass(frozen=True)
class ExecutionStep:
    name: str
    request_fields: dict[str, Any]
    idempotency_key: str
    ref_id: str


def _reason_hash(invoice_hash: str) -> str:
    return "0x" + sha256(f"tradeproof:invoice-completed:v1:{invoice_hash}".encode()).hexdigest()


def _step(name: str, wallet: str, contract: str, signature: str, parameters: list[Any]) -> ExecutionStep:
    return ExecutionStep(
        name=name,
        request_fields={
            "blockchain": CHAIN,
            "walletAddress": wallet,
            "contractAddress": contract,
            "abiFunctionSignature": signature,
            "abiParameters": parameters,
            "feeLevel": "MEDIUM",
        },
        idempotency_key=str(uuid4()),
        ref_id=f"tradeproof:arc:{name}",
    )


def build_step(plan: dict[str, Any], *, name: str, job_id: int | None = None) -> ExecutionStep:
    """Create one public Circle request from a no-broadcast TradeProof plan."""
    if plan.get("mode") != "DRY_RUN_NO_BROADCAST":
        raise ValueError("only a TradeProof dry-run plan can be executed")
    actors = plan["actors"]
    client, provider, evaluator = actors["client"], actors["provider"], actors["evaluator"]
    expiry = str(plan["expiry_epoch"])
    invoice_hash = plan["invoice_hash"]
    proof_hash = plan["delivery_proof_hash"]
    if name in {"set_budget_a", "approve_a", "fund_a", "submit_delivery_proof_a", "complete_a", "set_budget_b", "approve_b", "fund_b", "claim_refund_b"}:
        if not isinstance(job_id, int) or job_id < 0:
            raise ValueError(f"{name} requires a non-negative onchain job_id")

    if name == "create_job_a":
        return _step(name, client, REFERENCE_CONTRACT, "createJob(address,address,uint256,string,address)", [provider, evaluator, expiry, f"TradeProof invoice escrow completion: {invoice_hash[2:14]}", ZERO_ADDRESS])
    if name == "set_budget_a":
        return _step(name, provider, REFERENCE_CONTRACT, "setBudget(uint256,uint256,bytes)", [job_id, BUDGET_BASE_UNITS, "0x"])
    if name == "approve_a":
        return _step(name, client, USDC_INTERFACE, "approve(address,uint256)", [REFERENCE_CONTRACT, BUDGET_BASE_UNITS])
    if name == "fund_a":
        return _step(name, client, REFERENCE_CONTRACT, "fund(uint256,bytes)", [job_id, "0x"])
    if name == "submit_delivery_proof_a":
        return _step(name, provider, REFERENCE_CONTRACT, "submit(uint256,bytes32,bytes)", [job_id, proof_hash, "0x"])
    if name == "complete_a":
        return _step(name, evaluator, REFERENCE_CONTRACT, "complete(uint256,bytes32,bytes)", [job_id, _reason_hash(invoice_hash), "0x"])
    if name == "create_job_b":
        return _step(name, client, REFERENCE_CONTRACT, "createJob(address,address,uint256,string,address)", [provider, evaluator, expiry, f"TradeProof invoice escrow refund: {invoice_hash[2:14]}", ZERO_ADDRESS])
    if name == "set_budget_b":
        return _step(name, provider, REFERENCE_CONTRACT, "setBudget(uint256,uint256,bytes)", [job_id, BUDGET_BASE_UNITS, "0x"])
    if name == "approve_b":
        return _step(name, client, USDC_INTERFACE, "approve(address,uint256)", [REFERENCE_CONTRACT, BUDGET_BASE_UNITS])
    if name == "fund_b":
        return _step(name, client, REFERENCE_CONTRACT, "fund(uint256,bytes)", [job_id, "0x"])
    if name == "claim_refund_b":
        return _step(name, client, REFERENCE_CONTRACT, "claimRefund(uint256)", [job_id])
    raise ValueError(f"unknown TradeProof execution step: {name}")


def require_execution_authorization(*, execute: bool, confirmation: str | None) -> None:
    if execute is not True:
        raise ExecutionGuardError("execution requires explicit --execute")
    if confirmation != EXECUTION_CONFIRMATION:
        raise ExecutionGuardError("execution requires literal confirmation token")


def _default_client_factory(env_file: Path) -> tuple[Any, Any]:
    from dotenv import load_dotenv
    from circle.web3 import developer_controlled_wallets as dcw, utils

    load_dotenv(env_file, override=False)
    api_key = os.getenv("CIRCLE_API_KEY")
    entity_secret = os.getenv("CIRCLE_ENTITY_SECRET")
    if not api_key or not entity_secret:
        raise RuntimeError("Circle credentials unavailable after authorized request")
    return utils.init_developer_controlled_wallets_client(api_key=api_key, entity_secret=entity_secret), dcw


def execute_step(
    step: ExecutionStep,
    *,
    execute: bool,
    confirmation: str | None,
    client_factory: Callable[[], tuple[Any, Any]] | None = None,
    env_file: Path | None = None,
    poll_interval_seconds: float = 2,
    max_polls: int = 45,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, str | None]:
    """Broadcast exactly one pre-authorized step; never prints credentials."""
    require_execution_authorization(execute=execute, confirmation=confirmation)
    if client_factory is None:
        if env_file is None:
            raise ValueError("authorized execution requires an explicit local env_file")
        client_factory = lambda: _default_client_factory(env_file)
    client, dcw = client_factory()
    payload = {**step.request_fields, "idempotencyKey": step.idempotency_key, "refId": step.ref_id}
    request = dcw.CreateContractExecutionTransactionForDeveloperRequest.from_dict(payload)
    transactions = dcw.TransactionsApi(client)
    response = transactions.create_developer_transaction_contract_execution(request)
    transaction_id = str(response.data.id)
    for _ in range(max_polls):
        transaction = transactions.get_transaction(id=transaction_id).data.transaction
        raw_state = getattr(transaction, "state", None)
        state = str(getattr(raw_state, "value", raw_state)).rsplit(".", 1)[-1]
        if state == "COMPLETE":
            return {"transaction_id": transaction_id, "state": state, "tx_hash": getattr(transaction, "tx_hash", None)}
        if state in {"FAILED", "CANCELLED", "DENIED"}:
            raise TransactionFailedError(f"Circle transaction terminal state: {state}")
        sleep(poll_interval_seconds)
    raise TimeoutError("Circle transaction polling timed out; reconcile before retrying")
