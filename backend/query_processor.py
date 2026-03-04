"""
Query Processing Module
Cleans and prepares user input for the semantic search pipeline.

Responsibilities:
- Strip HTML and special characters
- Normalize whitespace
- Lowercase for uniform search
- Prepare a clean query string for embedding
"""

import re
import html


def clean_query(text: str) -> str:
    """
    Sanitize raw user input by removing HTML, excess whitespace,
    and other noise.

    Args:
        text (str): Raw input string from the user.

    Returns:
        str: Cleaned text string.
    """
    # Decode HTML entities (e.g., &amp; → &)
    text = html.unescape(text)

    # Remove HTML tags (in case input arrives from a web form)
    text = re.sub(r"<[^>]+>", "", text)

    # Collapse multiple whitespace characters into a single space
    text = re.sub(r"\s+", " ", text)

    # Strip leading and trailing whitespace
    text = text.strip()

    return text


def process_query(text: str) -> str:
    """
    Full processing pipeline for a user question.

    Cleans the raw input and prepares it as a search-ready query string.
    The result is suitable for:
    - Embedding-based semantic search
    - Strong's number extraction
    - Prompt construction

    Args:
        text (str): Raw user question.

    Returns:
        str: Cleaned, normalized query string.
    """
    # Step 1: Clean and sanitize
    cleaned = clean_query(text)

    # Step 2: Return the cleaned string (lowercase for semantic consistency)
    # Note: we keep the original case for display, lowercasing only for search
    return cleaned


def normalize_for_search(text: str) -> str:
    """
    Normalize query text specifically for embedding and vector search.

    Applies lowercase and removes punctuation that is unlikely to affect
    semantic meaning, making the embedding more consistent.

    Args:
        text (str): Cleaned query text.

    Returns:
        str: Lowercase, punctuation-reduced string for embedding.
    """
    # Lowercase
    text = text.lower()

    # Keep alphanumeric, spaces, and apostrophes (important in Biblical names)
    text = re.sub(r"[^a-z0-9\s']", " ", text)

    # Collapse spaces again
    text = re.sub(r"\s+", " ", text).strip()

    return text
