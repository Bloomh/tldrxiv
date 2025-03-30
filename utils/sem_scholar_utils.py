import os
import arxiv
from semanticscholar import SemanticScholar

ss_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
client = arxiv.Client()
sch = SemanticScholar(api_key=ss_api_key)


def get_ss_paper_info(arxiv_id: str):
    """Get specific paper information from Semantic Scholar.

    Only requests the TLDR field to minimize data transfer.
    """
    paper_id = "ARXIV:" + arxiv_id
    # Only request the tldr field to minimize data transfer
    paper_info = sch.get_paper(paper_id, fields=["tldr"]) # TODO: get citation

    return paper_info


def get_recommended_papers(arxiv_id: str, limit: int = 5):
    """Get recommended papers based on the given paper ID.

    Only requests essential fields to minimize data transfer.
    """
    paper_id = "ARXIV:" + arxiv_id

    # Only request fields that are actually displayed in the UI
    fields = [
        "title",
        "year",
        "authors.name",
        "citationCount"
    ]

    # Get the recommended papers with only necessary fields
    recommended_papers = sch.get_recommended_papers(paper_id, limit=limit, fields=fields)

    return recommended_papers


def get_paper_authors_info(arxiv_id: str, limit: int = 100):
    """Get a list of authors and their information for a given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the author information
    authors = sch.get_paper_authors(paper_id, limit=limit)[:limit]

    # get the information for each author
    author_ids = [author.authorId for author in authors]
    author_fields = ["name", "affiliations", "homepage", "paperCount", "citationCount", "hIndex"]
    author_info = sch.get_authors(author_ids, fields=author_fields)

    return author_info


def get_paper_citations(arxiv_id: str, limit: int = 20):
    """Get information about the citations for a given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the citation information
    # For citations, we need to use fields for the citingPaper object
    fields = [
        "citingPaper.title",
        "citingPaper.year",
        "citingPaper.authors",  # Request the full authors object
        "intents",
        "citingPaper.citationCount",
        "citingPaper.externalIds",
        "isInfluential"
    ]
    citation_info = sch.get_paper_citations(paper_id, limit=limit, fields=fields)[:limit]

    return citation_info


def get_paper_references(arxiv_id: str, limit: int = 20):
    """Get information about the references for a given paper ID."""
    paper_id = "ARXIV:" + arxiv_id

    # Get the reference information
    # For references, we need to use fields for the citedPaper object
    fields = [
        "citedPaper.title",
        "citedPaper.year",
        "citedPaper.authors",  # Request the full authors object
        "intents",
        "citedPaper.citationCount",
        "citedPaper.externalIds",
        "isInfluential"
    ]
    reference_info = sch.get_paper_references(paper_id, limit=limit, fields=fields)[:limit]

    return reference_info
