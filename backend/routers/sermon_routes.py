from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.core.security import get_current_user
from backend.core.supabase_client import supabase_admin
from backend.llm_engine import generate_answer, is_model_available

router = APIRouter(prefix="/api/sermon", tags=["sermons"])

class SermonRequest(BaseModel):
    topic: str
    verse_context: Optional[str] = ""
    language: Optional[str] = "en"

class SermonResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None

def build_sermon_prompt(topic: str, verse: str, language: str) -> str:
    lang_instruction = "Respond in Tamil." if language and language.lower() == "ta" else "Respond in English."
    prompt = (
        f"[INST] You are an expert theologian and pastor. Create a structured, impactful 4-part sermon outline "
        f"based on the following topic and verse context. The sermon should include an Introduction, "
        f"Key Points, Practical Application, and Conclusion.\n\n"
        f"Topic: {topic}\n"
        f"Verse/Context: {verse}\n\n"
        f"{lang_instruction}\n"
        f"Format the output using simple HTML tags (e.g., <h3>, <h4>, <ul>, <li>, <strong>, <p>) so it renders beautifully in a web view. "
        f"DO NOT wrap the output in markdown code blocks like ```html. Output raw HTML only. [/INST]"
    )
    return prompt

@router.post("/generate", response_model=SermonResponse)
async def generate_sermon(request: SermonRequest, current_user: str = Depends(get_current_user)):
    """
    Generates a structured sermon outline using the local Mistral LLM model
    and optionally saves the result to the Supabase database.
    """
    if not is_model_available():
        raise HTTPException(
            status_code=503, 
            detail="AI Model is not loaded or available on the server."
        )
    
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required.")
        
    prompt = build_sermon_prompt(topic, request.verse_context, request.language)
    
    # Generate content using local LLM
    try:
        html_content = generate_answer(prompt, max_tokens=1500, temperature=0.7)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")
        
    sermon_data = {"html": html_content}
    
    # Attempt to save to Supabase using the admin client
    if supabase_admin:
        try:
            supabase_admin.table("sermons").insert({
                "user_id": current_user,
                "topic": topic,
                "verse_context": request.verse_context,
                "generated_content": sermon_data
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to save sermon to Supabase: {e}")
            # Do not fail the request if saving fails, as the sermon is still valid

    return SermonResponse(
        success=True,
        data={"html": html_content}
    )
