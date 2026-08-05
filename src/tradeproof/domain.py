"""Canonical, synthetic invoice inputs for the testnet-only TradeProof demo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json


class ValidationError(ValueError):
    """Raised when a synthetic invoice is unsuitable for the demo workflow."""


@dataclass(frozen=True)
class Invoice:
    invoice_ref: str
    buyer: str
    supplier: str
    amount_minor: int
    currency: str
    delivery_deadline: str

    def __post_init__(self) -> None:
        for name in ("invoice_ref", "buyer", "supplier"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"{name} must be a non-empty string")
        if isinstance(self.amount_minor, bool) or not isinstance(self.amount_minor, int) or self.amount_minor <= 0:
            raise ValidationError("amount_minor must be a positive integer")
        if self.currency != "USDC":
            raise ValidationError("currency must be USDC for this testnet demo")
        if not isinstance(self.delivery_deadline, str):
            raise ValidationError("delivery_deadline must be an ISO-8601 string")
        try:
            datetime.fromisoformat(self.delivery_deadline.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("delivery_deadline must be ISO-8601") from exc


def canonical_invoice_hash(invoice: Invoice) -> str:
    """Return the SHA-256 hash of the stable business fields only."""
    payload = {
        "amount_minor": invoice.amount_minor,
        "buyer": invoice.buyer.strip(),
        "currency": invoice.currency,
        "delivery_deadline": invoice.delivery_deadline,
        "invoice_ref": invoice.invoice_ref.strip(),
        "supplier": invoice.supplier.strip(),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()
