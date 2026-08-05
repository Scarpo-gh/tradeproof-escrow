"""Fail-closed local model of a synthetic testnet invoice-escrow job."""

from __future__ import annotations

from dataclasses import dataclass, replace


class InvalidTransition(ValueError):
    """Raised for a lifecycle transition that must not be allowed."""


@dataclass(frozen=True)
class EscrowJob:
    invoice_hash: str
    expected_proof_hash: str
    expiry_epoch: int
    status: str = "DRAFT"
    arc_job_id: int | None = None
    fund_tx_hash: str | None = None
    complete_tx_hash: str | None = None
    refund_tx_hash: str | None = None


def _require_hash(value: str, field: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ValueError(f"{field} must be a lowercase 64-character SHA-256 hash")


def create_draft_job(invoice_hash: str, expected_proof_hash: str, expiry_epoch: int) -> EscrowJob:
    _require_hash(invoice_hash, "invoice_hash")
    _require_hash(expected_proof_hash, "expected_proof_hash")
    if not isinstance(expiry_epoch, int) or expiry_epoch <= 0:
        raise ValueError("expiry_epoch must be a positive integer")
    return EscrowJob(invoice_hash=invoice_hash, expected_proof_hash=expected_proof_hash, expiry_epoch=expiry_epoch)


def fund_job(job: EscrowJob, arc_job_id: int, fund_tx_hash: str) -> EscrowJob:
    if job.status != "DRAFT":
        raise InvalidTransition("only DRAFT jobs can be funded")
    if not isinstance(arc_job_id, int) or arc_job_id <= 0:
        raise ValueError("arc_job_id must be a positive integer")
    if not isinstance(fund_tx_hash, str) or not fund_tx_hash.startswith("0x"):
        raise ValueError("fund_tx_hash must be a transaction hash")
    return replace(job, status="FUNDED", arc_job_id=arc_job_id, fund_tx_hash=fund_tx_hash)


def complete_job(job: EscrowJob, delivery_proof_hash: str, complete_tx_hash: str) -> EscrowJob:
    if job.status != "FUNDED":
        raise InvalidTransition("only FUNDED jobs can complete")
    if delivery_proof_hash != job.expected_proof_hash:
        raise InvalidTransition("delivery proof does not match the job")
    if not isinstance(complete_tx_hash, str) or not complete_tx_hash.startswith("0x"):
        raise ValueError("complete_tx_hash must be a transaction hash")
    return replace(job, status="COMPLETED", complete_tx_hash=complete_tx_hash)


def refund_expired_job(job: EscrowJob, now_epoch: int, refund_tx_hash: str) -> EscrowJob:
    if job.status != "FUNDED":
        raise InvalidTransition("only FUNDED jobs can be refunded")
    if now_epoch < job.expiry_epoch:
        raise InvalidTransition("job is not expired")
    if not isinstance(refund_tx_hash, str) or not refund_tx_hash.startswith("0x"):
        raise ValueError("refund_tx_hash must be a transaction hash")
    return replace(job, status="REFUNDED", refund_tx_hash=refund_tx_hash)
