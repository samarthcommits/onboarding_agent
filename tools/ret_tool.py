import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "focus-bivouac-452012-h3-99731ca57b95.json"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from langgraph.checkpoint.memory import MemorySaver
import logging
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
# from count_token_history import count_history
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain_core.memory import BaseMemory
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import hub
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
import getpass
import re
# from doc_stats import count_tokens
import asyncio
from langchain_core.documents import Document
import json
from uuid import uuid4
from langchain_ollama import OllamaEmbeddings
from langchain_cohere import CohereRerank
from langchain_community.llms import Cohere
from langchain_community.embeddings import SentenceTransformerEmbeddings
import nest_asyncio
from nemoguardrails import RailsConfig, LLMRails
def get_chunk_documents():

#--------------------------------------------------------------------#
    # chunk size info (no. of tokens):
    # mean - 570
    # std dev - 280
    # median - 541
    # min - 23
    # max - 1291
#--------------------------------------------------------------------#

    #this method parses the scraped json data and then stores content from each key (url) of the json into a separate chunk.
    with open("sample.json", 'rb') as file:
        data = file.read()
    parsed_data = json.loads(data)
    parsed_data_org = parsed_data
    #parsed_data['https://www.pal.tech/gdpr-commitment/'].find('\n\nWe are a team of high-performing')
    c = 0
    for c, i in enumerate(parsed_data):
        if c==0:
            continue
        index = parsed_data[i].find('\n\nWe are a team of high-performing')
        parsed_data[i] = parsed_data[i][:index]

    for i in parsed_data:
        ind = parsed_data[i].rfind('Digital Product Engineering')
        if(ind)!=-1:
            parsed_data[i] = parsed_data[i][:ind]
            # count+=1

    for i in parsed_data:
        parsed_data[i] = i + ' ' + parsed_data[i]

    doc = []
    for i, key in enumerate(parsed_data):
        #print(i, key)
        doc.append(Document(page_content=parsed_data[key], metadata={'source':key}, id=i))
    print('exiting 01')
    return doc


def create_retriever():
    #this method is responsible for creating the vector store and a retriever.
    embeddings = SentenceTransformerEmbeddings(model_name="Alibaba-NLP/gte-base-en-v1.5",model_kwargs={"trust_remote_code": True})
    if os.path.exists('./chroma_langchain_db1')==False:
        doc = get_chunk_documents()
        uuids = [str(uuid4()) for _ in range(len(doc))]
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db1",  # Where to save data locally, remove if not necessary
        )
        
        vector_store.add_documents(documents=doc, ids=uuids)
    else:
        vector_store = Chroma(persist_directory='./chroma_langchain_db1', embedding_function=embeddings, collection_name='example_collection')
        print('chroma db used')
    # ret = vector_store.as_retriever(search_kwargs={"k": 6})
    from experiment.src.splade_custom import Retriever
    ret = Retriever()
    llm = Cohere(temperature=0)
    compressor = CohereRerank(model="rerank-english-v3.0", top_n=2)
    compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=ret
    )
    return compression_retriever



from summarizer import Summarizer,TransformerSummarizer

#making retriever as a tool
retriever = create_retriever()
sum = Summarizer()
def summarise_ret(query):
    
    docs = retriever.invoke(query)
    
    content = ''
    res = []
    result = {}
    for doc in docs:
        result = {}
        # content = sum(doc.page_content, min_length=100)
        content = doc.page_content
        content = content.replace('\n', ' ')
        content = re.sub(' +', ' ', content)
        model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        api_key=os.environ['GEMINI_API_KEY'],
        )
        # sum = ChatOllama(model='gemma3:4b', base_url='http://10.10.12.62:11434/')
        sum = model
        content1 = sum.invoke(f"summarise this in 150 words: {content}. **Cover every aspect and give the summary only and nothing else**").content
        result['source'] = doc.metadata['source']
        result['page_content'] = content
        res.append(result)
    # k = count_tokens(docs)
    # logger.info(f'retrieved docs with {k} tokens')
    # global token_log
    # token_log+=count_tokens(docs)
    # logger.info(f'number of tokens in all: {token_log}')
    
    # result
    return res

# template1 = template
from langchain.agents import AgentType
# from sparse import Retriever
#making retriever as a tool
# ret = Retriever(top_k=6)


ret_tool = Tool(
    name='ret_tool',
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    func=summarise_ret,
    description='Retrieves relevant information from a vector database based on a query string using semantic search. Input: a string query. Output: a list with relevant information.'
)
