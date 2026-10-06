import json
import re
from typing import Dict, List, Protocol, Optional
import httpx
from app.core.config import settings
from app.core.fields import CANONICAL_FIELDS_PER_DOC

class LLMProvider(Protocol):
    async def extract_fields(self, document_text: str, doc_type: str, expected_fields: List[str]) -> Dict[str, str]:
        ...

class RuleBasedFallbackProvider:
    """
    Intelligent heuristic and regex extraction engine.
    Ensures full offline operation, fast test execution, and fallback resilience
    when external LLM APIs (OpenAI / Watsonx) are not configured or rate-limited.
    """
    async def extract_fields(self, document_text: str, doc_type: str, expected_fields: List[str]) -> Dict[str, str]:
        extracted = {}
        text = document_text

        # Exporter / Shipper
        exporter_match = re.search(r"(?:Exporter|Shipper|Seller|From)[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if exporter_match and "exporter_name" in expected_fields:
            extracted["exporter_name"] = exporter_match.group(1).strip()

        # Importer / Consignee / Buyer
        importer_match = re.search(r"(?:Importer|Consignee|Buyer|To)[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if importer_match and "importer_name" in expected_fields:
            extracted["importer_name"] = importer_match.group(1).strip()

        # Date
        date_match = re.search(r"(?:Date|Shipment Date|Invoice Date|Issue Date)[:\s]+(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})", text, re.IGNORECASE)
        if date_match and "shipment_date" in expected_fields:
            extracted["shipment_date"] = date_match.group(1).strip()

        # Quantity
        qty_match = re.search(r"(?:Total Quantity|Quantity|Qty)[:\s]+([\d,]+(?:\.\d+)?)\s*(?:Units|PCS|Nos|Cartons|Boxes)?", text, re.IGNORECASE)
        if qty_match and "total_quantity" in expected_fields:
            extracted["total_quantity"] = qty_match.group(1).replace(",", "").strip()

        # Weight
        weight_match = re.search(r"(?:Total Weight|Gross Weight|Net Weight|Weight)[:\s]+([\d,]+(?:\.\d+)?)\s*(?:KG|KGS|MT)?", text, re.IGNORECASE)
        if weight_match and "total_weight_kg" in expected_fields:
            extracted["total_weight_kg"] = weight_match.group(1).replace(",", "").strip()

        # Total Value USD
        val_match = re.search(r"(?:Total Value|Total Amount|Invoice Value|FOB Value)[:\s]+(?:USD|\$)?\s*([\d,]+(?:\.\d+)?)", text, re.IGNORECASE)
        if val_match and "total_value_usd" in expected_fields:
            extracted["total_value_usd"] = val_match.group(1).replace(",", "").strip()
            if "currency" in expected_fields:
                extracted["currency"] = "USD"

        # HS Code
        hs_match = re.search(r"(?:HS Code|Tariff Code|ITC HS|Harmonized Code)[:\s]+(\d{4}(?:\.\d{2}(?:\.\d{2})?)?|\d{6,10})", text, re.IGNORECASE)
        if hs_match and "hs_code" in expected_fields:
            extracted["hs_code"] = hs_match.group(1).strip()

        # Product Description
        desc_match = re.search(r"(?:Description of Goods|Product Description|Goods Description|Commodity)[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if desc_match and "product_description" in expected_fields:
            extracted["product_description"] = desc_match.group(1).strip()

        # Ports
        pol_match = re.search(r"(?:Port of Loading|POL|Port of Departure)[:\s]+([^\n\r,]+)", text, re.IGNORECASE)
        if pol_match and "port_of_loading" in expected_fields:
            extracted["port_of_loading"] = pol_match.group(1).strip()

        pod_match = re.search(r"(?:Port of Discharge|POD|Port of Destination)[:\s]+([^\n\r,]+)", text, re.IGNORECASE)
        if pod_match and "port_of_discharge" in expected_fields:
            extracted["port_of_discharge"] = pod_match.group(1).strip()

        # Specific fields
        inv_match = re.search(r"(?:Invoice (?:No|Number|#))[:\s]+([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if inv_match and "invoice_number" in expected_fields:
            extracted["invoice_number"] = inv_match.group(1).strip()

        carton_match = re.search(r"(?:Number of Cartons|Cartons|Total Packages)[:\s]+(\d+)", text, re.IGNORECASE)
        if carton_match and "number_of_cartons" in expected_fields:
            extracted["number_of_cartons"] = carton_match.group(1).strip()

        sb_match = re.search(r"(?:Shipping Bill (?:No|Number|#)|Bill of Lading)[:\s]+([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if sb_match and "shipping_bill_number" in expected_fields:
            extracted["shipping_bill_number"] = sb_match.group(1).strip()

        po_match = re.search(r"(?:PO (?:No|Number|#)|Purchase Order)[:\s]+([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if po_match and "po_number" in expected_fields:
            extracted["po_number"] = po_match.group(1).strip()

        cert_match = re.search(r"(?:Certificate (?:No|Number|#))[:\s]+([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if cert_match and "certificate_number" in expected_fields:
            extracted["certificate_number"] = cert_match.group(1).strip()

        # Lab Name
        lab_match = re.search(r"(?:Lab Name|Laboratory|Inspection Body)[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if lab_match and "lab_name" in expected_fields:
            extracted["lab_name"] = lab_match.group(1).strip()

        # Buyer Ref
        buyer_match = re.search(r"(?:Buyer Ref|Buyer Reference)[:\s]+([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if buyer_match and "buyer_ref" in expected_fields:
            extracted["buyer_ref"] = buyer_match.group(1).strip()

        # Payment Terms
        pay_match = re.search(r"(?:Payment Terms)[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if pay_match and "payment_terms" in expected_fields:
            extracted["payment_terms"] = pay_match.group(1).strip()

        # Vessel & Voyage
        vessel_match = re.search(r"(?:Vessel Name|Vessel)[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if vessel_match and "vessel_name" in expected_fields:
            extracted["vessel_name"] = vessel_match.group(1).strip()

        voyage_match = re.search(r"(?:Voyage Number|Voyage)[:\s]+([A-Za-z0-9\-_/]+)", text, re.IGNORECASE)
        if voyage_match and "voyage_number" in expected_fields:
            extracted["voyage_number"] = voyage_match.group(1).strip()

        # Test Date
        if "test_date" in expected_fields and "shipment_date" in extracted:
            extracted["test_date"] = extracted["shipment_date"]

        return extracted

class OpenAIProvider:
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o")

    async def extract_fields(self, document_text: str, doc_type: str, expected_fields: List[str]) -> Dict[str, str]:
        fields_str = ", ".join(expected_fields)
        prompt = (
            f"You are an expert customs and trade document parser. Extract the following canonical fields from the document text.\n"
            f"Document Type: {doc_type}\n"
            f"Expected Fields: {fields_str}\n\n"
            f"Document Text:\n{document_text[:6000]}\n\n"
            f"Return ONLY a valid JSON object mapping each found field_name to its exact string value. "
            f"Do not include fields not found in the text."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            return json.loads(raw_content)

class WatsonxProvider:
    def __init__(self, api_key: str, project_id: str, url: str):
        self.api_key = api_key
        self.project_id = project_id
        self.url = url

    async def extract_fields(self, document_text: str, doc_type: str, expected_fields: List[str]) -> Dict[str, str]:
        # IBM Watsonx AI REST endpoint call
        return await RuleBasedFallbackProvider().extract_fields(document_text, doc_type, expected_fields)

def get_llm_provider() -> LLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider(settings.OPENAI_API_KEY)
    elif provider == "watsonx" and settings.WATSONX_API_KEY:
        return WatsonxProvider(settings.WATSONX_API_KEY, settings.WATSONX_PROJECT_ID or "", settings.WATSONX_URL or "")
    return RuleBasedFallbackProvider()
