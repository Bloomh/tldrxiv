from google import genai
import httpx
import io
from google.genai import types
from dotenv import load_dotenv
import os
from typing import Iterable

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_KEY"))


def gemini_upload_file(pdf_url: str) -> types.Document:
    """
    Upload a PDF file to Gemini

    Args:
        pdf_url (str): URL to the PDF file

    Returns:
        Document: Document object from Gemini
    """
    doc_io = io.BytesIO(httpx.get(pdf_url).content)
    document = client.files.upload(
        file=doc_io,
        config=dict(mime_type='application/pdf')
    )

    return document


def create_gemini_chat(doc: types.Document, model: str = "gemini-2.0-flash-lite") -> types.Chat:
    """
    Creates a chat with a faux history that includes file upload

    Args:
        doc (Document): Document to upload (Document object from gemini_upload_file)
        model (str, optional): Model to use. Defaults to "gemini-2.0-flash-lite".

    Returns:
        Chat: Chat object from Gemini
    """
    chat = client.chats.create(
        model=model,
        history=[
            types.Content(
                role="user",
                parts=[
                    types.Part(text="Here's a document I want to discuss"),
                    types.Part.from_uri(file_uri=doc.uri, mime_type="application/pdf")
                ]
            ),
            types.Content(
                role="model",
                parts=[types.Part(text="I've reviewed the document. What would you like to know?")]
            )
        ]
    )

    return chat

def gemini_ask_question(chat: types.Chat, prompt: str) -> Iterable[str]:
    """
    Ask a question to Gemini. Note that the response is a stream of text chunks.

    Args:
        chat (Chat): Chat object from create_gemini_chat
        prompt (str): Question to ask

    Yields:
        str: Text chunks from the response
    """
    response = chat.send_message_stream(prompt)

    for chunk in response:
        yield chunk.text