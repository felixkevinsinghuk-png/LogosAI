"""
Controller Module
=================
Orchestrates the complete question-answering pipeline.

The controller is the central coordinator of the system. It receives
a user question, triggers each stage of the RAG pipeline in sequence,
and returns the final generated answer.

Pipeline sequence:
    1. Query Processing     → Clean and prepare user question
    2. Context Retrieval    → Semantic Bible verse lookup
    3. Prompt Construction  → Build structured LLM prompt
    4. LLM Inference        → Generate answer with Mistral-7B
"""

import re
import uuid
import threading
from backend.query_processor import process_query
from backend.context_retrieval import retrieve_context, format_passages_for_display
from backend.prompt_builder import build_prompt, build_simple_prompt
from backend.llm_engine import generate_answer, generate_answer_stream
from backend.input_validator import (
    validate_input,
    RESPONSE_OFF_TOPIC,
    RESPONSE_GIBBERISH,
    RESPONSE_UNCLEAR,
)


# In-memory storage for conversations
_conversations: dict[str, list[dict]] = {}
# Concurrency locks to prevent simultaneous inferences on the same session
_session_locks: dict[str, threading.Lock] = {}


def _get_session_lock(conversation_id: str) -> threading.Lock:
    if conversation_id not in _session_locks:
        _session_locks[conversation_id] = threading.Lock()
    return _session_locks[conversation_id]


def _build_canned_response(canned_text: str, conversation_id: str, query: str) -> dict:
    """Return a short-circuit response with a canned message — no LLM call."""
    return {
        "answer": canned_text,
        "passages": [],
        "articles": [],
        "language_notes": "",
        "query": query,
        "conversation_id": conversation_id
    }


def handle_question(user_input: str, top_k: int = 5, conversation_id: str | None = None) -> dict:
    """
    Process a user's Bible question through the full RAG pipeline
    and return a structured response.

    Args:
        user_input (str): Raw question text from the user.
        top_k (int): Number of Bible passages to retrieve for context.
        conversation_id (str | None): Session identifier.

    Returns:
        dict: Response dictionary containing:
            - "answer" (str): The generated text answer from the LLM.
            - "passages" (list[dict]): Retrieved Bible verse context.
            - "articles" (list[dict]): Retrieved article snippets.
            - "language_notes" (str): Any original language information.
            - "query" (str): The processed query that was used for search.
            - "conversation_id" (str): Uniquely identifies the ongoing session.
    """
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    with _get_session_lock(conversation_id):
        print(f"\n[Controller] Processing question for session {conversation_id}: {user_input[:80]}...")

        clean_text = user_input.strip().lower()
        check_text = re.sub(r'[^a-z0-9\s]', '', clean_text).strip()

        # ── Gate 1: Domain & Gibberish Validation ─────────────────────────────
        history = _conversations.get(conversation_id, [])
        has_history = len(history) > 0
        
        greetings = {
            "hi", "hello", "hey", "greetings", "good morning",
            "good evening", "good afternoon", "hi there", "hello there"
        }

        if check_text not in greetings:
            # Pass has_history to validator to allow context-aware follow-ups
            validation_result = validate_input(user_input, has_history=has_history)
            print(f"[Controller] Input validation result: {validation_result}")

            if validation_result == "gibberish":
                print("[Controller] Input flagged as gibberish. Returning canned response.")
                return _build_canned_response(RESPONSE_GIBBERISH, conversation_id, clean_text)

            if validation_result == "off_topic":
                print("[Controller] Input flagged as off-topic. Returning canned response.")
                return _build_canned_response(RESPONSE_OFF_TOPIC, conversation_id, clean_text)

            if validation_result == "unclear":
                print("[Controller] Input flagged as unclear. Returning clarification request.")
                return _build_canned_response(RESPONSE_UNCLEAR, conversation_id, clean_text)

        # ── Gate 2: Greeting Fast-Path ─────────────────────────────────────────
        if check_text in greetings:
            print("[Controller] Simple greeting detected. Returning fast response.")
            response = "Hello! I am LogosAI, your Bible contextual assistant. How can I help you study the Scriptures today?"
            history = _conversations.setdefault(conversation_id, [])
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            # Keep only the last 10 exchanges to prevent context explosion
            if len(history) > 20: 
                history = history[-20:]
                _conversations[conversation_id] = history

            return {
                "answer": response,
                "passages": [],
                "articles": [],
                "language_notes": "",
                "query": clean_text,
                "conversation_id": conversation_id
            }

        # Dynamic Transformation Detection (Word count, formatting, structure)
        intent = None
        lower_input = user_input.lower()
        
        # 1. Detect arbitrary word count
        word_count_match = re.search(r"(\d+)\s*words?", lower_input)
        word_count = word_count_match.group(1) if word_count_match else None
        
        # 2. Extract structural/formatting instructions
        format_type = None
        if "single paragraph" in lower_input or "one paragraph" in lower_input:
            format_type = "single_paragraph"
        elif "two paragraphs" in lower_input:
            format_type = "two_paragraphs"
        elif "three paragraphs" in lower_input:
            format_type = "three_paragraphs"
        elif "bullet points" in lower_input or "bullets" in lower_input:
            format_type = "bullets"
        elif "bullet" in lower_input:
            format_type = "bullets"

        # 3. Consolidate into intent mapping
        if word_count or format_type:
            intent = {
                "type": "transform",
                "word_count": word_count,
                "format": format_type,
                "raw": lower_input
            }
        elif "summarize" in lower_input or "summary" in lower_input or "short version" in lower_input:
            intent = "summarize"
        elif "simplify" in lower_input or "simple words" in lower_input:
            intent = "simplify"
        elif "detail" in lower_input or "expand" in lower_input or "elaborate" in lower_input:
            intent = "detail"
        elif "spiritual" in lower_input:
            intent = "spiritual"

        # Step 1: Retrieve contextual Bible passages and language notes
        context = retrieve_context(user_input, top_k=top_k)

        passages = context["passages"]
        articles = context["articles"]
        language_notes = context["language_notes"]
        clean_query = context["query"]

        print(f"[Controller] Retrieved {len(passages)} passages and {len(articles)} articles.")
        if language_notes:
            print(f"[Controller] Language notes found for Strong's references.")

        # Step 2: Build the prompt using conversation history and intent
        if passages:
            prompt = build_prompt(clean_query, passages, articles, language_notes, history, intent=intent)
        else:
            # No matching passages found — use a simpler prompt
            prompt = build_simple_prompt(clean_query, history, intent=intent)

        # Step 3: Generate answer with the local LLM
        print("[Controller] Sending prompt to language model...")
        answer = generate_answer(prompt)

        # Step 4: Post-processing (Anti-hallucination safeguard)
        if not articles:
            # Check for common source names we support
            sources = ["BibleStudyTools", "GotQuestions", "BlueLetterBible", "EnduringWord", "BibleHub"]
            for source in sources:
                if source in answer:
                    # If a source is mentioned but no context was provided, replace with fallback
                    fallback = "No trusted contextual sources were found for this question."
                    answer = answer.replace(source, f"[Source citation removed: {fallback}]")

        print(f"[Controller] Answer generated ({len(answer)} characters).")

        # Update Conversation History
        if conversation_id not in _conversations:
            _conversations[conversation_id] = []
        _conversations[conversation_id].append({"role": "user", "content": user_input})
        _conversations[conversation_id].append({"role": "assistant", "content": answer})

        # Memory bounds (last 10 interactions / 20 messages)
        if len(_conversations[conversation_id]) > 20:
             _conversations[conversation_id] = _conversations[conversation_id][-20:]

        return {
            "answer": answer,
            "passages": passages,
            "articles": articles,
            "language_notes": language_notes,
            "query": clean_query,
            "conversation_id": conversation_id
        }


def handle_question_stream(user_input: str, top_k: int = 5):
    """
    Generator that orchestrates the RAG pipeline and yields:
    1. A metadata dictionary (passages, query, etc.)
    2. Tokens from the LLM
    """
    print(f"\n[Controller] Streaming question: {user_input[:80]}...")

    # 1. Retrieve context (Same as handle_question)
    context = retrieve_context(user_input, top_k=top_k)
    passages = context["passages"]
    articles = context["articles"]
    language_notes = context["language_notes"]
    clean_query = context["query"]

    # Yield metadata first so the frontend can render the sidebar/passages
    yield {
        "type": "metadata",
        "passages": passages,
        "articles": articles,
        "language_notes": language_notes,
        "query": clean_query
    }

    # 2. Build Prompt
    if passages:
        prompt = build_prompt(clean_query, passages, articles, language_notes)
    else:
        prompt = build_simple_prompt(clean_query)

    # 3. Stream LLM Answer
    print("[Controller] Starting LLM stream...")
    for token in generate_answer_stream(prompt):
        yield {
            "type": "token",
            "text": token
        }
