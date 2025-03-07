import json
import boto3
# Inicializa el cliente Lambda
lambda_client = boto3.client('lambda', region_name='us-east-1')
# Crea el payload que simula el evento S3
payload = { "Records": [{ "s3": { "bucket": {"name": "landingcasas101012"}, "object": {"key": "2025-03-07.html"}
         }
    }]
}
# Invoca la función Lambda
response = lambda_client.invoke( FunctionName='webScrappyMitula', InvocationType='RequestResponse')
# Imprime la respuesta
print(response['Payload'].read().decode('utf-8'))
