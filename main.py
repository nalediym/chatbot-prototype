import os
import requests
import uvicorn

from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Chroma
# from langchain.llms import OpenAI as LangChainOpenAI
# from langchain_community.llms import OpenAI as LangChainOpenAI
from langchain_openai import OpenAI as LangChainOpenAI
from langchain_openai import OpenAIEmbeddings as OpenAIEmbeddings
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate


# Load environment variables
load_dotenv()

# Validate API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
port = os.getenv("PORT")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. Check your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Create FastAPI app instance
app = FastAPI()

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Allow frontend access (dev only — restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load custom instructions from text file
with open("itsmf_instructions.txt", "r") as file:
    CUSTOM_INSTRUCTIONS = file.read()

# Data model for chat input
class MessageRequest(BaseModel):
    message: str

# 1. Load and Chunk Data
loader = TextLoader("itsmf_instructions.txt") # Replace with your file
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# 2. Embed and Store
embeddings = OpenAIEmbeddings()
# db = Chroma.from_documents(texts, embeddings)
db = Chroma.from_documents(texts, embeddings, persist_directory="chroma_db")
# db.persist()

# 3. Retrieve and Generate
# llm = OpenAI(temperature=0.2)
llm = LangChainOpenAI(temperature=0)
prompt_template = """You are a helpful assistant. Use the following pieces of context to answer the question at the end.
{context}
Question: {question}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=db.as_retriever(), return_source_documents=True, chain_type_kwargs={"prompt": prompt})

# # 4. Run the RAG pipeline
# query = "What is the main topic of the document?"
# result = qa_chain({"query": query})

# print(result["result"])
# print(result["source_documents"])

# Endpoint for handling chatbot messages
# @app.post("/chat/")
# async def chat(request: MessageRequest):
#     user_message = request.message

    # Load custom instructions from text file
    # with open("itsmf_instructions.txt", "r") as file:
    #     CUSTOM_INSTRUCTIONS = file.read()

    # system_prompt = f"""
    # You are a helpful assistant that responds on behalf of the IT Senior Management Forum (ITSMF). 
    # Use only the tone and information aligned with ITSMF's mission, programs, and professional development content.
    # Here are your instructions and knowledge base:

    # # {CUSTOM_INSTRUCTIONS}
    # # """
@app.post("/chat/")
async def chat(request: MessageRequest):
    user_message = request.message

    try:
        # Run LangChain RetrievalQA
        result = qa_chain.invoke({"query": user_message})
        # result = qa_chain({"query": user_message})
        # return {
        #     "response": result["result"],
        #     "sources": [doc.metadata for doc in result["source_documents"]]
        # }
        return {
            "response": result["result"],
            "sources": [
                {
                    "metadata": doc.metadata,
                    "content": doc.page_content
                }
                for doc in result["source_documents"]
            ]
        }

    except Exception as e:
        print("Error calling OpenAI:", e)
        return {"error": str(e)}

# Home route to serve chatbot page
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    # return templates.TemplateResponse("Cookies_Consent_Model.html", {"request": request})
    # return templates.TemplateResponse("new_chat.html", {"request": request})
    return templates.TemplateResponse("start_new_Chat.html", {"request": request})
