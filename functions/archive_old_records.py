import datetime
import azure.functions as func
import logging
import json
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient

COSMOS_ENDPOINT = "<YOUR_COSMOS_DB_ENDPOINT>"
COSMOS_KEY = "<YOUR_COSMOS_DB_KEY>"
COSMOS_DATABASE = "<YOUR_DB_NAME>"
COSMOS_CONTAINER = "<YOUR_CONTAINER_NAME>"
BLOB_CONNECTION_STRING = "<YOUR_BLOB_STORAGE_CONN_STRING>"
BLOB_CONTAINER = "<YOUR_BLOB_CONTAINER_NAME>"

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Archival function triggered')

    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(COSMOS_DATABASE)
    container = database.get_container_client(COSMOS_CONTAINER)

    cutoff_date = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
    query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff_date}'"
    old_records = list(container.query_items(query=query, enable_cross_partition_query=True))

    blob_service = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container=BLOB_CONTAINER, blob=f"archive_{datetime.datetime.utcnow().isoformat()}.json")

    if old_records:
        blob_client.upload_blob(json.dumps(old_records), overwrite=True)

        for item in old_records:
            container.delete_item(item=item['id'], partition_key=item['partitionKey'])

    logging.info(f"Archived {len(old_records)} records.")
