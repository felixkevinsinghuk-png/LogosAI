# RhemaLight AI Backend Implementation using Supabase

## Objective

Convert the existing RhemaLight AI frontend prototype into a fully functional application using **Supabase as the backend**.

The system must support authentication, database storage, real-time communication, and user-specific data handling while remaining within Supabase free-tier limits.

---

## Core Requirement

Use Supabase for:

- Authentication (Auth)
- Database (PostgreSQL)
- Real-time updates (Realtime)
- Optional storage (for future features like export)

All existing frontend features must now persist data and behave like a real application.

---

## 1. Authentication System

Implement Supabase Auth:

### Features:
- Email + Password signup/login
- Session persistence
- Logout functionality

### User Profile Table:
Store additional user data:

- id (UUID, from Supabase Auth)
- name
- email
- preferred_language (EN / TA)
- created_at

---

## 2. Database Schema (Required Tables)

Design and implement the following tables:

### USERS
- id (Primary Key)
- name
- email
- language_preference
- created_at

---

### VERSE_LIKES
- id
- user_id (FK)
- verse_reference
- created_at

---

### READING_PROGRESS
- id
- user_id
- plan_id
- day_number
- completed (boolean)
- updated_at

---

### PRAYER_LOGS
- id
- user_id
- content
- created_at

---

### SERMONS
- id
- user_id
- topic
- generated_content (text or JSON)
- created_at

---

### SERVICE_PLANS (CSI — Church of South India)
- id
- user_id
- title
- content (JSON structure)
- language (EN / TA)
- created_at

---

### GROUPS
- id
- room_code (6-character UNIQUE)
- group_name
- created_by
- created_at

---

### GROUP_MEMBERS
- id
- group_id
- user_id
- joined_at

---

### MESSAGES
- id
- group_id
- user_id
- message
- created_at

---

### ACCOUNTABILITY
- id
- user_id
- streak_count
- last_active_date

---

### SONGS
- id
- title
- category (praise / worship / tamil)
- lyrics

---

## 3. Home Dashboard Integration

- Store liked verses in VERSE_LIKES
- Fetch and display Verse of the Day (can be static or API-based)
- Track recent activity (optional)

---

## 4. AI Chat System (Backend Role)

- Store chat history (optional)

### CHAT_HISTORY (optional)
- id
- user_id
- question
- response
- created_at

Backend responsibilities:
- Receive user query
- Forward to local LLM or free API
- Return structured response

---

## 5. Scripture Module

Option 1 (Recommended):
- Use static dataset for Bible text (performance efficient)

Option 2:
- Store in Supabase table:

### BIBLE_TEXT
- id
- book
- chapter
- verse
- text_en
- text_ta

Support:
- English
- Tamil
- Dual-language display

---

## 6. Sermon Architect

- Save generated sermons into SERMONS table
- Allow retrieval per user

---

## 7. Service Planner (CSI)

Definition:
CSI = Church of South India

Store structured service plan:

Example JSON:
{
  "invocation": "",
  "scripture": "",
  "psalm": "",
  "sermon": "",
  "offering": "",
  "benediction": ""
}

Support:
- Tamil + English
- Editable structure

---

## 8. Community Group Chat (Realtime)

Use Supabase Realtime:

### Features:
- Create group → generate unique 6-character ROOM CODE
- Join group → validate ROOM CODE
- Limit: maximum 13 users per group

### Real-time Chat:
- Subscribe to MESSAGES table
- Broadcast new messages instantly

### Rules:
- Only group members can view messages
- Prevent joining if group is full

---

## 9. Accountability System

- Track streak_count
- Update last_active_date

Logic:
- If user logs activity daily → increment streak
- Else → reset streak

---

## 10. Devotional Plans

- Store plans as static JSON OR table
- Track user progress in READING_PROGRESS

---

## 11. Worship Hub

- Store songs in SONGS table
- Include Tamil songs category

---

## 12. Settings

Store user preferences:
- language (EN / TA)
- theme (optional)

---

## 13. Security (CRITICAL)

Enable Supabase Row Level Security (RLS):

### Rules:
- Users can access only their own data
- Group messages visible only to group members
- Prayer logs are private
- Sermons are private

---

## 14. API Usage

Use Supabase client for:

- Authentication
- CRUD operations
- Real-time subscriptions

Optional:
- Use Supabase Edge Functions for AI processing

---

## 15. Performance Considerations

- Index:
  - user_id
  - group_id
  - room_code

- Paginate chat messages
- Avoid large payload queries

---

## Expected Result

A fully working backend system where:

- All features persist data
- Users have secure accounts
- Chat works in real-time
- Sermons and service plans are saved
- Spiritual tracking is functional
- The system is scalable and clean
