import pytest

from tradeproof.jobs import InvalidTransition, complete_job, create_draft_job, fund_job, refund_expired_job


def test_funded_job_completes_only_with_matching_delivery_proof():
    draft = create_draft_job(
        invoice_hash="a" * 64,
        expected_proof_hash="b" * 64,
        expiry_epoch=1_000,
    )
    funded = fund_job(draft, arc_job_id=42, fund_tx_hash="0xabc")

    completed = complete_job(funded, delivery_proof_hash="b" * 64, complete_tx_hash="0xdef")

    assert completed.status == "COMPLETED"
    assert completed.complete_tx_hash == "0xdef"


def test_funded_job_rejects_mismatched_delivery_proof():
    funded = fund_job(
        create_draft_job("a" * 64, "b" * 64, expiry_epoch=1_000),
        arc_job_id=42,
        fund_tx_hash="0xabc",
    )

    with pytest.raises(InvalidTransition, match="delivery proof"):
        complete_job(funded, delivery_proof_hash="c" * 64, complete_tx_hash="0xdef")


def test_refund_requires_expiry_and_is_terminal():
    funded = fund_job(
        create_draft_job("a" * 64, "b" * 64, expiry_epoch=1_000),
        arc_job_id=42,
        fund_tx_hash="0xabc",
    )

    with pytest.raises(InvalidTransition, match="not expired"):
        refund_expired_job(funded, now_epoch=999, refund_tx_hash="0x123")

    refunded = refund_expired_job(funded, now_epoch=1_000, refund_tx_hash="0x123")
    assert refunded.status == "REFUNDED"

    with pytest.raises(InvalidTransition, match="FUNDED"):
        complete_job(refunded, delivery_proof_hash="b" * 64, complete_tx_hash="0xdef")
