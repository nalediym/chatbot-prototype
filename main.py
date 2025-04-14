import os
import requests
import uvicorn

from dotenv import load_dotenv
# from openai import OpenAI
import openai
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI as LangChainOpenAI
from langchain_openai import OpenAIEmbeddings as OpenAIEmbeddings
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
import chromadb
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
# from langchain.vectorstores import Chroma as LangChainChroma
# from langchain_community.vectorstores import Chroma as LangChainChroma
from langchain_chroma import Chroma as LangChainChroma
from fastapi.responses import HTMLResponse

# Load environment variables
load_dotenv()

# Validate API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
port = os.getenv("PORT")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. Check your .env file.")

# === Globals to be initialized on startup ===
retriever = None
qa_chain = None
vectorstore = None

# Initialize OpenAI client
# client = openai(api_key=api_key)
openai.api_key = api_key  # or os.getenv("OPENAI_API_KEY")

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




# === Utility Functions ===
def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_html(file: UploadFile) -> str:
    content = file.file.read().decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()

def extract_text_from_url(url: str) -> str:
    try:
        html = requests.get(url).text
        return BeautifulSoup(html, "html.parser").get_text()
    except Exception as e:
        return f"Error loading URL: {e}"

def embed_and_store(text: str, namespace: str):
    chunks = splitter.split_text(text)
    for i, chunk in enumerate(chunks):
        embedding = openai.Embedding.create(
            input=chunk,
            model="text-embedding-3-small"
        )["data"][0]["embedding"]

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"{namespace}-{i}"]
        )
    return len(chunks)

# === Upload Endpoint ===
@app.post("/upload/")
async def upload_data(
    namespace: str = Form(...),
    text: str = Form(""),
    url: str = Form(""),
    pdf_file: UploadFile = File(None),
    html_file: UploadFile = File(None)
):
   
    if vectorstore is None:
        return JSONResponse({"error": "Vector store not initialized."}, status_code=500)
    combined_text = ""

    if text:
        combined_text += "\n" + text
    if url:
        combined_text += "\n" + extract_text_from_url(url)
    if pdf_file:
        combined_text += "\n" + extract_text_from_pdf(pdf_file)
    if html_file:
        combined_text += "\n" + extract_text_from_html(html_file)

    if not combined_text.strip():
        return JSONResponse({"error": "No valid input provided"}, status_code=400)

    chunk_count = embed_and_store(combined_text, namespace)

    return {
        "message": "✅ Data embedded successfully.",
        "chunks": chunk_count,
        "namespace": namespace
    }




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




# === Startup Hook ===
@app.on_event("startup")
def init_vectorstore():
    global vectorstore, retriever, qa_chain
    print("🔄 Initializing ChromaDB and retriever...")
    embeddings = OpenAIEmbeddings()
    vectorstore = LangChainChroma(persist_directory="./chroma_store", embedding_function=embeddings)
    retriever = vectorstore.as_retriever()

    # # === Initialize Chroma ===   
    # chroma_client = chromadb.PersistentClient(path="./chroma_store")
    # collection = chroma_client.get_or_create_collection("knowledge")
    # splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=100)


    # 2. Embed and Store
    # embeddings = OpenAIEmbeddings()
    # db = Chroma.from_documents(texts, embeddings)
    # db = Chroma.from_documents(texts, embeddings, persist_directory="chroma_db")
    # db.persist()

    # 3. Retrieve and Generate
    # llm = OpenAI(temperature=0.2)
    llm = LangChainOpenAI(temperature=.5)
    prompt_template = """You are a helpful assistant. Use the following pieces of context to answer the question at the end. 
{context}

Question: {question}
"""

    # embeddings = OpenAIEmbeddings()
    # # Use the same persist_directory where you store data
    # vectorstore = LangChainChroma
    #     persist_directory="./chroma_store",
    #     embedding_function=embeddings
    # )

    # retriever = vectorstore.as_retriever()

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever,  return_source_documents=True, chain_type_kwargs={"prompt": prompt})

@app.post("/chat/")
async def chat(request: MessageRequest):
# async def chat(request: MessageRequest,namespace: str = Form(...), question: str = Form(...)):
    user_message = request.message
    # question_embedding = openai.Embedding.create(
    #     input=question, model="text-embedding-3-small"
    # )["data"][0]["embedding"]

    try:
        # Run LangChain RetrievalQA
        # result = qa_chain.invoke({"query": user_message})
        # result = qa_chain({"query": user_message})
        # return {
        #     "response": result["result"],
        #     "sources": [doc.metadata for doc in result["source_documents"]]
        # }
        results = collection.query(
        query_embeddings=[question_embedding],
        n_results=4,
        where={"namespace": namespace}
        )

        context = "\n---\n".join(results["documents"][0])

        prompt = f"""
        Use the context below to answer the question.

        Context:
        {context}

        Question: {question}
            """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )


        return {"answer": response["choices"][0]["message"]["content"]}

    except Exception as e:
        print("Error calling OpenAI:", e)
        return {"error": str(e)}

# Home route to serve chatbot page
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    # return templates.TemplateResponse("Cookies_Consent_Model.html", {"request": request})
    # return templates.TemplateResponse("new_chat.html", {"request": request})
     return templates.TemplateResponse("C_LM_Home.html", {"request": request})
