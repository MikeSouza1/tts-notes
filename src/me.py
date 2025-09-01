import json

def handler(event, context):
    # Em API Gateway REST + Authorizer Cognito, os claims vêm aqui:
    claims = (event.get("requestContext", {})
                   .get("authorizer", {})
                   .get("claims", {}))

    # Campos mais úteis: sub (id), email, cognito:username
    user = {
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "username": claims.get("cognito:username")
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"me": user})
    }
