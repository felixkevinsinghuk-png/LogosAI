"""
Context Retrieval Module
Combines semantic vector search with original language data to retrieve
relevant Bible passages for a given user query.

This module is the knowledge retrieval backbone of the RAG pipeline.
It bridges the user's question to the Bible knowledge base before
the prompt is built and passed to the language model.
"""

from typing import List, Dict, Optional, Union
from backend.query_processor import process_query
from vector_store.vector_db import search, search_articles
from database.original_language import get_language_notes
from database.bible_loader import get_verse, get_book_name, load_bible


def retrieve_context(user_question: str, top_k: int = 5, score_threshold: float = 0.65) -> dict:
    """
    Retrieve contextually relevant Bible passages and original language
    information for a given user question.

    Workflow:
        1. Clean and process the user's question.
        2. Perform semantic similarity search over all Bible verses.
        3. Filter verses below the semantic confidence threshold.
        4. Extract any Strong's numbers from the question for language lookup.

    Args:
        user_question (str): Raw question from the user.
        top_k (int): Number of most relevant Bible passages to retrieve.
                     Default is 5.
        score_threshold (float): Minimum semantic similarity score to include
                                 a passage, reducing hallucination.

    Returns:
        dict: A dictionary containing:
            - "query" (str): The processed (cleaned) query string.
            - "passages" (list[dict]): Top-K relevant verse results. Each has:
                  - reference (str): e.g. "John 3:16"
                  - text (str): The verse text
                  - score (float): Semantic similarity score
            - "articles" (list[dict]): Top relevant article snippets. Each has:
                  - source (str): e.g. "BibleStudyTools"
                  - reference (str): e.g. "John 21:15-17"
                  - text (str): The snippet text
                  - score (float): Similarity score
            - "language_notes" (str): Original language info if Strong's numbers
                                      were present in the query, else "".
    """
    # Step 1: Clean and process the user's raw question
    clean_question = process_query(user_question)

    # Step 2: Semantic search — find the most similar Bible verses
    raw_passages = search(clean_question, top_k=top_k)

    # Step 3: Apply confidence threshold filtering (Anti-hallucination)
    # Filter out low relevance chunks
    passages = [p for p in raw_passages if p["score"] >= score_threshold]

    primary_passage_notes = ""
    
    # Step 4: Add sliding window context and generate Primary Passage notes
    if passages:
        bible_verses = load_bible()
        from database.original_language import get_language_notes_for_passage
        
        # The first passage in the sorted list is our primary choice
        primary_p = passages[0]
        primary_passage_notes = get_language_notes_for_passage(primary_p["text"], primary_p["book"])

        for p in passages:
            b = p["book"]
            c = p["chapter"]
            v = p["verse"]
            
            prev_v = get_verse(b, c, v - 1, verses=bible_verses)
            next_v = get_verse(b, c, v + 1, verses=bible_verses)
            
            texts = []
            start_v = v
            end_v = v
            
            if prev_v:
                texts.append(prev_v["text"])
                start_v = v - 1
                
            texts.append(p["text"])
            
            if next_v:
                texts.append(next_v["text"])
                end_v = v + 1
                
            if start_v != end_v:
                book_name = get_book_name(b)
                p["reference"] = f"{book_name} {c}:{start_v}-{end_v}"
                p["text"] = " ".join(texts)

    # Step 5: Extract Strong's language notes from the query (Supplemental)
    query_language_notes = get_language_notes(user_question)
    
    # Combine notes, prioritizing Primary Passage notes
    combined_notes = primary_passage_notes
    if query_language_notes:
        combined_notes += "\n\n[Supplemental Query Insights]\n" + query_language_notes

    # Step 6: Retrieve trusted contextual articles (New Priority 3)
    # Search for articles based on the processed question
    raw_articles = search_articles(clean_question, top_k=3)
    
    # Filter out low relevance articles
    articles = [a for a in raw_articles if a["score"] >= score_threshold]

    return {
        "query": clean_question,
        "passages": passages,
        "articles": articles,
        "language_notes": combined_notes.strip()
    }


def format_passages_for_display(passages: List[Dict]) -> str:
    """
    Format a list of retrieved Bible passages into a readable string.

    Used for debugging and logging retrieved context.

    Args:
        passages (list[dict]): List of passage dicts from the search results.

    Returns:
        str: Multi-line formatted string of all retrieved passages.
    """
    if not passages:
        return "No relevant passages found."

    lines = []
    for i, p in enumerate(passages, start=1):
        lines.append(
            f"{i}. {p['reference']} (score: {p['score']:.3f})\n"
            f"   \"{p['text']}\""
        )

    return "\n".join(lines)
