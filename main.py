
from fastapi import FastAPI
# from .test_bot2 import agent_executor
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

# class Item(BaseModel):
#     message: str
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000/get_response",
    "http://localhost:8000",
    "https://www.pal.tech/careers",
    "http://localhost:8000/docs",
    "http://www.pal.tech/careers"
    "https://www.pal.tech"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# async def root():
#     # message = agent_executor.invoke
#     return {"message": "Hello World"}

# @app.post("/get_response")
# async def check(message:str):
#     print(message)
#     response = await agent_executor.ainvoke({'input': message})
#     return {'response':response}

class RequestBody(BaseModel):
    message: str

@app.post("/get_response")
async def check(data: RequestBody):
    print(data.message)
    res = requests.post(json={"text":data.message}, url='http://localhost:8001/query')
    # requests.post()
    try:
        # response = await agent_executor.ainvoke({'input': data.message})
        response = 'We are setting things up for you 😃'
    except:
        response = 'try again please'
    return {'response': response, 'path': res.json()['path']}