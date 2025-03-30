from typing import Optional, Dict, Any
import logging

from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
import os
import json

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tldrxiv")

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

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.info(f"Serving home page to {request.client.host}")
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search")
async def search(request: Request, q: str):
    logger.info(f"Search request received: {q}")
    # Extract arXiv ID from URL if a full URL was provided
    if "arxiv.org/abs/" in q:
        id = q.split("arxiv.org/abs/")[1].split("?")[0].split("#")[0]
        logger.info(f"Extracted ID from URL: {id}")
    else:
        # Assume it's already an ID
        id = q.strip()
        logger.info(f"Using provided ID: {id}")
    
    # Redirect to the paper page
    from fastapi.responses import RedirectResponse
    logger.info(f"Redirecting to /abs/{id}")
    return RedirectResponse(url=f"/abs/{id}", status_code=303)

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
    logger.info(f"Processing paper: {id}, format: {format}")

    # Get paper info
    logger.info(f"Fetching paper info for {id}")
    paper = get_paper_info(id)

    if "error" in paper:
        logger.error(f"Error fetching paper {id}: {paper['error']}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": paper["error"]}
        )

    pdf_content = download_paper_pdf(paper)

    if isinstance(pdf_content, dict) and "error" in pdf_content:
        logger.error(f"Error downloading PDF for {id}: {pdf_content['error']}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": pdf_content["error"]}
        )

    # If format=pdf is specified, return the raw PDF
    if format == "pdf":
        logger.info(f"Returning raw PDF for {id}")
        if isinstance(pdf_content, dict) and "error" in pdf_content:
            raise HTTPException(status_code=500, detail=pdf_content["error"])

        # Return the PDF directly with inline display (not attachment)
        return Response(
            content=pdf_content,
            media_type="application/pdf"
        )

    # Set up Gemini
    logger.info(f"Uploading PDF to Gemini API")
    gemini_document = gemini_upload_file(pdf_content)
    logger.info(f"Creating Gemini chat session")
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
    recommended_papers = get_recommended_papers(id)

    print("Recommended papers:", recommended_papers)

    # Return the HTML template with paper data
    return templates.TemplateResponse(
        "paper.html",
        {
            "request": request,
            "paper": paper,
            "authors_info": authors_info,
            "citations_info": citations_info,
            "references_info": references_info,
            "recommended_papers": recommended_papers,
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
    logger.info(f"Chat request for paper: {id}")
    # Get the message from the request body
    body = await request.json()
    user_message = body.get("message", "")
    logger.info(f"Received message: {user_message[:50]}{'...' if len(user_message) > 50 else ''}")

    if not user_message:
        logger.error("Empty message received")
        raise HTTPException(status_code=400, detail="Message is required")

    # Check if we already have a chat for this paper
    if id in paper_chats:
        logger.info(f"Found existing chat for paper {id}")
        chat = paper_chats[id]["chat"]
    else:
        logger.warning(f"No existing chat found for paper {id}, creating new session")
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
    logger.info("Starting TLDRxiv application")
    uvicorn.run(app, port=8000, loop="asyncio")