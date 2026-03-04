# Conversation Management System
## Session Isolation and Context Memory Behavior

This document defines how the chatbot must manage conversations, session isolation, and contextual memory.

The system must behave similarly to ChatGPT in terms of conversation handling:
- Each new conversation must start fresh.
- Each ongoing conversation must retain memory of previous messages.
- Conversations must not leak context across users or sessions.

---

# 1. Core Requirements

## 1.1 New Conversation Behavior

When a user starts a new conversation:

- The system must initialize a completely fresh session.
- No previous context should be loaded.
- No previous prompts, answers, or memory state should be reused.
- The conversation must start with an empty history.

Each conversation instance must be isolated.

This ensures:
- Privacy
- Clean contextual reasoning
- No cross-user data leakage
- Predictable theological analysis per session

---

## 1.2 Ongoing Conversation Behavior

Within the same conversation:

- The chatbot must remember prior user questions.
- The chatbot must remember its own previous responses.
- Context must accumulate progressively.
- Follow-up questions must reference earlier discussion.

Example behavior:

User: What does John 3:16 mean?  
Bot: [Detailed explanation]

User: What does "world" mean there?  
Bot: Must understand that "there" refers to John 3:16.

The system must use stored conversation history to interpret follow-up queries correctly.

---

# 2. Memory Scope Rules

## 2.1 Conversation-Level Memory

Memory must exist only at the conversation level.

- Memory begins when a conversation starts.
- Memory ends when the conversation is reset.
- Memory must not persist across different conversation IDs.

Each conversation must have:

- Unique session identifier
- Dedicated message history
- Isolated context storage

---

## 2.2 No Global Persistent Memory

The system must NOT:

- Store theological discussions globally.
- Carry interpretation across unrelated sessions.
- Share memory between different users.
- Cache user theological positions beyond the session.

All contextual awareness must be scoped strictly to the active conversation.

---

# 3. Technical Architecture Requirements

## 3.1 Conversation ID System

Each new conversation must generate:

- A unique conversation_id
- An associated message history object

All incoming requests must include:

- conversation_id
- current user message

The backend must retrieve history based on conversation_id.

---

## 3.2 Message History Structure

Each conversation must store:

- User messages
- Assistant responses
- Timestamps (optional)
- Structured formatting context (if required)

History must be appended after every exchange.

---

## 3.3 Context Injection for LLM

When generating a new response:

1. Retrieve conversation history.
2. Construct prompt including:
   - System instructions
   - Prior messages
   - Current user query
3. Send combined prompt to model.

This ensures continuity and contextual awareness.

---

# 4. Reset Behavior

A conversation must reset when:

- User clicks "New Chat"
- Session expires
- Explicit reset command is issued
- Server restart clears memory store

After reset:

- History must be cleared.
- New conversation_id must be generated.
- Model must not receive old messages.

---

# 5. Concurrency and Stability

To prevent memory-related crashes:

- Only one active inference per conversation at a time.
- Message history must not grow indefinitely.
- Implement optional context window trimming if needed.
- Avoid reloading model per conversation.

Memory must remain lightweight and scoped.

---

# 6. Security and Privacy

The system must guarantee:

- No cross-user context leakage.
- No accidental reuse of past theological responses.
- No long-term storage unless explicitly implemented.

If deployed via ngrok or public access:

- Each user must receive isolated conversation handling.
- Sessions must not overlap.

---

# 7. Expected Behavior Summary

New Conversation:
- No memory.
- Fresh theological analysis.

Same Conversation:
- Full contextual awareness.
- Follow-up understanding.
- Reference to earlier explanations.
- Structured, consistent reasoning.

---

# 8. Goal

The chatbot must replicate ChatGPT-style conversational memory behavior:

- Isolated sessions
- Context-aware responses
- Clean resets
- No cross-session contamination

This design ensures:

- Theological accuracy
- Logical continuity
- Privacy
- System stability