import io
import os
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings

FIXTURE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "docs", "fixtures")
)


@pytest.mark.asyncio
async def test_upload_valid_pdf_returns_202():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login = await ac.post(
            "/auth/login",
            json={"username": settings.TEAM_USERNAME, "password": settings.TEAM_PASSWORD},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        shipment = await ac.post(
            "/shipments",
            json={"name": "Upload Test Shipment", "description": None},
            headers=headers,
        )
        assert shipment.status_code == 201
        shipment_id = shipment.json()["id"]

        with open(os.path.join(FIXTURE_DIR, "invoice.pdf"), "rb") as f:
            res = await ac.post(
                f"/shipments/{shipment_id}/documents",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={"doc_type": "commercial_invoice"},
                headers=headers,
            )
        assert res.status_code == 202
        body = res.json()
        assert body["original_filename"] == "invoice.pdf"
        assert body["extraction_status"] in {"pending", "processing", "done"}

        docs = await ac.get(f"/shipments/{shipment_id}/documents", headers=headers)
        assert docs.status_code == 200
        assert len(docs.json()) == 1


@pytest.mark.asyncio
async def test_upload_invalid_content_type_rejected_400():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login = await ac.post(
            "/auth/login",
            json={"username": settings.TEAM_USERNAME, "password": settings.TEAM_PASSWORD},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        shipment = await ac.post(
            "/shipments",
            json={"name": "Bad Content Test", "description": None},
            headers=headers,
        )
        shipment_id = shipment.json()["id"]

        # Fake PDF: text bytes masquerading as a PDF -> content check must reject
        res = await ac.post(
            f"/shipments/{shipment_id}/documents",
            files={"file": ("fake.pdf", io.BytesIO(b"this is not a real pdf"), "application/pdf")},
            data={"doc_type": "commercial_invoice"},
            headers=headers,
        )
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_upload_oversized_file_rejected_413(monkeypatch):
    from app.services import storage as storage_module

    monkeypatch.setattr(storage_module, "MAX_FILE_SIZE_BYTES", 1024)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login = await ac.post(
            "/auth/login",
            json={"username": settings.TEAM_USERNAME, "password": settings.TEAM_PASSWORD},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        shipment = await ac.post(
            "/shipments",
            json={"name": "Oversize Test", "description": None},
            headers=headers,
        )
        shipment_id = shipment.json()["id"]

        with open(os.path.join(FIXTURE_DIR, "invoice.pdf"), "rb") as f:
            res = await ac.post(
                f"/shipments/{shipment_id}/documents",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={"doc_type": "commercial_invoice"},
                headers=headers,
            )
        assert res.status_code == 413
