import urllib

import singer
from singer import metrics, metadata, Transformer
from singer.bookmarks import set_currently_syncing

from tap_starshipit.discover import discover, RESOURCES

LOGGER = singer.get_logger()

def get_bookmark(state, stream_name, default):
    return state.get('bookmarks', {}).get(stream_name, default)

def write_bookmark(state, stream_name, value):
    if 'bookmarks' not in state:
        state['bookmarks'] = {}
    state['bookmarks'][stream_name] = value
    singer.write_state(state)

def write_schema(stream):
    schema = stream.schema.to_dict()
    singer.write_schema(stream.tap_stream_id, schema, stream.key_properties)

def process_records(stream, max_modified, records):
    schema = stream.schema.to_dict()
    mdata = metadata.to_map(stream.metadata)
    max_modified_field = RESOURCES[stream.tap_stream_id].get("max_modified_field", "")

    with metrics.record_counter(stream.tap_stream_id) as counter:
        for record in records:
            if max_modified_field:
                if record[max_modified_field] > max_modified:
                    max_modified = record[max_modified_field]

            with Transformer() as transformer:
                record = transformer.transform(record,
                                               schema,
                                               mdata
                                               )
            singer.write_record(stream.tap_stream_id, record)
            counter.increment()

        return max_modified

def sync_stream(client, catalog, state, start_date, stream, order_stream):
    stream_name = stream.tap_stream_id
    last_datetime = get_bookmark(state, stream_name, start_date)

    LOGGER.info('{} - Syncing data since {}'.format(stream.tap_stream_id, last_datetime))
    resource_name = stream_name

    count = 200
    page = 1
    has_more = True
    max_modified = last_datetime
    while has_more:
        query_params = {
            'since_last_updated': last_datetime,
            'limit': count,
            'page': page,
        }

        full_result = client.get(
            '{}?{}'.format(RESOURCES[resource_name]["url_path"],urllib.parse.urlencode(query_params) ),
            endpoint=stream_name)

        records = full_result[RESOURCES[stream.tap_stream_id]["result_field"]]

        if len(records) < count:
            has_more = False
        else:
            page += 1

        max_modified = process_records(stream, max_modified, records)

        # get orders
        for order in records:
            order_id = order["order_id"]
            order_result = client.get(f'orders?order_id={order_id}', endpoint=stream_name)
            if "order" in order_result:
                process_records(order_stream, None, [order_result["order"]])
            else:
                LOGGER.info('Order ID {} not retrieved on result: {}'.format(order_id, order_result))

        write_bookmark(state, stream_name, max_modified)

def update_current_stream(state, stream_name=None):  
    set_currently_syncing(state, stream_name) 
    singer.write_state(state)

def sync(client, catalog, state, start_date):
    if not catalog:
        catalog = discover(client)
        selected_streams = catalog.streams
    else:
        selected_streams = catalog.get_selected_streams(state)

    for stream in selected_streams:
        write_schema(stream)
        if stream.tap_stream_id == "orders":
            order_stream = stream

    for stream in selected_streams:
        if RESOURCES[stream.tap_stream_id]["base_sync"]:
            update_current_stream(state, stream.tap_stream_id)
            sync_stream(client, catalog, state, start_date, stream, order_stream)

        update_current_stream(state)
