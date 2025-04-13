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

# Endpoint for handling chatbot messages
@app.post("/chat/")
async def chat(request: MessageRequest):
    user_message = request.message
    print(f"User message: {user_message}")

    system_prompt = f"""
You are a helpful assistant that responds on behalf of the IT Senior Management Forum (ITSMF). 
Use only the tone and information aligned with ITSMF's mission, programs, and professional development content.
Here are your instructions and knowledge base:

{CUSTOM_INSTRUCTIONS}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        return {"response": reply}

    except Exception as e:
        return {"error": str(e)}

# Home route to serve chatbot page
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    # return templates.TemplateResponse("Cookies_Consent_Model.html", {"request": request})
    # return templates.TemplateResponse("new_chat.html", {"request": request})
    return templates.TemplateResponse("start_new_Chat.html", {"request": request})
