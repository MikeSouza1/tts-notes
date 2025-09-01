import json, os, boto3
from boto3.dynamodb.conditions import Key
from common import resp, user_id, now_iso, BUCKET_NAME, DEFAULT_VOICE, TABLE_NAME

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")
polly = boto3.client("polly")

def handler(event, context):
    uid = user_id(event)
    note_id = event.get("pathParameters", {}).get("id")
    if not note_id:
        return resp(400, {"error": "note id ausente"})

    body = json.loads(event.get("body") or "{}")
    new_text = (body.get("text") or "").strip()
    new_voice = (body.get("voice") or DEFAULT_VOICE).strip()

    # Busca item pelo GSI noteById e garante que pertence ao usuário
    q = table.query(
        IndexName="noteById",
        KeyConditionExpression=Key("noteId").eq(note_id)
    )
    items = [it for it in q.get("Items", []) if it.get("userId") == uid]
    if not items:
        return resp(404, {"error": "nota não encontrada"})
    item = items[0]

    # Atualiza áudio se texto/voz mudaram
    s3_key = item.get("s3Key")
    if new_text:
        synth = polly.synthesize_speech(Text=new_text, OutputFormat="mp3", VoiceId=new_voice)
        audio = synth["AudioStream"].read()
        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=audio, ContentType="audio/mpeg")

    # Atualiza metadados
    expr = "SET #voice=:v, #status=:s, #updatedAt=:u"
    vals = {":v": new_voice, ":s": "READY", ":u": now_iso()}
    names = {"#voice": "voice", "#status": "status", "#updatedAt": "updatedAt"}
    if new_text:
        expr += ", #text=:t"
        vals[":t"] = new_text[:2000]
        names["#text"] = "text"

    table.update_item(
        Key={"userId": item["userId"], "createdAt": item["createdAt"]},
        UpdateExpression=expr,
        ExpressionAttributeValues=vals,
        ExpressionAttributeNames=names
    )

    return resp(200, {"noteId": note_id, "status": "READY"})
