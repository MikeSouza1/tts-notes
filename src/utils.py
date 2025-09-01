import json

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
}

def ok(body):
    return {"statusCode": 200, "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
            "body": json.dumps(body, ensure_ascii=False)}

def err(status, message):
    return {"statusCode": status, "headers": CORS_HEADERS,
            "body": json.dumps({"error": message}, ensure_ascii=False)}
