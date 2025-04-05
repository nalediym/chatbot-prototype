import os
import requests
from dotenv import load_dotenv
from openai import OpenAI  # ✅ correct import for v1.69.0
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ use OpenAI client instance

app = FastAPI()


# Mount static files (if you have CSS or JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


url = "https://itsmfleaders.org/"

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load custom instructions
with open("itsmf_instructions.txt", "r") as file:
    CUSTOM_INSTRUCTIONS = file.read()

class MessageRequest(BaseModel):
    message: str

@app.post("/chat/")
async def chat(request: MessageRequest):
    user_message = request.message


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




@app.get("/chat/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    #return templates.TemplateResponse("Cookies_Consent_Model.html", {"request": request})
    #return templates.TemplateResponse("page1.html", {"request": request})
    #return templates.TemplateResponse("C_LM_Home.html", {"request": request})  
    #return templates.TemplateResponse("start_new_Chat.html", {"request": request})
    