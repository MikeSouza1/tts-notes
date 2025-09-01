# TTS Notes — AWS Serverless (API Gateway + Lambda + Cognito + S3)

Aplicativo 100% cloud que permite criar **notas de texto** e ouvir a versão **MP3** (Text-to-Speech) gerada na AWS.
Back‑end em **AWS Lambda** com **API Gateway** (Cognito Authorizer) e dados em **DynamoDB/S3**. Front‑end **estático** (S3, opcionalmente **CloudFront + HTTPS**).

> **Demo:** http://tts-notes-site-993412843245-sa-east-1.s3-website-sa-east-1.amazonaws.com/
>
> ⚠️ Este repositório usa **placeholders** para configurações sensíveis a ambiente.
> Substitua no `html/index.html` antes de publicar o site.

## Endpoints
- `POST /notes` — cria nota (`{ text, voice }`)
- `GET /notes` — lista notas do usuário
- `GET /notes/search?q=...` — busca por texto
- `GET /notes/{id}/audio-url` — URL pré-assinada do MP3
- `DELETE /notes/{id}` — remove nota + áudio

## Pré-requisitos
- AWS CLI v2 • SAM CLI • Python 3.12
- Conta AWS (free tier) — região sugerida: `sa-east-1`

## Deploy (back‑end)
```bash
sam build --clean
sam deploy --guided
# escolha um stack name (ex.: tts-notes) e região
```

## Publicar o front‑end
Edite `html/index.html` e substitua os placeholders de ambiente:

```js
// substitua pelos seus valores reais ANTES de publicar
const API_BASE = 'https://<api-id>.execute-api.sa-east-1.amazonaws.com/prod';
const COGNITO = {
  clientId: '<APP_CLIENT_ID>',
  region: 'sa-east-1',
  endpoint: 'https://cognito-idp.sa-east-1.amazonaws.com/'
};
```

Envie para o bucket do site (pegue o nome nos Outputs do stack):
```bash
SITE=$(aws cloudformation describe-stacks --stack-name tts-notes   --query "Stacks[0].Outputs[?OutputKey=='WebsiteBucketName'].OutputValue" --output text)

aws s3 cp html/index.html "s3://$SITE/index.html" --content-type text/html --cache-control no-store
```

> Para HTTPS/URL bonita, use **CloudFront (OAC)** com default root `index.html` e fallback 403/404 → `index.html`.

## Notas de segurança
- IDs do **Cognito App Client** e URL do **API Gateway** **não são segredos**, mas evite fixar valores reais em repositório público.
- Ative verificação de e‑mail e (opcional) MFA no Cognito.
- Garanta **CORS** no API tanto em preflight (`OPTIONS`) quanto em respostas `2xx/4xx/5xx` (use `utils.ok/err`).

## Estrutura sugerida
```
src/            # Lambdas (Create/List/Search/Delete/AudioURL)
html/index.html # SPA estática (Cognito via REST + fetch)
template.yaml   # SAM/CloudFormation
```

## Licença
MIT — veja [LICENSE](LICENSE).
