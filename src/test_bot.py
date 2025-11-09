import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "focus-bivouac-452012-h3-99731ca57b95.json"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from langgraph.checkpoint.memory import MemorySaver
import logging
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from count_token_history import count_history
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
from doc_stats import count_tokens
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
from prompts import super_template, super_template_1, super_template_2, super_template_3, super_template_4
from browser_tool import b_tool
token_log = 0
nest_asyncio.apply()
if "COHERE_API_KEY" not in os.environ:
    os.environ["COHERE_API_KEY"] = 'zf6XEllXJAVKyHmUY0QP6OQmpSlwAFXvSBjKFJYS'
memory = ConversationBufferMemory()
# NeMo Guardrails setup
config = RailsConfig.from_path("C:/Users/samarth.srivastava/new_scrap/org_scraper_new/config")
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, api_key="AIzaSyDHj1K2zO71K96f04rYJUbHFOkBkL8mR5E")
rails = LLMRails(config, llm=model)
# logger = logging.getLogger('token size status')
# logger.setLevel(logging.INFO)
from log_file import logger
def get_chunk_documents():

#--------------------------------------------------------------------#
    # chunk size info (no. of tokens):
    # mean - 570
    # std dev - 280
    # median - 541
    # min - 23
    # max - 1291
#--------------------------------------------------------------------#

    print('in here as well')
    #this method parses the scraped json data and then stores content from each key (url) of the json into a separate chunk.
    with open("C:/Users/samarth.srivastava/new_scrap/org_scraper_new/sample.json", 'rb') as file:
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
    if os.path.exists('C:/Users/samarth.srivastava/new_scrap/org_scraper_new/chroma_langchain_db3')==False:
        print('in here')
        doc = get_chunk_documents()
        uuids = [str(uuid4()) for _ in range(len(doc))]
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="C:/Users/samarth.srivastava/new_scrap/org_scraper_new/chroma_langchain_db3",  # Where to save data locally, remove if not necessary
        )
        
        vector_store.add_documents(documents=doc, ids=uuids)
    else:
        print("true")
        vector_store = Chroma(persist_directory='C:/Users/samarth.srivastava/new_scrap/org_scraper_new/chroma_langchain_db3', embedding_function=embeddings, collection_name='example_collection')
    
    print('done with embeddings, now reranking')
    ret = vector_store.as_retriever(search_kwargs={"k": 6})
    # llm = Cohere(temperature=0)
    compressor = CohereRerank(model="rerank-english-v3.0", top_n=2)
    
    compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=ret
    )
    print('retriever made')
    
    return compression_retriever


#template with specific instructions related to the conversation and tool calling
template2 = """
            SalesGPT is a sales agent for PalTech, a cutting-edge technology solutions provider, designed to assist customers with a wide range of needs by offering tailored product insights, answering questions, and guiding them toward the best solutions. As a sales agent, SalesGPT leverages its ability to generate human-like text to engage in natural, conversational exchanges, delivering responses that are relevant, persuasive, and aligned with PalTech’s mission to empower clients with innovative tools and services.

            SalesGPT is always refining its approach, continuously learning to better understand customer needs and provide compelling, accurate recommendations. It can process vast amounts of information to offer detailed explanations about PalTech’s products, answer inquiries, and highlight benefits that match the customer’s goals. Additionally, SalesGPT proactively asks follow-up questions at every step to better understand the customer’s interests, ensuring a personalized and engaging sales experience.

            Overall, SalesGPT is a powerful sales tool for PalTech, adept at helping customers explore solutions, addressing their specific challenges, and providing valuable insights into how PalTech’s offerings can enhance their lives or businesses. Whether you’re seeking a specific solution or just exploring options, SalesGPT is here to guide you with expertise and enthusiasm, always ready to ask the right questions to uncover your needs.

            TOOLS:
            SalesGPT has access to the following tools:

            {tools}

            To use a tool, please use the following format:

            {tools}

            To use a tool, please use the following format:

            Thought: Do I need to use a tool? Yes
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action

            When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

            Thought: Do I need to use a tool? No
            Final Answer: [your response here]

            Begin!

            Previous conversation history:
            {chat_history}

            New input: {input}
            {agent_scratchpad}

            
            """

from langchain.agents import AgentType
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
        api_key="AIzaSyDHj1K2zO71K96f04rYJUbHFOkBkL8mR5E",
        )
        # sum = ChatOllama(model='gemma3:4b', base_url='http://10.10.12.62:11434/')
        sum = model
        content1 = sum.invoke(f"summarise this in 150 words: {content}. **Cover every aspect and give the summary only and nothing else**").content
        result['source'] = doc.metadata['source']
        result['page_content'] = content
        res.append(result)
    k = count_tokens(docs)
    logger.info(f'retrieved docs with {k} tokens')
    global token_log
    token_log+=count_tokens(docs)
    logger.info(f'number of tokens in all: {token_log}')
    
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

# retriever = create_retriever()
# ret_tool = Tool(
#     name='ret_tool',
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     func=lambda query: retriever.invoke(query),
#     description='Retrieves relevant documents from a vector database based on a query string using semantic search. Input: a string query. Output: a list of relevant documents.'
# )

tools = [ret_tool, b_tool]

model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        api_key="AIzaSyDHj1K2zO71K96f04rYJUbHFOkBkL8mR5E",
    )
# llm = model
llm = ChatOllama(model='gemma3:27b', base_url='http://10.10.64.25:11434/', num_ctx=8000)

prompt2 = PromptTemplate(template=super_template_4)
tool_names = ['ret_tool', 'browser_tool']
agent = create_react_agent(llm, tools, prompt2.partial(tool_names=tool_names, chat_history = memory))
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=False, max_iterations=20, memory=memory)
# async def process_input(user_input: str):
#     # NeMo Guardrails input check
#     guardrails_response = await rails.generate_async(messages=[{"role": "user", "content": user_input}])
#     cond = guardrails_response["content"].startswith("I'm designed to be a helpful and harmless AI") or guardrails_response["content"].startswith("I'm unable to provide a response") or guardrails_response["content"].startswith("I understand you're trying") or guardrails_response["content"].startswith("Let's focus on task") or guardrails_response["content"].startswith("I'm not able to")

#     # print('guardrails_response: ', guardrails_response)
#     # if guardrails_response and cond:
#     #     # return guardrails_response["content"]
#     #     print('')

#     # LangChain agent execution
#     langchain_output = agent_executor.invoke({'input':f'''
#                                                 {user_input}

#                                                 **If you decide to use the ret_tool, give the source from the information retrieved**
                                            
#                                                 '''})['output']

#     # NeMo Guardrails output check
#     guardrails_output_response = await rails.generate_async(messages=[{"role": "assistant", "content": langchain_output}])
#     cond = guardrails_output_response["content"].startswith("I'm designed to be a helpful and harmless AI") or guardrails_output_response["content"].startswith("I'm unable to provide a response") or guardrails_output_response["content"].startswith("I understand you're trying") or guardrails_output_response["content"].startswith("Let's focus on task") or guardrails_output_response["content"].startswith("I'm not able to")

#     if guardrails_output_response and cond:
#         return guardrails_output_response["content"]

#     return langchain_output
# # input1 = input('You: ')
# # while(input1!='q'):
# #   message = agent_executor.invoke({'input':f'''
# #                                       {input1}
                                  
# #                                     **The tools you are equipped with will give you all the context you need to respond**'''})
# #   #print('You: ', input1)
# #   print('SalesGPT: ',message['output'], '\n')
# #   input1 = input('You: ')    
input1 = ''
flag = 0
# def f_call(input1)
while(input1!='q'):
    if flag==0:
        flag=1
        message = agent_executor.invoke({'input':'Introduce yourself but briefly'})
        #message = "Hi! I'm SalesGPT, a sales agent for PalTech. How may I assist you today?"
        print('SalesGPT: ', message['output'], '\n')
        k = count_history(agent_executor.memory.chat_memory)
        # logger.info(f'chat history tokens: {k}')
        token_log+=k
        # logger.info(f'final tokens in this iteration: {token_log}')
        input1 = input('You: ')
        token_log = 0
        continue
    # result = asyncio.run(process_input(input1))
    result = agent_executor.invoke({'input':input1})['output']
    print('SalesGPT: ', result, '\n')
    
    # global token_log
    # print(agent_executor.memory.chat_memory)
    # print(type(agent_executor.memory.chat_memory))
    # print('\n', agent_executor.memory.buffer)
    k = count_history(agent_executor.memory.chat_memory)
    # logger.info(f'chat history tokens: {k}')
    token_log+=k
    # logger.info(f'final tokens in this iteration: {token_log}')
    input1 = input('\nYou: ')
    token_log = 0
    # print(token_log)
    

# print('total_tokens:', token_log)
# token_log = 0

# result = agent_executor.invoke({'input':'hi'})
# print(result)
# print(agent_executor.invoke({'input':'what else?'}))
# print('\nmemory:\n')
# print(agent_executor.memory)