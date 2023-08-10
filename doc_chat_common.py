import json
import boto3
import os

s3 = boto3.resource('s3')
my_bucket = s3.Bucket('bfs-chat')

def get_collections():
    collections = []
    files = []
    for obj in my_bucket.objects.all():
        files.append(obj.key)
        if '/' in obj.key:
            collections.append(obj.key.split('/')[0])
    collections = list(set(collections))
    collections.sort()
    return collections

def get_secret(secret_name, region_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])

    return secret
def set_api_key():
    os.environ["OPENAI_API_KEY"] = get_secret('OPENAI_API_KEY', 'us-east-1')['OPENAI_API_KEY']