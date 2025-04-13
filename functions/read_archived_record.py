import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient

BLOB_CONNECTION_STRING = "<YOUR_BLOB_STORAGE_CONN_STRING>"
BLOB_CONTAINER = "<YOUR_BLOB_CONTAINER_NAME>"

def main(req: func.HttpRequest) -> func.HttpResponse:
    record_id = req.params.get('id')
    if not record_id:
        return func.HttpResponse("Please pass a record ID", status_code=400)

    blob_service = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    container_client = blob_service.get_container_client(BLOB_CONTAINER)

    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob)
        content = blob_client.download_blob().readall()
        records = json.loads(content)
        for record in records:
            if record['id'] == record_id:
                return func.HttpResponse(json.dumps(record), mimetype="application/json")

    return func.HttpResponse("Record not found", status_code=404)
