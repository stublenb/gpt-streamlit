import json
import boto3
import os
import openai

s3 = boto3.resource('s3')
my_bucket = s3.Bucket('bfs-chat')

def get_openai_models():
    models = []
    openai_models = openai.Model.list()
    for model in openai_models['data']:
        models.append(model['root'])
    models.sort()
    return models

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

def get_collection_files(collection):
    collection_path = collection + '/'
    files = []
    for obj in my_bucket.objects.all():
        if collection_path in obj.key and collection_path != obj.key:
            files.append(obj.key)
    files = list(set(files))
    files.sort()
    return files

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