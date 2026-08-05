from datetime import datetime, timezone

import pytest

from tradeproof.domain import Invoice, ValidationError, canonical_invoice_hash


def test_canonical_invoice_hash_is_stable_for_same_business_input():
    invoice = Invoice(
        invoice_ref="INV-UAE-001",
        buyer="UAE Demo Buyer LLC",
        supplier="Global Demo Supplier Ltd",
        amount_minor=10_000,
        currency="USDC",
        delivery_deadline="2026-08-09T12:00:00Z",
    )

    assert canonical_invoice_hash(invoice) == canonical_invoice_hash(invoice)


def test_canonical_invoice_hash_changes_when_amount_changes():
    base = {
        "invoice_ref": "INV-UAE-001",
        "buyer": "UAE Demo Buyer LLC",
        "supplier": "Global Demo Supplier Ltd",
        "currency": "USDC",
        "delivery_deadline": "2026-08-09T12:00:00Z",
    }

    assert canonical_invoice_hash(Invoice(amount_minor=10_000, **base)) != canonical_invoice_hash(
        Invoice(amount_minor=10_001, **base)
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"invoice_ref": ""},
        {"amount_minor": 0},
        {"amount_minor": -1},
        {"delivery_deadline": "not-a-date"},
    ],
)
def test_invoice_rejects_invalid_business_input(changes):
    payload = {
        "invoice_ref": "INV-UAE-001",
        "buyer": "UAE Demo Buyer LLC",
        "supplier": "Global Demo Supplier Ltd",
        "amount_minor": 10_000,
        "currency": "USDC",
        "delivery_deadline": "2026-08-09T12:00:00Z",
    }
    payload.update(changes)

    with pytest.raises(ValidationError):
        Invoice(**payload)
