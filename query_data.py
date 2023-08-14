from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.pgvector import PGVector
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
import pickle
import openai
from doc_chat_common import get_secret


_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
You can assume the question about the most recent state of the union address.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# template = """You are an AI assistant for answering questions about the software license agreements.
# You are given the following extracted parts of a long document and a question. Provide a conversational answer.
# If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
# If the question is not about the contracts or license agreements, politely inform them that you are tuned to only answer questions about the contracts or license agreements that are loaded into the database.
# Lastly, answer the question as if you were a lawyer.
# Question: {question}
# =========
# {context}
# =========
# Answer in Markdown:"""

template = """You are a pirate answering questions about the software license agreements.
You are given the following extracted parts of a long document and a question. Provide a conversational answer.
If you don't know the answer, just say "Arrrgh, I'm not sure." Don't try to make up an answer.
If the question is not about the contracts or license agreements, politely inform them that you are tuned to only answer questions about the contracts or license agreements that are loaded into the database.
Lastly, answer the question as if you were a pirate.
Question: {question}
=========
{context}
=========
Answer in Markdown:"""

QA_PROMPT = PromptTemplate(template=template, input_variables=[
                           "question", "context"])

pg = get_secret('postgres-vector', 'us-east-1')

def load_retriever(collection):
    CONNECTION_STRING = 'postgresql://' + pg['username'] + ':' + pg['password'] + '@' + pg['host'] + ':' +  str(pg['port']) + '/postgres'
    embeddings = OpenAIEmbeddings()

    store = PGVector(
        collection_name=collection,
        connection_string=CONNECTION_STRING,
        embedding_function=OpenAIEmbeddings()
    )
    retriever = store.as_retriever()
    return retriever


def get_basic_qa_chain(collection, llm, temperature):
    llm = ChatOpenAI(model_name=llm, temperature=temperature)
    retriever = load_retriever(collection)
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    model = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory)
    return model


def get_custom_prompt_qa_chain(collection, llm, temperature):
    llm = ChatOpenAI(model_name=llm, temperature=temperature)
    retriever = load_retriever(collection)
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    model = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT})
    return model


def get_condense_prompt_qa_chain(collection, llm, temperature):
    llm = ChatOpenAI(model_name=llm, temperature=temperature)
    retriever = load_retriever(collection)
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    model = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT})
    return model


def get_qa_with_sources_chain(collection, llm, temperature):
    llm = ChatOpenAI(model_name=llm, temperature=temperature)
    retriever = load_retriever(collection)
    history = []
    model = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True)

    def model_func(question):
        # bug: this doesn't work with the built-in memory
        # hacking around it for the tutorial
        # see: https://github.com/langchain-ai/langchain/issues/5630
        new_input = {"question": question['question'], "chat_history": history}
        result = model(new_input)
        history.append((question['question'], result['answer']))
        return result

    return model_func


chain_options = {
    "basic": get_basic_qa_chain,
    "with_sources": get_qa_with_sources_chain
    #"custom_prompt": get_custom_prompt_qa_chain,
    #"condense_prompt": get_condense_prompt_qa_chain
}