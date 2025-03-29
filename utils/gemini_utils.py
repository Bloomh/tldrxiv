from google import genai
from google.genai.chats import Chat
import httpx
import io
from google.genai import types
from dotenv import load_dotenv
import os
from typing import Iterator

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_KEY"))


def gemini_upload_file(pdf_content: bytes) -> types.File:
    """
    Upload a PDF file to Gemini

    Args:
        pdf_content (bytes): PDF file content

    Returns:
        types.File: File object from Gemini
    """
    doc_io = io.BytesIO(pdf_content)
    document = client.files.upload(
        file=doc_io,
        config=dict(mime_type='application/pdf'),
    )

    return document


def create_gemini_chat(doc: types.File, model: str = "gemini-2.0-flash-lite") -> Chat:
    """
    Creates a chat with a faux history that includes file upload

    Args:
        doc (types.File): File to upload (File object from gemini_upload_file)
        model (str, optional): Model to use. Defaults to "gemini-2.0-flash-lite".

    Returns:
        Chat: Chat object from Gemini
    """
    # Hard-coded system prompt
    system_prompt = (
        "You are a helpful research assistant that helps users understand academic papers. "
        "You should provide clear, concise explanations of complex concepts in the paper. "
        "When asked about the paper, focus on explaining the key ideas, methodology, results, and implications. "
        "If you're unsure about something, acknowledge the limitations of your understanding rather than making up information."
        "Do not answer unrelated questions that are not about the paper or any relevant fields."
        "You can write in markdown and should include latex equations, but do not surround the latex with backticks. For example, write $x_i$, NOT `x_i` or `$x_i$`."
    )

    # Create history
    history = []

    # Add document upload to history
    history.append(
        types.Content(
            role="user",
            parts=[
                types.Part(text="I would like to discuss this paper. Here is the document:"),
                types.Part.from_uri(file_uri=doc.uri, mime_type="application/pdf")
            ]
        )
    )

    # Add initial model response
    history.append(
        types.Content(
            role="model",
            parts=[types.Part(text="I've reviewed the document. What would you like to know?")]
        )
    )

    # Create the chat
    chat = client.chats.create(
        model=model,
        history=history,
        config={
            'system_instruction': system_prompt
        }
    )

    return chat

def gemini_ask_question(chat: Chat, prompt: str) -> Iterator[str]:
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