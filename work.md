# RhemaLight AI — Features, Options & How It Works

## Overview

**RhemaLight AI** is a locally-running, AI-powered Bible study and church management platform. It combines a Retrieval-Augmented Generation (RAG) language model with structured liturgical data, multi-lingual Bible content, and community tools — all served through a clean, modern web interface.

---

## How to Run

```bash
cd "/Volumes/FELIX SSD/LogosAI"
python main.py
```
Then open your browser at: **http://localhost:8000**

> ⚠️ Do NOT open `index.html` directly or use Live Server. All JS/CSS files are served only through the FastAPI backend.

---

## Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI (Python) | REST API, static file serving, AI inference |
| **AI Engine** | Mistral-7B (local) | Scripture-based question answering |
| **Vector Store** | FAISS | Semantic Bible passage retrieval |
| **Database** | Supabase (PostgreSQL) | User profiles, history, plans, songs |
| **Frontend** | HTML + Vanilla JS + CSS | Single-page application UI |
| **Auth** | Supabase Auth (JWT) | User login, session management |

---

## Features & How Each Works

---

### 1. 🤖 Ask AI (Bible Chat) — `⌘K`
**Purpose:** Ask any Bible-related question and get a contextual AI-generated answer with scripture references.

**How it works:**
1. The user types a question into the chat input.
2. The question is sent to `POST /chat` on the FastAPI backend.
3. The controller runs a FAISS vector search to retrieve the most semantically similar Bible passages.
4. These passages are injected into the prompt context sent to the local Mistral-7B model.
5. The AI generates a grounded answer, citing specific scripture.
6. The response is displayed in a chat bubble with an expandable "Sources" section showing the matched passages.

---

### 2. 📖 Read Bible
**Purpose:** Read the full Bible in English or Tamil, chapter by chapter.

**How it works:**
- User selects a Bible version (e.g., KJV, BSI Tamil), a book, and a chapter.
- `GET /api/bible/passage` fetches the chapter verses from the backend JSON data store.
- Verses are rendered in the reading area with verse numbers.
- `GET /api/bible/chapter-count` ensures the chapter selector only shows valid chapters.
- Tamil scripture uses the `Anek Tamil` Google Font for correct rendering.

---

### 3. 📅 Reading Plans
**Purpose:** Follow structured daily Bible reading schedules and track your progress.

**How it works:**
- Plans are stored in Supabase and fetched via `GET /api/plans`.
- Each plan has a list of daily scripture readings.
- Completed days are tracked and a progress bar is updated.
- Linked to the Accountability streak system.

---

### 4. ❤️ Accountability & Streaks
**Purpose:** Track daily devotional consistency and build a prayer/reading streak.

**How it works:**
- Each day the user completes a reading or devotional activity, a streak entry is recorded via `POST /api/streak`.
- The streak counter (consecutive days) is fetched via `GET /api/streak` and displayed on the dashboard.
- Streaks reset if a day is missed.

---

### 5. 📚 Library
**Purpose:** Save, organise, and revisit favourite Bible passages and study notes.

**How it works:**
- Saved entries are stored in Supabase.
- Users can add a passage reference, personal notes, and tags.
- The Library view fetches and renders saved items via the history/profile APIs.

---

### 6. 🔍 Study Guides
**Purpose:** Access pre-built topical Bible study guides on key theological themes.

**How it works:**
- Study guides are static structured content served from the backend.
- Each guide groups relevant scripture references under a theme (e.g., Faith, Prayer, Grace).
- Clicking a reference opens the Bible Reader at that passage.

---

### 7. ✏️ Sermon Builder
**Purpose:** AI-assisted tool for ministers and preachers to generate structured sermon outlines.

**How it works:**
- User provides a topic, a scripture text, and optional sermon style preferences.
- The request is sent to `POST /api/sermon`.
- The AI generates a full outline: Introduction, 3 main points with supporting scriptures, Illustration, Application, and Conclusion.
- The result is displayed in a formatted, printable content area.

---

### 8. 🗓️ Service Orders (CSI Liturgy Planner)
**Purpose:** An interactive, accordion-style Order of Service for CSI church services.

**How it works:**
- User selects a service type from the dropdown:
  - **English First Service** — Full Sunday liturgy in English
  - **Tamil Order of Service** — Full Sunday liturgy in Tamil
  - **Bilingual (இருமொழி)** — English and Tamil side-by-side per section
  - **Wedding Service** — Full CSI wedding liturgy in English or Tamil
- `GET /api/service?type=sunday&lang=en` fetches the structured liturgy from the backend.
- Each section (Invocation, Confession, Creed, Sermon, etc.) is rendered as a collapsible accordion card.
- Clicking a card expands it to show the full text (Minister/Congregation parts, rubrics, scripture references).
- **Expand All / Collapse All** buttons control all cards at once.
- **Search** filters visible sections by keyword in real time.
- The print button triggers a browser print dialog optimised for clean paper output.

---

### 9. 🎵 Worship Hub & Playlists
**Purpose:** Manage and curate worship song playlists for church services.

**How it works:**
- Songs are stored in Supabase and fetched via `GET /api/songs`.
- Users can create named playlists and add YouTube-embedded songs to them.
- Songs can be added by title, artist, and YouTube URL.
- Playlists are saved per user account and retrieved via `GET /api/playlists`.

---

### 10. 👥 Community Group Chat
**Purpose:** Real-time Bible study group chat rooms for small groups or cells.

**How it works:**
- **Create**: A user enters their name and a group name → a unique 6-character room code is generated.
- **Join**: Another user enters the room code to join the group.
- Messages are sent over a **WebSocket** connection (`ws://localhost:8000/ws/{room_code}/{username}`).
- All participants in the same room code receive messages in real time.
- The group leader's messages are shown as the host.

---

### 11. 🔔 Notifications
**Purpose:** In-app alert system for reminders and app events.

**How it works:**
- User clicks the bell icon in the top header to open the Notifications modal.
- Notifications are fetched from `GET /api/notifications` and rendered as a list.
- Unread count badge is shown on the bell icon.

---

### 12. 👤 User Profile & Auth
**Purpose:** Secure user accounts with personalisation.

**How it works:**
- Authentication is powered by **Supabase Auth**.
- The user can log in via email/password.
- On login, a JWT is stored and appended to all subsequent API calls as an `Authorization: Bearer <token>` header.
- The backend validates tokens via `get_current_user()` from `backend/core/security.py`.
- Profile data (name, avatar initial) is stored in Supabase and shown in the top-right avatar button.

---

## Key API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serves the frontend HTML |
| `POST` | `/chat` | AI Bible Q&A |
| `GET` | `/api/service` | CSI Liturgy data |
| `GET` | `/api/bible/passage` | Fetch Bible chapter |
| `GET` | `/api/bible/chapter-count` | Valid chapter count |
| `GET` | `/api/bible/votd` | Verse of the Day |
| `POST` | `/api/sermon` | Generate sermon outline |
| `GET` | `/api/songs` | Fetch songs |
| `GET/POST` | `/api/playlists` | Manage playlists |
| `GET` | `/api/streak` | Get devotional streak |
| `GET` | `/api/history` | Chat history |
| `WS` | `/ws/{room}/{name}` | Group chat WebSocket |

---

## Static Files (Frontend)

All frontend files are served by FastAPI under the `/static/` route, mapped to the `/frontend/` directory:

| File | Purpose |
|---|---|
| `index.html` | Main HTML shell for the single-page application |
| `style.css` | All UI styles including dark theme, glassmorphism, animations |
| `app_v2.js` | Core application logic, navigation, API calls, UI rendering |
| `liturgy-data.js` | Local CSI liturgy data dictionary (backup/reference) |
| `bible-engine.js` | BibleEngine class for fetching scripture from the backend |
| `supabase-client.js` | Supabase Auth client initialisation |
| `group.js` | Group chat WebSocket connection logic |
