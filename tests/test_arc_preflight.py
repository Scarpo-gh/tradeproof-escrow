import pytest

from tradeproof.arc_preflight import AuthorizationRequired, build_arc_testnet_plan, require_execution_authorization


def test_execution_guard_rejects_without_explicit_flag_before_client_factory():
    called = False

    def client_factory():
        nonlocal called
        called = True

    with pytest.raises(AuthorizationRequired, match="--execute"):
        require_execution_authorization(execute=False, confirmation=None, client_factory=client_factory)

    assert called is False


def test_execution_guard_rejects_wrong_confirmation_before_client_factory():
    called = False

    def client_factory():
        nonlocal called
        called = True

    with pytest.raises(AuthorizationRequired, match="confirmation"):
        require_execution_authorization(execute=True, confirmation="wrong", client_factory=client_factory)

    assert called is False


def test_preflight_is_dry_run_with_tradeproof_specific_invoice_hash():
    plan = build_arc_testnet_plan(
        client="0x7a0a0bd6e35cf5656c6fbc6c6b769b53c374d4b8",
        provider="0x14f7bfa882989448edc8147009cee42d69ef78c8",
        evaluator="0x7a0a0bd6e35cf5656c6fbc6c6b769b53c374d4b8",
        invoice_hash="a" * 64,
        delivery_proof_hash="b" * 64,
        expiry_epoch=1_800_000_000,
    )

    assert plan["mode"] == "DRY_RUN_NO_BROADCAST"
    assert plan["chain_id"] == 5042002
    assert plan["invoice_hash"] == "0x" + "a" * 64
    assert plan["steps"][-1]["name"] == "claim_refund_b"
