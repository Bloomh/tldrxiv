from google import genai
from google.genai.chats import Chat
import io
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
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


def create_gemini_chat(doc: types.File, context_message: str = "", model: str = "gemini-2.0-flash") -> Chat:
    """
    Creates a chat with a faux history that includes file upload

    Args:
        doc (types.File): File to upload (File object from gemini_upload_file)
        model (str, optional): Model to use. Defaults to "gemini-2.0-flash".

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

    if context_message:
        history.append(
            types.Content(
                role="user",
                parts=[types.Part(text=context_message)]
            )
        )

    search_tool = Tool(
    google_search = GoogleSearch()
)

    # Create the chat
    chat = client.chats.create(
        model=model,
        history=history,
        config={
            'system_instruction': system_prompt,
            'tools': [search_tool]
        }
    )

    return chat


def gemini_ask_question(chat: Chat, prompt: str) -> Iterator[str]:
    """
    Ask a question to Gemini. Note that the response is a stream of text chunks.
    Logs Google Search queries and URLs accessed by the model.

    Args:
        chat (Chat): Chat object from create_gemini_chat
        prompt (str): Question to ask

    Yields:
        str: Text chunks from the response
    """
    # Send the message to get the streamed response
    response = chat.send_message_stream(prompt)
    
    # Track search queries and URLs we've seen to avoid duplicates
    seen_queries = set()
    seen_urls = set()
    
    # Process each chunk in the response
    for chunk in response:
        # Check for search information in candidates
        if hasattr(chunk, 'candidates') and chunk.candidates:
            for candidate in chunk.candidates:
                # Extract search queries from grounding_metadata
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    # Get search queries
                    if hasattr(candidate.grounding_metadata, 'web_search_queries'):
                        queries = candidate.grounding_metadata.web_search_queries
                        if queries:
                            for query in queries:
                                if query and query not in seen_queries:
                                    print(f"Google Search Query: {query}")
                                    seen_queries.add(query)

                    # Get grounding chunks with URLs
                    if hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                        chunks = candidate.grounding_metadata.grounding_chunks
                        if chunks:
                            for chunk_item in chunks:
                                if hasattr(chunk_item, 'web') and chunk_item.web:
                                    if hasattr(chunk_item.web, 'uri') and chunk_item.web.uri:
                                        url = chunk_item.web.uri
                                        if url and url not in seen_urls:
                                            print(f"Google Search URL: {url}")
                                            seen_urls.add(url)

        # Yield the text from the chunk
        if chunk.text:
            yield chunk.text


def generate_podcast_script(pdf_bytes: bytes, model_name="gemini-1.5-pro-latest") -> str:
    """Generate podcast script from PDF content"""
    print("Generating podcast script...")
    pdf_file = gemini_upload_file(pdf_bytes)

    prompt = """Create a podcast script summary of this research paper for a general audience. Follow these rules:
    1. Structure with: introduction to the field, key research question, methodology overview, main findings, and significance
    2. Write in natural, conversational paragraphs that flow like a real podcast
    3. Absolutely DO NOT include phrases like:
       - "Here's a 5-minute podcast script..."
       - "Welcome to this podcast about..."
       - "Let's dive in"
       - Any other meta commentary about the script itself
    4. Start immediately with substantive content about the paper
    5. Use engaging segues between sections but keep them natural
    6. Maintain a professional yet accessible tone"""

    response = create_gemini_chat(pdf_file).send_message([
        prompt
    ])

    return response.text

