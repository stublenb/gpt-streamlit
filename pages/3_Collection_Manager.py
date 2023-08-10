import streamlit as st
import pandas as pd
import boto3
import json
import psycopg2
from doc_chat_common import get_secret

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

def get_collection_files(collection):
    collection_path = collection + '/'
    files = []
    for obj in my_bucket.objects.all():
        if collection_path in obj.key and collection_path != obj.key:
            files.append(obj.key)
    files = list(set(files))
    files.sort()
    return files

def delete_files_s3(files, checkbox):
    for file in files:
        if checkbox[file]:
            s3.Object('bfs-chat', file).delete()
    return True

def delete_files_pg(files, checkbox):
    pg = get_secret('postgres-vector', 'us-east-1')

    conn = psycopg2.connect(
        host=pg['host'],
        database='postgres',
        user=pg['username'],
        password=pg['password'],
        port=pg['port']
    )

    cursor = conn.cursor()
    for file in files:
        if checkbox[file]:
            delete_sql = 'DELETE FROM public.langchain_pg_embedding where cmetadata->>\'source\' like \'%' + file + '%\''
            cursor.execute(delete_sql)
    conn.commit()
    cursor.close()
    conn.close()
    return True


collection = st.selectbox(
    'What collection would you like to add the document to?',
    get_collections())

files_to_delete = []
checkbox = {}

form = st.form("checkboxes", clear_on_submit = True)
with form:
    files = get_collection_files(collection)
    for file in files:
        checkbox[file] = st.checkbox(file)

submitted = form.form_submit_button("Delete Files")
if submitted:
    delete_files_s3(files, checkbox)
    delete_files_pg(files, checkbox)
    st.experimental_rerun()

