import os, json, boto3, traceback
from boto3.dynamodb.conditions import Key, Attr  
from common import resp, user_id, TABLE_NAME

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    uid = user_id(event)
    try:
        params = event.get("queryStringParameters") or {}
        q = (params.get("q") or params.get("query") or "").strip()
        if not q:
            return resp(400, {"error": "parâmetro 'q' é obrigatório"})

        # Query pela PK (userId) + filtro contém (case sensitive)
        res = table.query(
            KeyConditionExpression=Key("userId").eq(uid),
            FilterExpression=Attr("text").contains(q),
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
            }
            for it in items
        ]
        return resp(200, {"q": q, "count": len(notes), "notes": notes})

    except Exception as e:
        # Loga e tenta um fallback com SCAN (completo, mais lento)
        print("SEARCH_ERROR:", repr(e))
        traceback.print_exc()
        try:
            res2 = table.scan(
                FilterExpression=Attr("userId").eq(uid) & Attr("text").contains(q)
            )
            items2 = res2.get("Items", [])
            notes2 = [
                {
                    "noteId": it.get("noteId"),
                    "text": it.get("text"),
                    "voice": it.get("voice"),
                    "status": it.get("status"),
                    "createdAt": it.get("createdAt"),
                }
                for it in items2
            ]
            return resp(200, {"q": q, "count": len(notes2), "notes": notes2, "mode": "fallback-scan"})
        except Exception as e2:
            print("FALLBACK_ERROR:", repr(e2))
            traceback.print_exc()
            return resp(500, {"error": "search_failed", "detail": str(e2)})
