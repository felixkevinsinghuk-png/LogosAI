# RhemaLight AI — AI-Powered Spiritual Companion Platform

## Overview

RhemaLight AI is a modern, AI-powered web application designed to assist users in Bible study, sermon preparation, Church of South India (CSI) service planning, and spiritual growth. The platform combines intelligent AI assistance with structured theological tools to create a complete digital spiritual companion.

This system is designed to work using **free APIs and open-source tools only**, with optional local AI model integration (e.g., Mistral-7B).

---

## Core Objectives

- Provide **contextual Bible understanding**
- Support **original language insights (Greek/Hebrew)**
- Enable **Tamil + English bilingual usage**
- Assist in **sermon creation**
- Support **Church of South India (CSI) service planning**
- Encourage **daily spiritual discipline**
- Enable **faith-based community interaction**

---

## System Constraints

- No paid APIs or services
- Backend optional (can simulate using local state)
- Must work as a **functional frontend prototype**
- Must have a **unique UI design (not copied)**

---

## Application Modules

### 1. Home Dashboard

#### Features
- Time-based greeting (e.g., Good Morning / Evening)
- Personalized welcome message
- AI input box for spiritual queries
- Quick action cards
- Verse of the Day (from free dataset/API)
- Continue Reading section

#### Quick Actions
- Open Scripture
- Ask AI
- Start Devotional Plan
- Build Sermon
- Worship Songs
- Knowledge Hub

---

### 2. AI Chat System

#### Capabilities
- Bible-restricted responses
- Context-aware follow-up handling
- Structured theological responses
- Original language insights (Greek/Hebrew)

#### Behavior
- Show **3-dot animated loading** while generating
- Display full response only after completion
- Do NOT stream partial text

---

### 3. Scripture Module

#### Features
- Book → Chapter → Verse navigation
- Clean reading interface
- Highlighting and bookmarking (local state)

#### Language Support
- English (KJV or public domain)
- Tamil Bible (mandatory)
- Optional dual-language view

---

### 4. Devotional Plans

#### Features
- Predefined plans:
  - 7-day
  - 30-day
  - 90-day
- Progress tracking
- Completion percentage

---

### 5. Growth Tracker

#### Features
- Daily reading streak
- Consistency tracking
- Optional prayer logging (local)

---

### 6. Knowledge Hub

#### Content Categories
- Doctrine
- Church History
- Devotionals

---

### 7. Study Insights

#### Features
- Topic-based guides:
  - Faith
  - Love
  - Salvation
- AI-assisted explanations
- Cross-referencing verses

---

### 8. Sermon Architect

#### Input
- Topic OR Bible verse

#### Output
- Sermon outline
- Key points
- Supporting scriptures
- Practical applications

---

### 9. Service Planner (CSI — Church of South India)

#### Definition
CSI = **Church of South India**

#### Order of Service Structure
- Invocation
- Opening Prayer
- Scripture Reading
- Psalm / Responsive Reading
- Sermon
- Intercessory Prayer
- Offering
- Closing Hymn
- Benediction

#### Features
- Editable service flow
- Tamil + English support
- AI-assisted generation (optional)
- Export or copy formatted output

---

### 10. Worship Hub

#### Categories
- Praise Songs
- Worship Songs
- Tamil Songs (mandatory)

#### Features
- Song listing
- Lyrics display

---

### 11. Community Module

#### Create Group
- Input:
  - Name
  - Group Name
- Generate:
  - 6-character alphanumeric ROOM CODE

#### Join Group
- Input:
  - Name
  - Room Code

#### Rules
- Maximum 13 users per room
- Join only via ROOM CODE

#### UI
- Modern chat interface
- Inspired by messaging apps but unique
- Simulated chat (no backend required)

---

### 12. Settings

#### Options
- Theme toggle
- Language switch (English / Tamil)

---

### 13. Help Center

#### Features
- FAQ
- Usage guidance

---

## UI/UX Design Requirements

### Design Principles
- Modern SaaS-style UI
- Clean and minimal layout
- Strong visual hierarchy
- Responsive design

### Visual Style
- Deep blue / purple base colors
- Soft gold or light accents
- Card-based components
- Smooth animations
- Glassmorphism or soft shadows

### Interaction Design
- Hover effects
- Smooth transitions
- Animated panels
- Responsive layouts

---

## Free API & Data Usage

### Allowed Sources
- Public domain Bible datasets (e.g., KJV)
- Open Tamil Bible datasets
- Free AI inference APIs OR local LLM

### Fallback
- Use static/mock data if APIs are unavailable

---

## AI System Requirements

### Model Options
- Local: Mistral-7B (recommended for Mac M3)
- Free API: any open inference endpoint

### Restrictions
- Only Bible-related responses
- Reject unrelated queries politely

---

## Context Awareness (Critical Feature)

### Must Support
- Follow-up questions like:
  - "Explain above"
  - "Summarize that"
  - "Rewrite in 300 words"
  - "Make it simple"

### Behavior
- Use previous response as context
- Do NOT ask for clarification unnecessarily

---

## Your Use Case (Core Purpose)

This application is designed as:

A **personal AI spiritual assistant** that:

- Explains Bible context deeply
- Provides original language insights
- Supports Tamil-speaking users
- Assists in sermon preparation
- Helps Church of South India service planning
- Encourages daily spiritual discipline
- Enables small faith-based communities

---

## Expected Outcome

A fully functional prototype that:

- Implements all modules
- Uses only free resources
- Supports English + Tamil
- Includes CSI service planning
- Has a modern, unique UI
- Works without backend dependency
- Feels like a production-ready application

---

## Future Enhancements (Optional)

- Backend integration (user accounts, persistence)
- Real-time chat using WebSockets
- Advanced AI fine-tuning for theology
- Voice-based interaction
- Mobile app version

---