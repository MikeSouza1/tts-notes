import os, json, boto3
from boto3.dynamodb.conditions import Key
from utils import ok, err

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def _uid(event):
    return (event.get("requestContext", {})
                 .get("authorizer", {})
                 .get("claims", {})
                 .get("sub") or "local-user")

def handler(event, context):
    try:
        user_id = _uid(event)
        res = table.query(
            KeyConditionExpression=Key("userId").eq(user_id),
            ScanIndexForward=False
        )
        items = res.get("Items", [])
        notes = [
            {
                "noteId": it.get("noteId"),
                "text": it.get("text"),
                "voice": it.get("voice"),
                "status": it.get("status"),
                "createdAt": it.get("createdAt"),
            } for it in items
        ]
        return ok({"notes": notes})
    except Exception as e:
        return err(500, f"list failed: {e}")
