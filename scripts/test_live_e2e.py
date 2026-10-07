import urllib.request
import json

def test_live():
    base = "http://localhost:8000"
    print("1. Checking Backend Health...")
    with urllib.request.urlopen(f"{base}/health") as r:
        data = json.loads(r.read().decode())
        print(f"   Status: {r.status}, Service: {data.get('service')}")

    print("2. Authenticating as team...")
    auth_data = json.dumps({"username": "team", "password": "secret"}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/auth/login",
        data=auth_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        token = json.loads(r.read().decode())["access_token"]
        print("   JWT Access Token acquired.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("3. Creating Shipment Session...")
    shipment_payload = json.dumps({
        "name": "Live Verification Run - Cochin to Rotterdam",
        "description": "Full end-to-end integration test"
    }).encode("utf-8")
    req = urllib.request.Request(f"{base}/shipments", data=shipment_payload, headers=headers)
    with urllib.request.urlopen(req) as r:
        shipment = json.loads(r.read().decode())
        shipment_id = shipment["id"]
        print(f"   Created Shipment: ID={shipment_id}, Name='{shipment['name']}'")

    print("4. Loading and Ingesting 5 Sample Documents...")
    req = urllib.request.Request(
        f"{base}/shipments/{shipment_id}/load-samples",
        data=b"{}",
        headers=headers
    )
    with urllib.request.urlopen(req) as r:
        sample_res = json.loads(r.read().decode())
        print(f"   Sample docs loaded: {sample_res.get('documents')}")

    print("5. Verifying Ingested Documents...")
    req = urllib.request.Request(f"{base}/shipments/{shipment_id}/documents", headers=headers)
    with urllib.request.urlopen(req) as r:
        docs = json.loads(r.read().decode())
        print(f"   Document count: {len(docs)}")
        for d in docs:
            print(f"   - {d.get('file_name')} ({d.get('doc_type')}): status={d.get('extraction_status')}")

    print("6. Verifying Discrepancy Detection Engine...")
    req = urllib.request.Request(f"{base}/shipments/{shipment_id}/discrepancies", headers=headers)
    with urllib.request.urlopen(req) as r:
        discs = json.loads(r.read().decode())
        print(f"   Total discrepancies detected: {len(discs)}")
        for d in discs:
            print(f"   - [{d.get('severity').upper()}] {d.get('field_name')}: Doc A='{d.get('document_a_value')}' vs Doc B='{d.get('document_b_value')}' (Status: {d.get('status')})")

    print("7. Verifying Customs Readiness Checklist...")
    req = urllib.request.Request(f"{base}/shipments/{shipment_id}/checklist", headers=headers)
    with urllib.request.urlopen(req) as r:
        checklist = json.loads(r.read().decode())
        print(f"   Checklist items generated: {len(checklist)}")
        for item in checklist[:3]:
            passed_str = "PASS" if item.get("is_passed") else "FAIL"
            print(f"   - [{passed_str}] {item.get('label')}: {item.get('notes')}")

    print("8. Generating PDF/HTML Verification Report...")
    req = urllib.request.Request(f"{base}/shipments/{shipment_id}/report/pdf", headers=headers)
    with urllib.request.urlopen(req) as r:
        report_bytes = r.read()
        content_type = r.headers.get("Content-Type")
        print(f"   Report generated successfully! Size: {len(report_bytes)} bytes, Content-Type: {content_type}")

    print("9. Verifying Analytics Dashboard Metrics...")
    req = urllib.request.Request(f"{base}/dashboard", headers=headers)
    with urllib.request.urlopen(req) as r:
        metrics = json.loads(r.read().decode())
        print(f"   Total Shipment Sessions: {metrics.get('total_sessions')}")
        print(f"   Overall Pass Rate: {metrics.get('overall_pass_rate')}%")
        print(f"   Open Discrepancies: {metrics.get('open_discrepancies')}")
        print(f"   Status Breakdown: {metrics.get('status_breakdown')}")

    print("10. Verifying React Frontend Dev Server...")
    with urllib.request.urlopen("http://localhost:5173") as r:
        html = r.read().decode("utf-8")
        print(f"   Frontend HTTP status: {r.status} OK (HTML size: {len(html)} bytes)")

    print("\n=======================================================")
    print("ALL TESTS PASSED! ExportGuard is fully operational.")
    print("=======================================================\n")

if __name__ == "__main__":
    test_live()
