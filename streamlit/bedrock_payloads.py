import json

bedrock_payloads = {
    "Claude v2" : {
        "modelId": "anthropic.claude-v2",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "$BEDROCK_PROMPT_HERE$",
            "max_tokens_to_sample": 500,
            "temperature": 0.5,
            "top_k": 300,
            "top_p": 1,
            "stop_sequences": [],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    "Titan Embeddings": {
        "modelId": "amazon.titan-embed-text-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": "$BEDROCK_PROMPT_HERE$"
        } 
    }
}

def build_payload(payload_name, body):
    print(bedrock_payloads[payload_name])
    JSON_payload = json.dumps(bedrock_payloads[payload_name])
    JSON_payload = JSON_payload.replace('$BEDROCK_PROMPT_HERE$', body)
    print(JSON_payload)
    return json.loads(JSON_payload, strict=False)