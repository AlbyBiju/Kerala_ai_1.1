import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings
from app.core.database import init_db

@pytest.mark.asyncio
async def test_full_exportguard_verification_flow(invoice_pdf_path, packing_list_pdf_path):
    await init_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login
        login_res = await ac.post("/auth/login", json={
            "username": settings.TEAM_USERNAME,
            "password": settings.TEAM_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Shipment Session
        create_res = await ac.post("/shipments", json={
            "name": "E2E Test Shipment Seafood 2026",
            "description": "Export to Singapore test container"
        }, headers=headers)
        assert create_res.status_code == 201
        shipment = create_res.json()
        shipment_id = shipment["id"]
        assert shipment["status"] == "draft"

        # 3. Upload Document 1: Commercial Invoice (1200 Cartons) — real PDF fixture
        with open(invoice_pdf_path, "rb") as f:
            doc1_res = await ac.post(
                f"/shipments/{shipment_id}/documents",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={"doc_type": "commercial_invoice"},
                headers=headers
            )
        assert doc1_res.status_code == 202
        doc1_id = doc1_res.json()["id"]

        # 4. Upload Document 2: Packing List (1180 Cartons — intentional discrepancy) — real PDF fixture
        with open(packing_list_pdf_path, "rb") as f:
            doc2_res = await ac.post(
                f"/shipments/{shipment_id}/documents",
                files={"file": ("packing_list.pdf", f, "application/pdf")},
                data={"doc_type": "packing_list"},
                headers=headers
            )
        assert doc2_res.status_code == 202
        doc2_id = doc2_res.json()["id"]

        # 5. List uploaded documents
        docs_res = await ac.get(f"/shipments/{shipment_id}/documents", headers=headers)
        assert docs_res.status_code == 200
        assert len(docs_res.json()) >= 2

        # 6. Trigger Analysis
        analyse_res = await ac.post(f"/shipments/{shipment_id}/analyse", headers=headers)
        assert analyse_res.status_code == 202

        # In direct execution, run the task synchronously for test validation
        from app.tasks.process_document import run_analysis_task
        await run_analysis_task(shipment_id)

        # 7. Check Discrepancies
        discs_res = await ac.get(f"/shipments/{shipment_id}/discrepancies", headers=headers)
        assert discs_res.status_code == 200
        discrepancies = discs_res.json()

        # Quantity mismatch (1200 vs 1180) must be flagged with critical severity
        qty_disc = next((d for d in discrepancies if d["field_name"] == "total_quantity"), None)
        assert qty_disc is not None
        assert qty_disc["severity"] == "critical"
        assert qty_disc["status"] == "open"

        # 8. Update Discrepancy Status (PATCH)
        patch_res = await ac.patch(
            f"/shipments/{shipment_id}/discrepancies/{qty_disc['id']}",
            json={"status": "acknowledged"},
            headers=headers
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "acknowledged"

        # 9. Verify Checklist Items
        checklist_res = await ac.get(f"/shipments/{shipment_id}/checklist", headers=headers)
        assert checklist_res.status_code == 200
        checklist = checklist_res.json()
        assert len(checklist) == 5

        # 10. Test Dashboard API
        dash_res = await ac.get("/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["total_sessions"] >= 1
        assert "open_discrepancies" in dash_data

        # 11. Download Verification Report — must be a real PDF (challenge requirement)
        report_res = await ac.get(f"/shipments/{shipment_id}/report/pdf", headers=headers)
        assert report_res.status_code == 200
        assert len(report_res.content) > 0
        assert report_res.content.startswith(b"%PDF"), (
            f"Report must be a real PDF, got magic bytes: {report_res.content[:8]!r}"
        )
        assert report_res.headers["content-type"].startswith("application/pdf")
