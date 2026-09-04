"""
API Module
FastAPI application that exposes the Bible chatbot as a web service.

Endpoints:
    GET  /          — Serves the chat frontend (index.html)
    POST /chat      — Accepts a question, returns a generated answer
    GET  /health    — Health check endpoint
    GET  /status    — Reports model and index availability

Static files for the frontend are served from the 'frontend/' directory.
"""

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

from backend.core.security import get_current_user

from backend.controller import handle_question, handle_question_stream
from backend.llm_engine import is_model_available
from vector_store.vector_db import is_indexed
from backend.group_chat import create_room, validate_room, manager, get_room_info
from backend.routers import sermon_routes, history_routes, bible_routes, song_routes, plan_routes, streak_routes, profile_routes, notification_routes

# Resolve path to the frontend directory
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# FastAPI app initialization
app = FastAPI(
    title="RhemaLight AI — Bible Contextual Assistant",
    description="A locally-running RAG-based Bible AI assistant using Mistral-7B.",
    version="1.0.0"
)

# Register routers
app.include_router(sermon_routes.router)
app.include_router(history_routes.router)
app.include_router(bible_routes.router)
app.include_router(song_routes.router)
app.include_router(plan_routes.router)
app.include_router(streak_routes.router)
app.include_router(profile_routes.router)
app.include_router(notification_routes.router)
from backend.routers import service_routes, playlist_routes
app.include_router(service_routes.router)
app.include_router(playlist_routes.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",  # Common Vite port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving
# Mount the frontend/static directory so CSS, and JS are served under /static
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
if os.path.isdir(STATIC_DIR):
    app.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR),
        name="static"
    )

@app.on_event("startup")
async def startup_event():
    """
    Preload models into memory when the server starts.
    """
    # Disabling preload for debugging
    pass
    # from backend.llm_engine import load_model, is_model_available
    # from vector_store.embedder import _get_model
    # from vector_store.vector_db import is_indexed

    # if is_indexed():
    #     _get_model()
    
    # if is_model_available():
    #     load_model()


# Request / Response Models

class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="The Bible question to answer.",
        example="What does John 3:16 mean?"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the conversational session. If none is provided, a new session is started."
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=15,
        description="Number of Bible passages to retrieve as context."
    )


class PassageResult(BaseModel):
    """A single retrieved Bible passage."""
    reference: str
    text: str
    score: float


class ChatResponse(BaseModel):
    """Response body from the /chat endpoint."""
    answer: str
    query: str
    passages: list[PassageResult]
    language_notes: str
    conversation_id: str


class GroupCreateRequest(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=100)


# Routes

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def serve_frontend():
    """
    Serve the chat frontend HTML page.

    Returns:
        FileResponse: The index.html file from the frontend directory.
    """
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.isfile(index_path):
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(index_path)


@app.post("/chat")
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    try:
        result = handle_question(
            request.question,
            top_k=request.top_k,
            conversation_id=request.conversation_id
        )
        return {
            "success": True,
            "data": {
                "answer": result["answer"],
                "query": result["query"],
                "passages": result["passages"],
                "language_notes": result.get("language_notes", ""),
                "conversation_id": result["conversation_id"]
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"message": str(e)}
        }


# /chat/stream removed as per new non-streaming requirement.


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.

    Returns:
        JSONResponse: {"status": "ok"}
    """
    return JSONResponse({"status": "ok"})


@app.get("/status")
async def system_status():
    """
    Report the current system status, including model and index availability.

    Returns:
        JSONResponse: Status dict with model_available and bible_indexed flags.
    """
    return JSONResponse({
        "status": "running",
        "model_available": is_model_available(),
        "bible_indexed": is_indexed(),
        "model_info": "Mistral-7B Instruct (GGUF)",
        "embedding_model": "all-MiniLM-L6-v2"
    })

@app.get("/api/diag")
async def diagnostic():
    """Diagnostic endpoint to check environment and data paths."""
    from backend.core.config import settings
    from database.bible_loader import DATA_DIR, VERSION_SOURCES
    
    bible_status = {}
    for code in VERSION_SOURCES:
        path = os.path.join(DATA_DIR, f"{code}.json")
        bible_status[code] = {
            "path": path,
            "exists": os.path.exists(path),
            "size": os.path.getsize(path) if os.path.exists(path) else 0
        }

    return {
        "env": {
            "SUPABASE_URL": settings.SUPABASE_URL,
            "SUPABASE_SERVICE_ROLE_KEY_SET": bool(settings.SUPABASE_SERVICE_ROLE_KEY),
            "SUPABASE_JWT_SECRET_SET": bool(settings.SUPABASE_JWT_SECRET),
            "SCRIPTURE_DATA_PATH_SET": settings.SCRIPTURE_DATA_PATH
        },
        "bible_loader": {
            "DATA_DIR": DATA_DIR,
            "files": bible_status
        },
        "cwd": os.getcwd()
    }

@app.post("/api/gemini/chat")
async def gemini_chat_proxy(payload: dict):
    """Proxy endpoint for frontend Gemini requests to avoid exposing the API key."""
    import requests
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured on the server.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Group Chat Routes ---

@app.post("/group/create")
async def create_group(request: GroupCreateRequest, current_user: str = Depends(get_current_user)):
    """Creates a new isolated chat group and returns a unique 6-character alphanumeric room code."""
    group_name = request.group_name.strip()
    if not group_name:
        raise HTTPException(status_code=400, detail="Group Name cannot be empty.")
    
    room_code = create_room(group_name)
    return {"room_code": room_code}


@app.get("/group/validate/{room_code}")
async def validate_group(room_code: str):
    """Validates if a 6-character room code exists."""
    if validate_room(room_code):
        info = get_room_info(room_code)
        
        # Check limit early
        if info and info["participants"] >= info["max"]:
             return {"valid": False, "full": True, "room_code": room_code.upper(), "info": info}
             
        return {"valid": True, "full": False, "room_code": room_code.upper(), "info": info}
    raise HTTPException(status_code=404, detail="Invalid Room Code. Please check the code and try again.")


@app.websocket("/ws/group/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, name: str = "Anonymous"):
    """
    WebSocket connection for an isolated room. 
    Accepts incoming messages and broadcasts them to all clients connected to 'room_code'.
    Room code is strictly a 6-character string.
    """
    # Force uppercase to stay consistent
    internal_code = room_code.upper()
    
    if not validate_room(internal_code):
        await websocket.close(code=1008, reason="Room does not exist.")
        return

    # Add connection to connection manager
    success = await manager.connect(internal_code, name, websocket)
    if not success:
        # Connect handles sending the close status directly if full.
        return

    try:
        while True:
            # We expect JSON: { "message": "hello!" }
            data = await websocket.receive_json()
            # Safety checks
            if "message" in data:
                # Add username and broadcast
                payload = {
                    "name": name,
                    "message": data["message"]
                }
                await manager.broadcast(internal_code, payload)

    except WebSocketDisconnect:
        await manager.disconnect(internal_code, name, websocket)
        
    except Exception as e:
        print(f"WebSocket error in room {internal_code}: {e}")
        await manager.disconnect(internal_code, name, websocket)
