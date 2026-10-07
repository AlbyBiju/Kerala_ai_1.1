"""System-level live integration verification test for ExportGuard.

Validates the complete backend API surface, extraction pipeline,
discrepancy detection engine, checklist readiness, PDF reporting, and dashboard metrics.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings
from app.core.database import init_db


@pytest.mark.asyncio
async def test_full_system_verification():
    await init_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        health = await client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        print("\n[PASS] Health check passed")

        # 2. Authentication
        login_res = await client.post("/auth/login", json={
            "username": settings.TEAM_USERNAME,
            "password": settings.TEAM_PASSWORD
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] Team login successful, JWT token acquired")

        # 3. Create a new Shipment Session
        shipment_res = await client.post("/shipments", json={
            "name": "Live Test Shipment - Kochi to Singapore",
            "description": "Marine seafood export batch 2026-X"
        }, headers=headers)
        assert shipment_res.status_code == 201
        shipment = shipment_res.json()
        shipment_id = shipment["id"]
        print(f"[PASS] Shipment session created: ID={shipment_id}")

        # 4. Load Sample Documents (triggers parsing, extraction, and discrepancy engine)
        load_res = await client.post(f"/shipments/{shipment_id}/load-samples", headers=headers)
        assert load_res.status_code == 200
        sample_data = load_res.json()
        assert len(sample_data["documents"]) == 5
        print(f"[PASS] Loaded and parsed 5 sample documents: {sample_data['documents']}")

        # 5. Verify documents persisted and extracted
        docs_res = await client.get(f"/shipments/{shipment_id}/documents", headers=headers)
        assert docs_res.status_code == 200
        docs = docs_res.json()
        assert len(docs) == 5
        for d in docs:
            assert d["extraction_status"] == "done"
        print("[PASS] All 5 documents extracted with status='done'")

        # 6. Check Discrepancies
        discs_res = await client.get(f"/shipments/{shipment_id}/discrepancies", headers=headers)
        assert discs_res.status_code == 200
        discrepancies = discs_res.json()
        print(f"[PASS] Discrepancies detected: {len(discrepancies)} discrepancies")

        # Quantity discrepancy (1200 Cartons on invoice vs 1180 Cartons on packing list)
        qty_disc = next((d for d in discrepancies if d["field_name"] == "total_quantity"), None)
        assert qty_disc is not None
        assert qty_disc["severity"] == "critical"
        print(f"[PASS] Critical discrepancy confirmed: total_quantity mismatch ({qty_disc['document_a_value']} vs {qty_disc['document_b_value']})")

        # 7. Update Discrepancy Status (resolve/acknowledge)
        disc_id = qty_disc["id"]
        patch_res = await client.patch(
            f"/shipments/{shipment_id}/discrepancies/{disc_id}",
            json={"status": "resolved"},
            headers=headers
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "resolved"
        print(f"[PASS] Discrepancy {disc_id} updated to status='resolved'")

        # 8. Check Customs Readiness Checklist
        checklist_res = await client.get(f"/shipments/{shipment_id}/checklist", headers=headers)
        assert checklist_res.status_code == 200
        checklist = checklist_res.json()
        assert len(checklist) > 0
        print(f"[PASS] Customs readiness checklist generated with {len(checklist)} items")

        # 9. Download PDF Verification Report
        report_res = await client.get(f"/shipments/{shipment_id}/report/pdf", headers=headers)
        assert report_res.status_code == 200
        report_bytes = report_res.content
        assert len(report_bytes) > 0
        assert report_bytes.startswith(b"%PDF") or report_res.headers.get("content-type", "").startswith("text/html")
        print(f"[PASS] Report generated successfully ({len(report_bytes)} bytes, content-type={report_res.headers.get('content-type')})")

        # 10. Dashboard Metrics
        dash_res = await client.get("/dashboard", headers=headers)
        assert dash_res.status_code == 200
        metrics = dash_res.json()
        assert metrics["total_sessions"] >= 1
        assert "open_discrepancies" in metrics
        print(f"[PASS] Dashboard metrics verified: total_sessions={metrics['total_sessions']}, pass_rate={metrics['overall_pass_rate']}")

        # 11. Retrieve Shipment Detail
        detail_res = await client.get(f"/shipments/{shipment_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == shipment_id
        assert detail["name"] == "Live Test Shipment - Kochi to Singapore"
        print(f"[PASS] Retrieved shipment details successfully for ID={shipment_id}")
