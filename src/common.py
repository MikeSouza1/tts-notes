import json, os, time, uuid

TABLE_NAME = os.environ.get("TABLE_NAME")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
DEFAULT_VOICE = os.environ.get("DEFAULT_VOICE", "Camila")

def resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }

def user_id(event):
    return (
        event.get("requestContext", {})
             .get("authorizer", {})
             .get("claims", {})
             .get("sub")
        or "local-user"
    )

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def new_note_id():
    return str(uuid.uuid4())
