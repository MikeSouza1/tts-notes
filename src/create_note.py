import json, os, boto3, traceback
from common import resp, user_id, now_iso, new_note_id, BUCKET_NAME, DEFAULT_VOICE, TABLE_NAME

# Clientes AWS
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")

# Algumas vozes não existem em todas as regiões. Ajuste se precisar.
POLLY_REGION = os.environ.get("POLLY_REGION", os.environ.get("AWS_REGION", "sa-east-1"))
polly = boto3.client("polly", region_name=POLLY_REGION)

def handler(event, context):
    """POST /notes  -> gera MP3 com Polly, salva no S3 e grava metadados no DynamoDB"""
    try:
        body = json.loads(event.get("body") or "{}")
        text = (body.get("text") or "").strip()
        voice = (body.get("voice") or DEFAULT_VOICE).strip()

        if not text:
            return resp(400, {"error": "Campo 'text' é obrigatório."})

        uid = user_id(event)
        note_id = new_note_id()
        created_at = now_iso()
        s3_key = f"{uid}/{note_id}.mp3"

        # TTS
        synth = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId=voice)
        audio = synth["AudioStream"].read()

        # S3
        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=audio, ContentType="audio/mpeg")

        # DynamoDB
        table.put_item(Item={
            "userId": uid,
            "createdAt": created_at,
            "noteId": note_id,
            "text": text[:2000],
            "voice": voice,
            "status": "READY",
            "s3Key": s3_key
        })

        return resp(201, {"noteId": note_id, "status": "READY", "createdAt": created_at})

    except Exception as e:
        # Log detalhado no CloudWatch
        print("ERROR:", repr(e))
        traceback.print_exc()
        return resp(500, {"error": "create_failed", "detail": str(e)})
