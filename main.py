from typing import Optional, Dict, Any

from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
import os
import json

import uvicorn

# Importing our utils
from utils.arxiv_utils import get_paper_info, download_paper_pdf
from utils.sem_scholar_utils import get_paper_authors_info, get_paper_citations, get_paper_references, get_recommended_papers
from utils.gemini_utils import gemini_upload_file, create_gemini_chat, gemini_ask_question

load_dotenv()

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Store chats in memory (in a production app, you'd use a database)
paper_chats = {} # TODO: protect against multiple users viewing the same ID? – could give people a unique session ID when they load a paper

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/abs/{id}")
@app.get("/pdf/{id}")
@app.get("/html/{id}")
async def process_paper(request: Request, id: str, format: str = None):
    """
    Single endpoint that handles paper info and PDF display.

    Args:
        request: FastAPI request object
        id: arXiv paper ID
        format: Optional query parameter - if "pdf", returns raw PDF
    """

    # Get paper info
    paper = get_paper_info(id)

    if "error" in paper:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": paper["error"]}
        )

    pdf_content = download_paper_pdf(paper)

    if isinstance(pdf_content, dict) and "error" in pdf_content:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": pdf_content["error"]}
        )

    # If format=pdf is specified, return the raw PDF
    if format == "pdf":
        if isinstance(pdf_content, dict) and "error" in pdf_content:
            raise HTTPException(status_code=500, detail=pdf_content["error"])

        # Return the PDF directly with inline display (not attachment)
        return Response(
            content=pdf_content,
            media_type="application/pdf"
        )

    # Set up Gemini
    gemini_document = gemini_upload_file(pdf_content)
    chat = create_gemini_chat(gemini_document)

    # Store the chat for future use
    paper_chats[id] = {
        "document": gemini_document,
        "chat": chat
    }

    # Create PDF embed URL - using the same endpoint with format=pdf
    pdf_embed_url = f"/abs/{id}?format=pdf"

    authors_info = get_paper_authors_info(id)
    citations_info = get_paper_citations(id)
    references_info = get_paper_references(id)
    # recommended_papers = get_recommended_papers(id)

    # Return the HTML template with paper data
    return templates.TemplateResponse(
        "paper.html",
        {
            "request": request,
            "paper": paper,
            "authors_info": authors_info,
            "citations_info": citations_info,
            "references_info": references_info,
            "pdf_embed_url": pdf_embed_url
        }
    )


@app.post("/chat/{id}")
async def chat_with_paper(request: Request, id: str):
    """
    Endpoint to handle chat interactions with the paper.

    Args:
        request: FastAPI request object
        id: arXiv paper ID
    """
    # Get the message from the request body
    body = await request.json()
    user_message = body.get("message", "")

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Check if we already have a chat for this paper
    if id in paper_chats:
        chat = paper_chats[id]["chat"]
    else:
        # Get paper info
        paper = get_paper_info(id)

        if "error" in paper:
            raise HTTPException(status_code=404, detail=paper["error"])

        # Download the PDF
        pdf_content = download_paper_pdf(paper)

        if isinstance(pdf_content, dict) and "error" in pdf_content:
            raise HTTPException(status_code=500, detail=pdf_content["error"])

        # Set up Gemini
        gemini_document = gemini_upload_file(pdf_content)
        chat = create_gemini_chat(gemini_document)

        # Store the chat for future use
        paper_chats[id] = {
            "document": gemini_document,
            "chat": chat
        }

    # Create a streaming response with the chat
    async def generate_response():
        for chunk in gemini_ask_question(chat, user_message):
            yield chunk

    return StreamingResponse(generate_response())


if __name__ == "__main__":
    uvicorn.run(app, port=8000, loop="asyncio")