# RHEMALIGHT AI — FULL MVP BUILD SPEC (ZERO-COST)

## Project Name

RhemaLight AI

---

## Core Goal

Transform the existing prototype into a **fully working, zero-cost MVP** with:

* Real backend (FastAPI)
* Supabase (Auth + DB + Realtime)
* Local AI (no paid APIs)
* Full Bible integration (Tamil + English)
* Interactive CSI Order of Service
* No placeholder or fake features

---

## 🔒 Zero-Cost Enforcement

### Allowed

* Supabase Free Tier
* FastAPI + Uvicorn
* Local LLM (llama.cpp / mlx)
* ChromaDB (local)
* Static JSON datasets
* Vanilla JS frontend

### Strictly Not Allowed

* OpenAI / Gemini / Anthropic APIs
* Paid hosting / DB / GPU
* Paid Bible APIs
* Paid email services

---

## 🧠 System Architecture

### Frontend

* HTML / CSS / JS (modularized)
* API client layer
* Auth handler
* Feature modules

### Backend (FastAPI)

```
/api
 ├── sermon
 ├── bible
 ├── service
 ├── history
 ├── plans
 ├── profile
 ├── songs
 ├── notifications
```

### Database

* Supabase PostgreSQL
* Row Level Security enabled

### Local Systems

* Bible dataset → JSON
* LLM → local GGUF
* Embeddings → MiniLM
* Vector DB → ChromaDB

---

## 📖 Bible System (CRITICAL FEATURE)

### Requirements

Include **FULL Bible**:

* Old Testament + New Testament
* All books, chapters, verses

### Languages

* English
* Tamil

### Versions (Minimum 3)

* KJV (EN)
* ESV or NIV (EN)
* Tamil BSI

---

### Storage (MANDATORY APPROACH)

Use **static JSON files**:

```
/data/bible/
  ├── en_kjv.json
  ├── en_esv.json
  ├── ta_bsi.json
```

### Structure

```
{
  "book": "John",
  "chapter": 3,
  "verse": 16,
  "text": "For God so loved the world..."
}
```

---

### API Endpoints

```
GET /api/scripture/{version}/{book}/{chapter}
GET /api/bible/votd?lang=en
```

---

### Features

* Verse navigation
* Language toggle
* Dual view (EN + TA side-by-side)
* Keyword search
* Lazy loading (no full preload)

---

## ✝️ CSI ORDER OF SERVICE (INTERACTIVE)

### Requirement

Build **fully interactive service system**:

* Each section = clickable
* On click → expand full content

---

### Sections

* Invocation
* Confession
* Absolution
* Apostles’ Creed
* Lord’s Prayer
* OT Reading
* Psalm
* Epistle
* Gospel
* Sermon
* Offering
* Intercession
* Benediction

---

### Behavior

| Action          | Result         |
| --------------- | -------------- |
| Click section   | Expand content |
| Click again     | Collapse       |
| Switch language | Reload content |

---

### Data Structure

```
{
  "section": "Apostles Creed",
  "language": "EN",
  "content": "I believe in God...",
  "type": "static"
}
```

Scripture-based:

```
{
  "section": "Gospel Reading",
  "reference": "John 3:16",
  "text_en": "...",
  "text_ta": "...",
  "type": "scripture"
}
```

---

### Content Sources

#### English

* CSI official order references (provided PDFs)

#### Tamil

* ஆராதனை முறைகள் (Goldwyn Sudhakar)

#### Wedding Service

* Tamil CSI wedding liturgy
* Include:

  * vows
  * ring exchange
  * blessing

---

### API

```
GET /api/service?type=sunday&lang=en
GET /api/service?type=wedding&lang=ta
```

---

## 🤖 AI SERMON BUILDER

### Endpoint

```
POST /api/sermon/generate
```

### Rules

* Use ONLY local LLM
* Structured JSON output:

```
{
  "title": "",
  "introduction": "",
  "points": [],
  "application": "",
  "conclusion": ""
}
```

---

## 📊 Accountability System

### Logic (Strict)

* Same day → no increment
* Yesterday → +1
* Missed → reset to 1

---

## 🎵 Worship Hub

* Data from Supabase
* Tamil + English songs
* Lyrics view
* Optional audio

---

## 👥 Community Chat

* Supabase Realtime
* Room code (6 char)
* Max 13 users
* Live messaging

---

## 📚 Reading Plans

* Start / Continue / Complete
* Stored in DB
* Tracks daily progress

---

## 👤 Profile System

* Name
* Language
* Theme
* Password reset (Supabase)

---

## 🎨 UI REDESIGN (IMPORTANT)

### Layout

* Left sidebar (fixed)
* Right content area
* Centered container

---

### Alignment

* Grid system
* Equal spacing (8px scale)
* Card-based UI

---

### Color System

* Background → soft white
* Primary → deep blue / violet
* Accent → soft gold
* Text → dark gray

---

### Components

* Rounded cards
* Soft shadows
* Smooth hover effects

---

### Chat UI

* User → right
* AI → left
* Input fixed bottom

---

## 🔐 Security

* JWT validation (Supabase)
* Protected endpoints
* RLS policies

---

## 🧩 API Standard

### Success

```
{
  "success": true,
  "data": {},
  "error": null
}
```

### Error

```
{
  "success": false,
  "error": {
    "message": ""
  }
}
```

---

## 🚫 Remove All Fake Logic

Replace:

* setTimeout mocks
* static arrays
* fake success messages

With:

* real API calls
* real DB data

---

## 🧪 Testing

### Must Work

* Login / Signup
* Sermon generation
* Verse of day
* Bible reading
* Service expansion
* Song playback (optional)
* Streak update
* Plan completion

---

## ⚡ Performance Rules

* Lazy load scripture
* Cache verse of day
* Paginate history
* Debounce search

---

## 🧠 Definition of Done

App is complete ONLY IF:

* No fake features remain
* Bible fully accessible
* Tamil + English working
* Service is interactive
* Backend fully connected
* Supabase handles all persistence
* AI runs locally
* UI is clean and aligned
* Zero paid dependency

---

## FINAL RULE

If something cannot be built with zero cost:

→ Build the **best possible free version**
→ DO NOT fake functionality
→ DO NOT simulate backend behavior

---
