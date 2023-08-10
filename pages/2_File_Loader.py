import streamlit as st
import pandas as pd
import boto3

s3 = boto3.resource('s3')
my_bucket = s3.Bucket('bfs-chat')
collections = []
files = []
for obj in my_bucket.objects.all():
    files.append(obj.key)
    if '/' in obj.key:
        collections.append(obj.key.split('/')[0])
collections = list(set(collections))
collections.append('<Create New Collection>')
collections.sort()


option = st.selectbox(
    'What collection would you like to add the document to?',
    collections)

if option != '<Create New Collection>':
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        if st.button('Upload File'):
            if uploaded_file is None:
                st.write('No File Selected')
            else:
                #st.write('Uploading File')
                s3 = boto3.resource('s3')
                key_path = option + '/' + uploaded_file.name
                if key_path not in files:
                    s3.Bucket('bfs-chat').put_object(Key=key_path, Body=bytes_data)
                    st.write(key_path, ' Uploaded')
                else:
                    st.write('File not uploaded: ', key_path, ' already exists')
else:
    new_collection_form = st.form("New Collection", clear_on_submit = True)
    new_collection = new_collection_form.text_input('Collection Name')
    submitted = new_collection_form.form_submit_button("Create Collection")
    if submitted:
        if new_collection not in collections:
            new_collection = new_collection + '/'
            s3.Bucket('bfs-chat').put_object(Key=new_collection)
            st.experimental_rerun()
        else:
            st.write('Collection Already Exists')
