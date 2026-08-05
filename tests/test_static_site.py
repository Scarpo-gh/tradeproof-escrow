from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pages_entrypoint_is_wallet_free_and_links_verifiable_evidence():
    page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "TradeProof Escrow" in page
    assert "STATIC DEMO" in page
    assert "crypto.subtle.digest" in page
    assert "168870" in page
    assert "168872" in page
    assert "privateKey" not in page
    assert "seed phrase" not in page.lower()
