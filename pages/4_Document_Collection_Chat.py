import openai
import streamlit as st
import boto3
import json
from query_data import chain_options
import my_funcs

collection = st.sidebar.selectbox(
    'What collection would you like to chat with?',
    my_funcs.get_collections())

#st.title("Chatbot")
model = st.sidebar.selectbox(
    'Which QA model would you like to work with?',
    list(chain_options.keys())
)
chain = chain_options[model](collection)
st.write('You selected:', model)

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

