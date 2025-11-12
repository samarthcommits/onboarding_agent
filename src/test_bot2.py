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
from .prompts import super_template, super_template_1, super_template_2, super_template_3, super_template_4, super_template_5
from tools.browser_tool import b_tool
from tools.e_tool import email_tool
from tools.ret_tool import ret_tool
token_log = 0
nest_asyncio.apply()

memory = ConversationBufferMemory()
# NeMo Guardrails setup
config = RailsConfig.from_path("C:/Users/samarth.srivastava/new_scrap/org_scraper_new/config")
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, api_key=os.environ['GEMINI_API_KEY'])
rails = LLMRails(config, llm=model)


#template with specific instructions related to the conversation and tool calling
template2 = """
            SalesGPT is a sales agent for company_name, a cutting-edge technology solutions provider, designed to assist customers with a wide range of needs by offering tailored product insights, answering questions, and guiding them toward the best solutions. As a sales agent, SalesGPT leverages its ability to generate human-like text to engage in natural, conversational exchanges, delivering responses that are relevant, persuasive, and aligned with company_name's mission to empower clients with innovative tools and services.

            SalesGPT is always refining its approach, continuously learning to better understand customer needs and provide compelling, accurate recommendations. It can process vast amounts of information to offer detailed explanations about company_name's products, answer inquiries, and highlight benefits that match the customer’s goals. Additionally, SalesGPT proactively asks follow-up questions at every step to better understand the customer’s interests, ensuring a personalized and engaging sales experience.

            Overall, SalesGPT is a powerful sales tool for company_name, adept at helping customers explore solutions, addressing their specific challenges, and providing valuable insights into how company_name offerings can enhance their lives or businesses. Whether you’re seeking a specific solution or just exploring options, SalesGPT is here to guide you with expertise and enthusiasm, always ready to ask the right questions to uncover your needs.

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
tools = [ret_tool, b_tool, email_tool]

model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        api_key=os.environ['GEMINI_API_KEY'],
    )
# llm = model
llm = ChatOllama(model='gemma3:27b', base_url=os.environ['OLLAMA_API_ADDRESS'], num_ctx=8000)

prompt2 = PromptTemplate(template=super_template_5)
tool_names = ['ret_tool', 'browser_tool', 'email_tool']
agent = create_react_agent(llm, tools, prompt2.partial(tool_names=tool_names, chat_history = memory))
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True, max_iterations=20, memory=memory)
async def process_input(user_input: str):
    # NeMo Guardrails input check
    guardrails_response = await rails.generate_async(messages=[{"role": "user", "content": user_input}])
    cond = guardrails_response["content"].startswith("I'm designed to be a helpful and harmless AI") or guardrails_response["content"].startswith("I'm unable to provide a response") or guardrails_response["content"].startswith("I understand you're trying") or guardrails_response["content"].startswith("Let's focus on task") or guardrails_response["content"].startswith("I'm not able to")

    langchain_output = agent_executor.invoke({'input':f'''
                                                {user_input}

                                                **If you decide to use the ret_tool, give the source from the information retrieved**
                                            
                                                '''})['output']

    # NeMo Guardrails output check
    guardrails_output_response = await rails.generate_async(messages=[{"role": "assistant", "content": langchain_output}])
    cond = guardrails_output_response["content"].startswith("I'm designed to be a helpful and harmless AI") or guardrails_output_response["content"].startswith("I'm unable to provide a response") or guardrails_output_response["content"].startswith("I understand you're trying") or guardrails_output_response["content"].startswith("Let's focus on task") or guardrails_output_response["content"].startswith("I'm not able to")

    if guardrails_output_response and cond:
        return guardrails_output_response["content"]

    return langchain_output
