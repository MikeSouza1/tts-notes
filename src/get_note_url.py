import os, boto3
from boto3.dynamodb.conditions import Key
from common import resp, user_id, TABLE_NAME, BUCKET_NAME

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")

def handler(event, context):
    uid = user_id(event)
    note_id = event.get("pathParameters", {}).get("id")
    if not note_id:
        return resp(400, {"error": "note id ausente"})

    q = table.query(IndexName="noteById", KeyConditionExpression=Key("noteId").eq(note_id))
    items = [it for it in q.get("Items", []) if it.get("userId") == uid]
    if not items:
        return resp(404, {"error": "nota não encontrada"})
    item = items[0]

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": item["s3Key"]},
        ExpiresIn=600  # 10 min
    )
    return resp(200, {"audioUrl": url})
