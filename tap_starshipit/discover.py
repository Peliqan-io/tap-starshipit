from singer.catalog import Catalog, CatalogEntry, Schema

RESOURCES = {
    "shipped_orders": {
        "url_path":"orders/shipped",
        "result_field": "orders",
        "max_modified_field": "shipped_date",
        "base_sync": True,
        "metadata":{
           "order_id": "integer",
           "order_date": "datetime",
           "shipped_date": "string",
           "order_number": "string",
           "reference": "string",
           "integration_source_name": "string",
           "name": "string",
           "country": "string",
           "carrier": "string",
           "carrier_name": "string",
           "carrier_service_code": "string",
           "carrier_service_name": "string",
           "shipment_type": "string",
           "tracking_number": "string",
           "tracking_short_status": "string",
           "tracking_full_status": "string",
           "manifest_number": "integer",
           "manifest_sent": "boolean",
           "writeback_status": "string",
           "writeback_details": "string"
        }
    },
    "unshipped_orders": {
        "url_path":"orders/unshipped",
        "result_field": "orders",
        "max_modified_field": "order_date",
        "base_sync": True,
        "metadata": {
            "order_id": "integer",
            "order_date": "datetime",
            "order_number": "string",
            "reference": "string",
            "carrier": "string",
            "carrier_name": "string",
            "carrier_service_code": "string",
            "carrier_service_name": "string",
            "shipping_method": "string",
            "signature_required": "boolean",
            "dangerous_goods": "boolean",
            "sender_details": "object",
            "destination": "object",
            "items": "object",
            "packages": "object",
            "metadatas": "object",
            "status":"string",
            "declared_value": "number",
        }
    },
    "orders": {
        "url_path": "orders/orders",
        "result_field": "order",
        "max_modified_field": "",
        "base_sync": False,
        "metadata": {
            "order_id": "integer",
            "order_date": "datetime",
            "order_number": "string",
            "reference": "string",
            "carrier": "string",
            "carrier_name": "string",
            "carrier_service_code": "string",
            "carrier_service_name": "string",
            "shipping_method": "string",
            "signature_required": "boolean",
            "dangerous_goods": "boolean",
            "sender_details": "object",
            "destination": "object",
            "items": "object",
            "packages": "object",
            "metadatas": "object",
            "status": "string",
            "events": "object",
            "declared_value": "integer",
        }
    },
}


def get_schema(client, resource_name):
    data = RESOURCES[resource_name]["metadata"]

    properties = {}
    metadata = [
        {
            'breadcrumb': [],
            'metadata': {
                'tap-starshipit.resource': resource_name
            }
        }
    ]

    for field_name, field_type in data.items():
        if field_type in ['date', 'datetime']:
            json_schema = {
                'type': ['null', 'string'],
                'format': 'date-time'
            }
        elif field_type in ['object']:
            json_schema = {
                'type': ['null', 'object', 'string'],
                'properties': {}
            }
        else:
            json_schema = {
                'type': ['null', field_type]
            }

        properties[field_name] = json_schema

        metadata.append({
            'breadcrumb': ['properties', field_name],
            'metadata': {
                'inclusion': 'automatic' if field_name == 'order_id' else 'available'
            }
        })

    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': properties
    }

    return schema, metadata

def discover(client):
    catalog = Catalog([])

    for resource_name in RESOURCES.keys():
        schema_dict, metadata = get_schema(client, resource_name)
        schema = Schema.from_dict(schema_dict)

        stream_name = resource_name

        catalog.streams.append(CatalogEntry(
            stream=stream_name,
            tap_stream_id=stream_name,
            key_properties=['order_id'],
            schema=schema,
            metadata=metadata
        ))

    return catalog
