import openai
import streamlit as st
import boto3
import json
from query_data import chain_options
from query_data import template
import doc_chat_common
import os

doc_chat_common.set_api_key()

collection = st.sidebar.selectbox(
    'What collection would you like to chat with?',
    doc_chat_common.get_collections())

llm = st.sidebar.selectbox(
    'What LLM would you like to use?',
    doc_chat_common.get_openai_models()
)
temperature = st.sidebar.slider(
    'Set temperature for model',
    0.0, 1.0, 1.0, 0.05)

model = st.sidebar.selectbox(
    'Which QA model would you like to work with?',
    list(chain_options.keys())
)

st.write(template)
# def reset_conversation():
#   st.session_state.conversation = None
#   st.session_state.chat_history = None
#   st.session_state.messages = []
# st.sidebar.button('Reset Chat', on_click=reset_conversation)

chain = chain_options[model](collection, llm, temperature)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    result = chain({"question": prompt}) #, collection)
    #st.write('Answer: ', result['answer'])
    #response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    #msg = response.choices[0].message
    msg['content'] = result['answer']
    msg['role'] = 'assistant'
    st.session_state.messages.append(msg)
    if model == 'with_sources':
        msg['content'] = msg['content'] + '\n\n'
        for doc in result['source_documents']:
            msg['content'] = msg['content'] +  doc.metadata['source'] + '\n\n'
            msg['content'] = msg['content'] + doc.page_content + '\n\n'
    st.chat_message("assistant").write(msg['content'])

