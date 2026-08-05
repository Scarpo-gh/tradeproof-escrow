"""Local-only API for synthetic, testnet invoice-escrow demo jobs."""

from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from tradeproof.domain import Invoice, ValidationError, canonical_invoice_hash
from tradeproof.jobs import EscrowJob, create_draft_job


class InvoiceJobRequest(BaseModel):
    invoice_ref: str
    buyer: str
    supplier: str
    amount_minor: int
    currency: str
    delivery_deadline: str
    expected_proof_hash: str | None = None


class InvoiceJobResponse(BaseModel):
    id: str
    invoice_ref: str
    invoice_hash: str
    expected_proof_hash: str
    status: str
    arc_job_id: int | None
    fund_tx_hash: str | None
    complete_tx_hash: str | None
    refund_tx_hash: str | None


def _response(job_id: str, invoice_ref: str, job: EscrowJob) -> InvoiceJobResponse:
    return InvoiceJobResponse(id=job_id, invoice_ref=invoice_ref, **asdict(job))


def create_app() -> FastAPI:
    app = FastAPI(
        title="TradeProof Escrow API",
        version="0.1.0",
        description="Synthetic invoice and testnet-only escrow demo API.",
        docs_url=None,
        redoc_url=None,
    )
    jobs: dict[str, tuple[str, EscrowJob]] = {}

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/invoice-jobs", response_model=InvoiceJobResponse, status_code=status.HTTP_201_CREATED)
    def create_invoice_job(request: InvoiceJobRequest) -> InvoiceJobResponse:
        try:
            invoice = Invoice(
                invoice_ref=request.invoice_ref,
                buyer=request.buyer,
                supplier=request.supplier,
                amount_minor=request.amount_minor,
                currency=request.currency,
                delivery_deadline=request.delivery_deadline,
            )
        except ValidationError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        invoice_hash = canonical_invoice_hash(invoice)
        proof_hash = request.expected_proof_hash or invoice_hash
        try:
            job = create_draft_job(invoice_hash, proof_hash, expiry_epoch=1)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        job_id = str(uuid4())
        jobs[job_id] = (invoice.invoice_ref, job)
        return _response(job_id, invoice.invoice_ref, job)

    @app.get("/v1/invoice-jobs/{job_id}", response_model=InvoiceJobResponse)
    def get_invoice_job(job_id: str) -> InvoiceJobResponse:
        stored = jobs.get(job_id)
        if stored is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invoice job not found")
        invoice_ref, job = stored
        return _response(job_id, invoice_ref, job)

    return app


app = create_app()
