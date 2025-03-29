import arxiv
import httpx

ach = arxiv.Client()


def get_paper_info(arxiv_id: str):
    """Get information about a paper from its arXiv ID."""
    try:
        search = arxiv.Search(id_list=[arxiv_id])

        for result in ach.results(search):
            paper = result

            return {
                "id": arxiv_id,
                "title": paper.title,
                "summary": paper.summary,
                "authors": paper.authors,
                "published_date": paper.published,
                "categories": paper.categories,
                "doi": paper.doi,
                "pdf_link": paper.pdf_url,
                "url": f"https://arxiv.org/abs/{arxiv_id}"
            }
    except Exception as e:
        return {"error": f"Error fetching paper: {str(e)}"}

def download_paper_pdf(paper: dict):
    """Download paper PDF and return the binary content."""
    # Get PDF URL from paper info or construct it from ID
    if "pdf_link" in paper and paper["pdf_link"]:
        pdf_url = paper["pdf_link"]
    elif "id" in paper:
        pdf_url = f"https://arxiv.org/pdf/{paper['id']}"
    else:
        return {"error": "No PDF link or ID available"}

    # Download the PDF
    try:
        response = httpx.get(pdf_url)
        if response.status_code != 200:
            return {"error": f"Failed to download paper: HTTP {response.status_code}"}

        # Return the binary content
        return response.content
    except Exception as e:
        return {"error": f"Error downloading PDF: {str(e)}"}

