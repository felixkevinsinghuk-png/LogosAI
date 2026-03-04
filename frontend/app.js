/**
 * LogosAI — Frontend Application Logic
 * ======================================
 * Handles all chat UI interactions, API communication, and dynamic rendering.
 *
 * Features:
 *  - Sends questions to the /chat endpoint
 *  - Renders AI answers with Markdown-like formatting
 *  - Displays retrieved Bible passages and language notes
 *  - Shows typing indicators while the model is generating
 *  - Auto-resizes textarea, character counter
 *  - Sidebar toggle for mobile/desktop
 *  - System status check on load
 */

// ── Constants ───────────────────────────────────────────────────────────────
const API_BASE = "";          // Same origin — FastAPI serves both API and frontend
const CHAT_ENDPOINT = `${API_BASE}/chat`;
const STATUS_ENDPOINT = `${API_BASE}/status`;

// ── DOM References ───────────────────────────────────────────────────────────
const messagesList = document.getElementById("messages-list");
const messagesWindow = document.getElementById("messages-window");
const welcomeScreen = document.getElementById("welcome-screen");
const questionInput = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const sidebar = document.querySelector(".sidebar");

// ── State ────────────────────────────────────────────────────────────────────
let isLoading = false;
let conversationId = null;


// ══════════════════════════════════════════════════════════════════════════════
// Initialization
// ══════════════════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  checkStatus();
  questionInput.focus();
});


// ══════════════════════════════════════════════════════════════════════════════
// Status Check
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Polls the /status endpoint and updates the sidebar badge.
 */
async function checkStatus() {
  try {
    const res = await fetch(STATUS_ENDPOINT);
    if (!res.ok) throw new Error("Not OK");
    const data = await res.json();

    if (data.model_available && data.bible_indexed) {
      setStatus("Ready", "online");
    } else if (data.model_available && !data.bible_indexed) {
      setStatus("Indexing…", "indexing");
    } else {
      setStatus("Model missing", "warning");
    }
  } catch {
    setStatus("Offline", "offline");
  }

  // Re-check every 30 seconds
  setTimeout(checkStatus, 30_000);
}

function setStatus(label, state) {
  statusText.textContent = label;
  statusDot.className = `status-dot status-dot--${state}`;
}


// ══════════════════════════════════════════════════════════════════════════════
// Input Handling
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Auto-resize the textarea to fit its content.
 */
function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 180) + "px";
}

function handleKeyDown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

/**
 * Fill the question input from a hint chip or welcome card.
 */
function fillQuestion(text) {
  questionInput.value = text;
  questionInput.focus();
  autoResize(questionInput);
  // Scroll to input on mobile
  questionInput.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Clear chat history and show welcome screen.
 */
function newChat() {
  conversationId = null;
  messagesList.innerHTML = "";
  welcomeScreen.style.display = "";
  questionInput.value = "";
  autoResize(questionInput);
  questionInput.focus();
}

/**
 * Toggle sidebar visibility (mobile menu).
 */
function toggleSidebar() {
  sidebar.classList.toggle("sidebar--open");
}


// ══════════════════════════════════════════════════════════════════════════════
// Message Sending
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Send the user's question to the /chat API and display the response.
 */
async function sendMessage() {
  const question = questionInput.value.trim();
  if (!question || isLoading) return;

  // Guard: minimum length
  if (question.length < 3) {
    shakeInput();
    return;
  }

  // Hide welcome screen on first message
  welcomeScreen.style.display = "none";

  // Render user bubble
  appendUserBubble(question);

  // Clear input
  questionInput.value = "";
  autoResize(questionInput);

  // Show typing indicator
  const typingId = appendTypingIndicator();

  setLoading(true);

  try {
    const payload = { question, top_k: 5 };
    if (conversationId) {
      payload.conversation_id = conversationId;
    }

    const res = await fetch(CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      removeTypingIndicator(typingId);
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      appendErrorBubble(err.detail || `HTTP ${res.status}`);
      return;
    }

    const data = await res.json();

    // Store the conversation ID for follow-up messages
    if (data.conversation_id) {
      conversationId = data.conversation_id;
    }

    // Remove typing indicator before showing result
    removeTypingIndicator(typingId);

    // Render the response instantly
    appendAssistantBubble(data);


  } catch (err) {
    removeTypingIndicator(typingId);
    appendErrorBubble("Could not connect to the server. Is LogosAI running?");
    console.error("Chat error:", err);
  } finally {
    setLoading(false);
    questionInput.focus();
  }
}

function setLoading(state) {
  isLoading = state;
  sendBtn.disabled = state;
  sendBtn.classList.toggle("send-btn--loading", state);
}

function shakeInput() {
  questionInput.classList.add("shake");
  setTimeout(() => questionInput.classList.remove("shake"), 400);
}


// ══════════════════════════════════════════════════════════════════════════════
// Message Rendering
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Append a user chat bubble.
 */
function appendUserBubble(text) {
  const div = document.createElement("div");
  div.className = "message message--user";
  div.innerHTML = `
    <div class="message__bubble">
      <div class="message__text">${escapeHtml(text)}</div>
    </div>
  `;
  messagesList.appendChild(div);
  scrollToBottom();
}

/**
 * Create an empty assistant bubble and render sidebars/passages from metadata.
 */
function createAssistantBubble(data) {
  const div = document.createElement("div");
  div.className = "message message--assistant";

  // Build passages HTML
  let passagesHtml = "";
  if (data.passages && data.passages.length > 0) {
    const items = data.passages.map(p => `
      <div class="passage-item">
        <span class="passage-ref">${escapeHtml(p.reference)}</span>
        <span class="passage-score">${(p.score * 100).toFixed(0)}%</span>
        <p class="passage-text">"${escapeHtml(p.text)}"</p>
      </div>
    `).join("");
    passagesHtml = `
      <details class="passages-drawer" open>
        <summary class="passages-summary">
          📖 ${data.passages.length} Relevant Passage${data.passages.length !== 1 ? "s" : ""}
        </summary>
        <div class="passages-list">${items}</div>
      </details>
    `;
  }

  // Build language notes HTML
  let langHtml = "";
  if (data.language_notes && data.language_notes.trim()) {
    langHtml = `
      <details class="lang-drawer">
        <summary class="lang-summary">🔤 Original Language Notes</summary>
        <pre class="lang-notes">${escapeHtml(data.language_notes)}</pre>
      </details>
    `;
  }

  div.innerHTML = `
    <div class="message__avatar">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
      </svg>
    </div>
    <div class="message__content">
      <div class="message__bubble">
        <div class="message__text">...</div>
      </div>
      ${passagesHtml}
      ${langHtml}
    </div>
  `;

  messagesList.appendChild(div);
  scrollToBottom();
  return div;
}

/**
 * Update the text in the assistant bubble progressively.
 */
function updateAssistantText(bubbleEl, text) {
  const textEl = bubbleEl.querySelector(".message__text");
  if (textEl) {
    // During streaming, we show raw text with line breaks preserved
    textEl.style.whiteSpace = "pre-wrap";
    textEl.textContent = text;
    scrollToBottom();
  }
}

/**
 * Apply full Markdown/Bible formatting once streaming is complete.
 */
function finalizeAssistantText(bubbleEl, text) {
  const textEl = bubbleEl.querySelector(".message__text");
  if (textEl) {
    textEl.style.whiteSpace = "";
    textEl.innerHTML = formatAnswer(text);
    scrollToBottom();
  }
}

/**
 * Legacy: Append the assistant's response bubble all at once.
 */
function appendAssistantBubble(data) {
  const bubble = createAssistantBubble(data);
  finalizeAssistantText(bubble, data.answer);
}

/**
 * Append a red error bubble.
 */
function appendErrorBubble(message) {
  const div = document.createElement("div");
  div.className = "message message--error";
  div.innerHTML = `
    <div class="message__bubble message__bubble--error">
      <span class="error-icon">⚠️</span>
      <div class="message__text">${escapeHtml(message)}</div>
    </div>
  `;
  messagesList.appendChild(div);
  scrollToBottom();
}

/**
 * Add a typing indicator and return its ID.
 * Shows three animated dots that blink sequentially.
 */
function appendTypingIndicator() {
  const id = `typing-${Date.now()}`;
  const div = document.createElement("div");
  div.className = "message message--assistant";
  div.id = id;
  div.innerHTML = `
    <div class="message__avatar">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
      </svg>
    </div>
    <div class="message__content">
      <div class="message__bubble">
        <div class="typing-indicator" aria-label="Thinking...">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  `;
  messagesList.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}


// ══════════════════════════════════════════════════════════════════════════════
// Text Formatting
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Convert plain-text answer into safe HTML with basic Markdown-like formatting.
 * Handles: **bold**, *italic*, `code`, line breaks, and verse references.
 */
function formatAnswer(text) {
  if (!text) return "";

  // 1. Scrub visual separators and word count metadata (Presentation Layer Fail-safe)
  // Remove dashed/equals lines (e.g., --- or ===)
  let scrubbed = text.replace(/^[-\s]{3,}$/gm, "");
  scrubbed = scrubbed.replace(/^[\=\s]{3,}$/gm, "");
  // Remove word count mentions (e.g., (MIN 200 WORDS))
  scrubbed = scrubbed.replace(/\(MIN\s+\d+\s+WORDS.*?\)/gi, "");
  scrubbed = scrubbed.replace(/\d+\s+WORDS\s+MINIMUM/gi, "");
  scrubbed = scrubbed.replace(/TWO\s+PARAGRAPHS/gi, "");

  let html = escapeHtml(scrubbed);

  // Bold: **text**
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Italic: *text*
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

  // Inline code: `code`
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Headers: SECTION X: TITLE or just SECTION X:
  html = html.replace(/^(SECTION\s+\d+:?.*)$/gm, '<h3>$1</h3>');

  // Bullet points
  html = html.replace(/^\s*-\s+(.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*?<\/li>+)/gs, "<ul>$1</ul>");

  // Line breaks and paragraphs
  // Preserve headers outside of <p>
  html = html.split('</h3>').map(part => {
    if (part.includes('<h3>')) {
      return part + '</h3>';
    }
    return part.replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br>");
  }).join('');

  // Final cleanup: wrap in P if not already wrapped or if empty
  if (!html.startsWith('<h') && !html.startsWith('<p')) {
    html = `<p>${html}</p>`;
  }

  // Highlight Bible references
  html = html.replace(
    /\b(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|1 Samuel|2 Samuel|1 Kings|2 Kings|1 Chronicles|2 Chronicles|Ezra|Nehemiah|Esther|Job|Psalms|Psalm|Proverbs|Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|1 Corinthians|2 Corinthians|Galatians|Ephesians|Philippians|Colossians|1 Thessalonians|2 Thessalonians|1 Timothy|2 Timothy|Titus|Philemon|Hebrews|James|1 Peter|2 Peter|1 John|2 John|3 John|Jude|Revelation)\s+(\d+:\d+(?:-\d+)?)\b/g,
    '<span class="verse-ref">$1 $2</span>'
  );

  return `<p>${html}</p>`;
}

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(text) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

/**
 * Smooth-scroll the messages window to the bottom.
 */
function scrollToBottom() {
  messagesWindow.scrollTo({ top: messagesWindow.scrollHeight, behavior: "smooth" });
}
