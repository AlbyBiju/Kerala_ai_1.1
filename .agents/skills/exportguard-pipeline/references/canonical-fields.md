# Canonical Field Matrix Reference

Extracted and verified across the 5 export document types:

| Field Name | Description | Invoice | Packing List | Shipping Bill | PO | Quality Cert | Severity |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| `exporter_name` | Shipper / Vendor Name | ✓ | ✓ | ✓ | ✓ | ✓ | warning |
| `importer_name` | Consignee / Buyer Name | ✓ | ✓ | ✓ | ✓ | | warning |
| `shipment_date` | Date of export / issue | ✓ | ✓ | ✓ | ✓ | | warning |
| `total_quantity` | Total unit count | ✓ | ✓ | ✓ | ✓ | | critical |
| `total_weight_kg` | Total mass in kg | ✓ | ✓ | ✓ | | | critical |
| `total_value_usd` | Total commercial value | ✓ | | | ✓ | | critical |
| `currency` | Currency code (USD, EUR, etc.) | ✓ | | | ✓ | | info |
| `hs_code` | Harmonized System Tariff Code | ✓ | ✓ | ✓ | ✓ | | critical |
| `product_description` | Commodity goods description | ✓ | ✓ | ✓ | ✓ | ✓ | warning |
| `port_of_loading` | Origin seaport/airport | ✓ | | ✓ | | | warning |
| `port_of_discharge` | Destination seaport/airport | ✓ | | ✓ | | | warning |
| `invoice_number` | Commercial invoice identifier | ✓ | | | | | info |
| `payment_terms` | Terms of payment | ✓ | | | | | info |
| `number_of_cartons` | Package count | | ✓ | | | | critical |
| `gross_weight_kg` | Gross cargo weight | | ✓ | | | | info |
| `net_weight_kg` | Net cargo weight | | ✓ | | | | info |
| `shipping_bill_number`| Customs SB / BL number | | | ✓ | | | info |
| `vessel_name` | Transport vessel name | | | ✓ | | | info |
| `voyage_number` | Vessel voyage number | | | ✓ | | | info |
| `po_number` | Purchase order identifier | | | | ✓ | | info |
| `buyer_ref` | Buyer reference ID | | | | ✓ | | info |
| `certificate_number` | Lab cert ID | | | | | ✓ | info |
| `lab_name` | Testing laboratory | | | | | ✓ | info |
| `test_date` | Lab test date | | | | | ✓ | info |
