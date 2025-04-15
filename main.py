import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# FastAPI app
app = FastAPI()

# Mount static directory for CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class MessageRequest(BaseModel):
    message: str

# Streaming generator for response
async def stream_openai_response(messages):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True
        )
        async def generate():
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    await asyncio.sleep(0.01)
        return generate()
    except Exception as e:
        async def error_gen():
            yield f"Error: {str(e)}"
        return error_gen()

# Chat endpoint (streaming)
from fastapi.responses import StreamingResponse
@app.post("/chat/", response_class=StreamingResponse)
async def chat(request: MessageRequest):
    messages = [
        {"role": "system", "content": "You are a helpful assistant named Chereena that answers ITSMF questions. Use line breaks, numbered lists, or bullet points if applicable. Format your responses using markdown-like structure."},
        {"role": "user", "content": request.message}
    ]

    def generate():
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"⚠️ Server error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")


# New Chat Window
@app.get("/new_chat", response_class=HTMLResponse)
async def serve_new_chat(request: Request):
    return templates.TemplateResponse("new_chat.html", {"request": request})

# Serve the chatbot homepage
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("C_LM_Home.html", {"request": request})
