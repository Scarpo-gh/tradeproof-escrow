from fastapi.testclient import TestClient

from tradeproof.api import create_app


VALID_INVOICE = {
    "invoice_ref": "INV-UAE-001",
    "buyer": "UAE Demo Buyer LLC",
    "supplier": "Global Demo Supplier Ltd",
    "amount_minor": 10_000,
    "currency": "USDC",
    "delivery_deadline": "2026-08-09T12:00:00Z",
}


def test_create_invoice_job_returns_hash_and_draft_status():
    client = TestClient(create_app())

    response = client.post("/v1/invoice-jobs", json=VALID_INVOICE)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "DRAFT"
    assert len(body["invoice_hash"]) == 64
    assert body["arc_job_id"] is None


def test_get_invoice_job_returns_created_job():
    client = TestClient(create_app())
    created = client.post("/v1/invoice-jobs", json=VALID_INVOICE).json()

    response = client.get(f"/v1/invoice-jobs/{created['id']}")

    assert response.status_code == 200
    assert response.json()["invoice_ref"] == "INV-UAE-001"


def test_create_invoice_job_rejects_invalid_amount():
    client = TestClient(create_app())

    response = client.post("/v1/invoice-jobs", json={**VALID_INVOICE, "amount_minor": 0})

    assert response.status_code == 422


def test_healthz_never_exposes_configuration_or_wallet_data():
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
