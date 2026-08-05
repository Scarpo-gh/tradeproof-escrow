from types import SimpleNamespace

import pytest

from tradeproof.arc_execution import ExecutionGuardError, build_step, execute_step
from tradeproof.arc_preflight import build_arc_testnet_plan


def _plan():
    return build_arc_testnet_plan(
        client="0x7a0a0bd6e35cf5656c6fbc6c6b769b53c374d4b8",
        provider="0x14f7bfa882989448edc8147009cee42d69ef78c8",
        evaluator="0x7a0a0bd6e35cf5656c6fbc6c6b769b53c374d4b8",
        invoice_hash="a" * 64,
        delivery_proof_hash="b" * 64,
        expiry_epoch=1_800_000_000,
    )


def test_create_job_step_uses_tradeproof_description_and_arc_reference_contract():
    step = build_step(_plan(), name="create_job_a")

    assert step.request_fields["blockchain"] == "ARC-TESTNET"
    assert step.request_fields["abiFunctionSignature"] == "createJob(address,address,uint256,string,address)"
    assert step.request_fields["contractAddress"] == "0x0747eef0706327138c69792bf28cd525089e4583"
    assert step.request_fields["abiParameters"][3].startswith("TradeProof invoice escrow")


def test_guard_blocks_client_factory_before_any_sdk_or_network_access():
    step = build_step(_plan(), name="create_job_a")
    calls = []

    with pytest.raises(ExecutionGuardError, match="--execute"):
        execute_step(step, execute=False, confirmation=None, client_factory=lambda: calls.append("called"))

    assert calls == []


def test_guarded_step_uses_only_public_request_fields_and_returns_tx_hash():
    step = build_step(_plan(), name="create_job_a")
    created = []

    class Request:
        @classmethod
        def from_dict(cls, payload):
            created.append(payload)
            return payload

    class Transactions:
        def __init__(self, _client):
            pass

        def create_developer_transaction_contract_execution(self, _request):
            return SimpleNamespace(data=SimpleNamespace(id="circle-tx-id"))

        def get_transaction(self, *, id):
            assert id == "circle-tx-id"
            return SimpleNamespace(data=SimpleNamespace(transaction=SimpleNamespace(state="COMPLETE", tx_hash="0xabc")))

    sdk = SimpleNamespace(CreateContractExecutionTransactionForDeveloperRequest=Request, TransactionsApi=Transactions)
    result = execute_step(step, execute=True, confirmation="TRADEPROOF_TESTNET_EXECUTION_CONFIRMED", client_factory=lambda: (object(), sdk), poll_interval_seconds=0)

    assert result == {"transaction_id": "circle-tx-id", "state": "COMPLETE", "tx_hash": "0xabc"}
    assert "entitySecretCiphertext" not in created[0]
