# Bible Contextual LLM Chatbot
## Local Mistral-7B Based AI Assistant

This project is a Bible-based AI assistant that runs completely offline using a locally installed language model. The system provides contextual explanations of Bible passages with reference to original languages such as Hebrew and Greek.

The assistant works as a chatbot and focuses on contextual meaning rather than simple verse lookup.

The system is designed to run locally on a Mac M3 with zero operational cost.

---

# Project Objective

The objective of this project is to develop an AI-powered Bible assistant that can:

- Understand Bible-related questions
- Provide contextual explanations
- Explain original language meaning
- Retrieve relevant Bible passages
- Work fully offline
- Use a lightweight local language model

The system emphasizes contextual interpretation rather than keyword search.

---

# System Overview

The system combines:

- A chatbot interface
- A local language model
- A Bible knowledge base
- A semantic search system

The assistant interprets questions and produces contextual explanations based on Bible data.

---

# System Workflow

The system operates in the following sequence:

User Question  
→ Chat Interface  
→ Backend Processing  
→ Question Understanding  
→ Context Retrieval  
→ Bible Data Lookup  
→ Prompt Preparation  
→ Mistral-7B Model  
→ Generated Answer  
→ Displayed to User

This workflow allows the assistant to generate context-aware responses.

---

# Retrieval Augmented Generation

The system uses Retrieval Augmented Generation (RAG).

Instead of relying only on the language model, the system first retrieves relevant Bible passages and language information.

This information is then used by the language model to produce grounded answers.

This approach improves accuracy and reduces incorrect responses.

---

# Model Choice

The system uses the Mistral-7B language model.

Reasons for choosing this model:

- Good reasoning ability
- Lightweight enough for local execution
- Efficient on Mac M3
- Works offline
- No API cost

The model runs entirely on the local machine.

---

# System Architecture

The system contains five major components:

1. User Interface
2. Backend Processing System
3. Context Retrieval System
4. Bible Knowledge Base
5. Language Model Engine

These components work together to generate contextual explanations.

---

# Module Structure

The system is divided into logical modules.

Each module has a clear responsibility.

---

## 1. Frontend Module

### Purpose

Provides the user interface.

### Responsibilities

- Accept user questions
- Send requests to backend
- Display generated answers
- Provide chatbot interaction

### Components

- Chat interface
- Input system
- Response display

---

## 2. API Module

### Purpose

Handles communication between frontend and backend.

### Responsibilities

- Receive user questions
- Validate requests
- Send responses to frontend

### Role in System

Acts as the entry point for the system.

---

## 3. Controller Module

### Purpose

Coordinates the entire system.

### Responsibilities

- Receive questions from API
- Trigger context retrieval
- Send data to language model
- Return generated answers

### Role in System

Central decision-making component.

---

## 4. Query Processing Module

### Purpose

Processes user questions.

### Responsibilities

- Clean input text
- Interpret question meaning
- Prepare search queries

### Role in System

Prepares questions for semantic search.

---

## 5. Context Retrieval Module

### Purpose

Finds relevant Bible passages.

### Responsibilities

- Perform semantic search
- Identify relevant verses
- Retrieve context passages

### Role in System

Provides knowledge for the language model.

---

## 6. Vector Search Module

### Purpose

Supports semantic search.

### Responsibilities

- Convert text into vectors
- Store vector representations
- Find similar passages

### Role in System

Allows meaning-based search instead of keyword search.

---

## 7. Bible Data Module

### Purpose

Stores Bible information.

### Responsibilities

- Store Bible verses
- Store translations
- Store language data
- Provide structured access

### Role in System

Acts as the knowledge base.

---

## 8. Original Language Module

### Purpose

Provides Hebrew and Greek meaning.

### Responsibilities

- Provide word meanings
- Provide lexical information
- Provide Strong's references

### Role in System

Supports deeper interpretation.

---

## 9. Prompt Construction Module

### Purpose

Prepares instructions for the language model.

### Responsibilities

- Combine question and context
- Structure information
- Guide model responses

### Role in System

Improves answer quality.

---

## 10. Language Model Module

### Purpose

Generates answers.

### Responsibilities

- Interpret prompts
- Generate explanations
- Produce natural language responses

### Role in System

Core intelligence of the system.

---

# Folder Organization

The project is organized into major sections.

## Models

Contains the local language model files.

Example:

- Mistral-7B model

---

## Data

Contains datasets.

Examples:

- Bible verses
- Hebrew text
- Greek text
- Lexicons

---

## Embeddings

Contains vector representations used for semantic search.

These allow the system to search by meaning.

---

## Backend

Contains system logic.

Includes:

- API handling
- Controllers
- Retrieval pipeline
- Model interaction

---

## Vector Store

Contains semantic search components.

Includes:

- Vector generation
- Vector storage
- Similarity search

---

## Database

Contains structured Bible data loaders.

Provides organized access to:

- Verses
- Language data

---

## Frontend

Contains the chatbot interface.

Allows users to interact with the assistant.

---

# Key Features

## Contextual Understanding

The assistant understands meaning rather than only matching words.

---

## Original Language Meaning

Supports Hebrew and Greek interpretation.

---

## Offline Operation

Runs without internet connection.

---

## Zero Cost

Uses only open-source tools.

---

## Local AI Processing

All processing happens locally.

---

# Hardware Target

Designed for:

MacBook M3

The system is optimized for efficient local execution.

---

# Development Stages

## Stage 1

Local model setup.

Basic chatbot.

---

## Stage 2

Backend system.

User interface.

---

## Stage 3

Bible dataset integration.

Semantic search.

---

## Stage 4

Original language integration.

Improved contextual reasoning.

---

# Future Improvements

Possible extensions include:

- Cross references
- Multiple translations
- Commentary support
- Study tools
- Advanced language analysis

---

# Intended Use

This system is intended for:

- Bible study
- AI research
- Academic projects
- Personal learning

---

# Summary

This project is a locally running Bible AI assistant based on Mistral-7B.

The system combines:

- Language model reasoning
- Context retrieval
- Semantic search
- Bible datasets

The result is a contextual Bible assistant that runs offline with zero cost.