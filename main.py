from typing import Optional

from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
import os

import uvicorn

# Importing our utils
from utils.arxiv_utils import get_paper_info, download_paper_pdf

load_dotenv()

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/abs/{id}")
@app.get("/pdf/{id}")
@app.get("/html/{id}")
async def read_item(request: Request, id: str, format: str = None):
    """
    Single endpoint that handles paper info and PDF display.

    Args:
        request: FastAPI request object
        middle: Path component (abs, pdf, etc.)
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

    # If format=pdf is specified, return the raw PDF
    if format == "pdf":
        if "error" in paper:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": paper["error"]}
            )

        pdf_content = download_paper_pdf(paper)
        if isinstance(pdf_content, dict) and "error" in pdf_content:
            raise HTTPException(status_code=500, detail=pdf_content["error"])

        # Return the PDF directly with inline display (not attachment)
        return Response(
            content=pdf_content,
            media_type="application/pdf"
        )

    # Otherwise, just get paper info

    # Create PDF embed URL - using the same endpoint with format=pdf
    pdf_embed_url = f"/abs/{id}?format=pdf"

    # Return the HTML template with paper data
    return templates.TemplateResponse(
        "paper.html",
        {
            "request": request,
            "paper": paper,
            "pdf_embed_url": pdf_embed_url
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8000, loop="asyncio")