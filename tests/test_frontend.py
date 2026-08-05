from fastapi.testclient import TestClient

from tradeproof.api import create_app


def test_root_serves_invoice_form_without_secret_fields():
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert 'id="invoice-form"' in response.text
    assert 'name="invoice_ref"' in response.text
    assert "privateKey" not in response.text
    assert "seed phrase" not in response.text.lower()


def test_frontend_script_targets_only_public_demo_endpoints():
    client = TestClient(create_app())

    response = client.get("/app.js")

    assert response.status_code == 200
    assert "/v1/invoice-jobs" in response.text
    assert "CIRCLE_API_KEY" not in response.text
    assert "ENTITY_SECRET" not in response.text
