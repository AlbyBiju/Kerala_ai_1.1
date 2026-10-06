from typing import Dict, List, Set

DOC_TYPES = [
    "commercial_invoice",
    "packing_list",
    "shipping_bill",
    "purchase_order",
    "quality_certificate"
]

CANONICAL_FIELDS_PER_DOC: Dict[str, List[str]] = {
    "commercial_invoice": [
        "exporter_name", "importer_name", "shipment_date", "total_quantity",
        "total_weight_kg", "total_value_usd", "currency", "hs_code",
        "product_description", "port_of_loading", "port_of_discharge",
        "invoice_number", "payment_terms"
    ],
    "packing_list": [
        "exporter_name", "importer_name", "shipment_date", "total_quantity",
        "total_weight_kg", "hs_code", "product_description",
        "number_of_cartons", "gross_weight_kg", "net_weight_kg"
    ],
    "shipping_bill": [
        "exporter_name", "importer_name", "shipment_date", "total_quantity",
        "total_weight_kg", "hs_code", "product_description",
        "port_of_loading", "port_of_discharge", "shipping_bill_number",
        "vessel_name", "voyage_number"
    ],
    "purchase_order": [
        "exporter_name", "importer_name", "shipment_date", "total_quantity",
        "total_value_usd", "currency", "hs_code", "product_description",
        "po_number", "buyer_ref"
    ],
    "quality_certificate": [
        "exporter_name", "product_description",
        "certificate_number", "lab_name", "test_date"
    ]
}

CRITICAL_FIELDS: Set[str] = {
    "total_quantity",
    "total_weight_kg",
    "total_value_usd",
    "number_of_cartons",
    "hs_code"
}

WARNING_FIELDS: Set[str] = {
    "product_description",
    "shipment_date",
    "port_of_loading",
    "port_of_discharge",
    "exporter_name",
    "importer_name"
}

def get_field_severity(field_name: str) -> str:
    if field_name in CRITICAL_FIELDS:
        return "critical"
    if field_name in WARNING_FIELDS:
        return "warning"
    return "info"
