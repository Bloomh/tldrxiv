from semanticscholar import SemanticScholar
from collections import deque
from time import sleep
import os
import arxiv

ss_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
client = arxiv.Client()
sch = SemanticScholar(api_key=ss_api_key)


def get_recommended_papers(arxiv_id: str, limit: int = 5):
    """Get recommended papers based on the given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the paper details
    paper = sch.get_paper(paper_id)

    if not paper:
        # TODO: return an error screen
        return {"error": "Paper not found"}

    # Get the paper title
    title = paper.get("title", "Unknown Title")

    # Get the recommended papers
    recommended_papers = sch.get_recommended_papers(paper_id, limit=limit)

    return {
        "title": title,
        "recommended_papers": recommended_papers
    }


def get_paper_authors_info(arxiv_id: str, limit: int = 5):
    """Get a list of authors and their information for a given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the author information
    authors = sch.get_paper_authors(paper_id)

    # get the information for each author
    author_ids = [author.authorId for author in authors[:limit]]
    author_fields = ["name", "url", "affiliations", "homepage", "paperCount", "citationCount", "hIndex"]
    author_info = sch.get_authors(author_ids, fields=author_fields)

    return author_info


def get_paper_citations(arxiv_id: str):
    """Get information about the citations for a given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the citation information
    citation_info = sch.get_paper_citations(paper_id)

    return citation_info


def get_paper_references(arxiv_id: str):
    """Get information about the references for a given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the reference information
    reference_info = sch.get_paper_references(paper_id)

    return reference_info
