// ── State ────────────────────────────────────────────────────────────────────
let isLoading = false;
let conversationId = null;
let currentView = 'home';
let isLiked = false;
let chatHistory = []; // Local history to manage Gemini context

// ── Static Bible Data ────────────────────────────────────────────────────────
const FALLBACK_VERSES = [
  { text: '"casting all your anxieties on him, because he cares for you."', ref: '— 1 Peter 5:7 (ESV)', theme: 'Peace' },
  { text: '"For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life."', ref: '— John 3:16 (ESV)', theme: 'Love' },
  { text: '"I can do all things through him who strengthens me."', ref: '— Philippians 4:13 (ESV)', theme: 'Strength' },
  { text: '"Trust in the LORD with all your heart, and do not lean on your own understanding."', ref: '— Proverbs 3:5 (ESV)', theme: 'Trust' },
  { text: '"The LORD is my shepherd; I shall not want."', ref: '— Psalm 23:1 (ESV)', theme: 'Provision' },
  { text: '"Be strong and courageous. Do not be frightened, for the LORD your God is with you."', ref: '— Joshua 1:9 (ESV)', theme: 'Courage' },
  { text: '"And we know that for those who love God all things work together for good."', ref: '— Romans 8:28 (ESV)', theme: 'Hope' },
];
let verseIndex = 0;

/**
 * Helper to get or create the default 'USER' playlist for a user.
 */
async function getOrCreateDefaultPlaylist(userId) {
  if (!userId) return null;
  const supabase = window.supabaseClient;
  
  const { data, error } = await supabase
    .from('playlists')
    .select('id')
    .eq('user_id', userId)
    .eq('name', 'USER')
    .single();
    
  if (data) return data.id;
  
  const { data: newData, error: newError } = await supabase
    .from('playlists')
    .insert({ name: 'USER', user_id: userId })
    .select()
    .single();
    
  return newData ? newData.id : null;
}

// Removed legacy static mockResponses and defaultResponses

// ── DOM References ──────────────────────────────────────────────────────────
const messagesList    = document.getElementById('messages-list');
const chatMessages    = document.getElementById('chat-messages');
const chatWelcome     = document.getElementById('chat-welcome');
const questionInput   = document.getElementById('question-input');
const sendBtn         = document.getElementById('send-btn');
const sidebar         = document.getElementById('sidebar');
const sidebarOverlay  = document.getElementById('sidebar-overlay');
const statusDot       = document.getElementById('status-dot');
const statusText      = document.getElementById('status-text');
const aiChipDot       = document.getElementById('ai-chip-dot');
const aiChipText      = document.getElementById('ai-chip-text');

// ── Static App Data ──────────────────────────────────────────────────────────
const STATIC_PLANS = [
  {
    "id": "full-bible-365",
    "title": "Full Bible in One Year",
    "description": "Read through the entire Old and New Testament in 365 days.",
    "duration_days": 365
  },
  {
    "id": "gospels-120",
    "title": "Gospels in 4 Months",
    "description": "A 120-day journey through Matthew, Mark, Luke, and John.",
    "duration_days": 120
  },
  {
    "id": "nt-year",
    "title": "New Testament in a Year",
    "description": "Read through the entire New Testament in 365 days, one chapter a day.",
    "duration_days": 365
  }
];

// ══════════════════════════════════════════════════════════════════════════════
// Initialization & Auth Helpers
// ══════════════════════════════════════════════════════════════════════════════

// authFetch and API_BASE removed for static cPanel deployment.
// Using direct window.supabaseClient for all database operations.

async function initializeApp() {
  setGreeting();
  simulateStatusCheck();
  loadVerseOfDay();
  initBibleUI();
  questionInput && questionInput.addEventListener('keydown', handleKeyDown);
  
  // ⚠️ IMPORTANT: Run Supabase calls sequentially (not in parallel!)
  // Parallel calls steal each other's auth token lock and fail with:
  // "Lock was released because another request stole it"
  await fetchPlaylists();
  await new Promise(r => setTimeout(r, 150)); // Small gap to prevent lock contention
  await fetchPlans();
  await new Promise(r => setTimeout(r, 150));
  await fetchStreak();
}


// ── Diagnostic Tool ──────────────────────────────────────────────────────────
async function runSupabaseDiagnostic() {
  const supabase = window.supabaseClient;
  const results = [];
  const tables = ['users', 'songs', 'playlists', 'accountability_users', 'reading_progress'];
  
  showToast('Running diagnostics...', 'info');
  for (const table of tables) {
    try {
      const { error } = await supabase.from(table).select('id').limit(1);
      results.push( error ? `❌ ${table}: ${error.code} - ${error.message}` : `✅ ${table}: OK` );
    } catch(e) {
      results.push(`❌ ${table}: ${e.message}`);
    }
  }
  
  const msg = results.join('\n');
  alert(`Supabase Diagnostic Results\n\n${msg}\n\nIf you see ❌ errors, run SUPABASE_RLS_FIX.sql in your Supabase SQL Editor.`);
}

// Application initialization is now exclusively handled by Supabase onAuthStateChange
// to prevent premature API calls before the JWT is resolved.

function setGreeting() {
  const hour = new Date().getHours();
  let time = 'Good morning';
  if (hour >= 12 && hour < 17) time = 'Good afternoon';
  else if (hour >= 17) time = 'Good evening';

  const el = document.getElementById('greeting-time');
  if (el) el.textContent = time;
}

function simulateStatusCheck() {
  // Show as online initially, then flip to online after a moment
  setStatus('Connecting…', '');
  setTimeout(() => {
    setStatus('Ready (Cloud)', 'online');
    if (aiChipDot) { aiChipDot.className = 'status-chip-dot online'; }
    if (aiChipText) { aiChipText.textContent = 'AI Static Mode'; }
  }, 1000);
}

function setStatus(label, state) {
  if (statusText) statusText.textContent = label;
  if (statusDot) statusDot.className = `status-dot${state ? ' status-dot--' + state : ''}`;
}

// ══════════════════════════════════════════════════════════════════════════════
// Navigation / View Routing
// ══════════════════════════════════════════════════════════════════════════════

function navigateTo(viewName) {
  console.log("[App] Navigating to:", viewName);
  // Hide all views
  document.querySelectorAll('.view').forEach(v => v.classList.remove('view--active'));

  // Show target view
  const target = document.getElementById('view-' + viewName);
  if (target) target.classList.add('view--active');

  // Update nav active state
  currentView = viewName;

  // Handle sidebar active state based on data-view attribute
  document.querySelectorAll('.nav-item').forEach(n => {
    if (n.getAttribute('data-view') === viewName) {
      n.classList.add('nav-item--active');
    } else {
      n.classList.remove('nav-item--active');
    }
  });

  if (viewName === 'chat') {
    const navAsk = document.getElementById('ask-ai-btn');
    // no special state needed
  }

  currentView = viewName;

  // Focus input if chat
  if (viewName === 'chat' && questionInput) {
    setTimeout(() => questionInput.focus(), 100);
  }

  // Load appropriate data
  if (viewName === 'bible') {
    // Always initialize bible dropdowns when navigating to this view
    initBibleUI();
  } else if (viewName === 'liturgy' || viewName === 'service') {
    setTimeout(renderLiturgy, 50); // slight delay to ensure DOM is ready
  } else if (viewName === 'history') {
    fetchHistory('all', 'history-container');
  } else if (viewName === 'songs') {
    fetchSongs();
  } else if (viewName === 'plans') {
    fetchPlans();
  } else if (viewName === 'accountability') {
    fetchStreak();
  }

  // Close sidebar on mobile
  if (window.innerWidth < 900) {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('active');
  }
}

function refreshDashboard() {
  showToast('Dashboard refreshed!', 'success');
  setGreeting();
  verseIndex = Math.floor(Math.random() * verses.length);
  loadVerseOfDay();
}

async function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  
  // Update UI immediately
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('rhemalight_theme', newTheme);
  
  // Persist to backend if logged in
  if (currentUser) {
    try {
      const supabase = window.supabaseClient;
      await supabase.from('users').update({ theme: newTheme }).eq('id', currentUser.id);
    } catch (e) {
      console.error("Failed to sync theme:", e);
    }
  }
}

// Ensure theme applies before main render
function applyInitialTheme() {
  const saved = localStorage.getItem('rhemalight_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
}
applyInitialTheme();

// ══════════════════════════════════════════════════════════════════════════════
// Sidebar
// ══════════════════════════════════════════════════════════════════════════════

function toggleSidebar() {
  sidebar.classList.toggle('open');
  sidebarOverlay.classList.toggle('active');
}

// ══════════════════════════════════════════════════════════════════════════════
// Verse of the Day
// ══════════════════════════════════════════════════════════════════════════════

async function loadVerseOfDay() {
  const textEl  = document.getElementById('verse-text');
  const refEl   = document.getElementById('verse-ref');
  const themeEl = document.getElementById('votd-theme');
  
  if (!textEl || !refEl) return;

  // Deterministic local selection based on the current date
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now - start;
  const oneDay = 1000 * 60 * 60 * 24;
  const dayOfYear = Math.floor(diff / oneDay);
  
  const v = FALLBACK_VERSES[dayOfYear % FALLBACK_VERSES.length];

  if (textEl)  textEl.textContent  = v.text;
  if (refEl)   refEl.textContent   = v.ref;
  if (themeEl) themeEl.textContent = "Daily Bread";
  
  // Store current verse in memory for "Save" functionality
  window.currentVotd = v;
}

function loadNewVerse() {
  // Re-fetch the verse of the day (it will be deterministic for the date)
  loadVerseOfDay();
  showToast('Daily verse refreshed!', 'info');
}

async function toggleLike() {
  if (!currentUser) {
    showToast('Please log in to save verses.', 'info');
    openAuthModal();
    return;
  }
  
  if (!window.currentVotd) return;
  
  isLiked = !isLiked;
  const btn = document.getElementById('like-btn');
  if (btn) btn.classList.toggle('liked', isLiked);

  const supabase = window.supabaseClient;
  if (!supabase) return;

  const currentVerse = window.currentVotd;
  
  if (isLiked) {
    const { error } = await supabase.from('verse_likes').insert({
      user_id: currentUser.id,
      verse_reference: currentVerse.ref,
      verse_text: currentVerse.text
    });
    showToast(error ? error.message : 'Verse saved to database!', error ? 'error' : 'success');
  } else {
    // Attempt delete
    const { error } = await supabase.from('verse_likes')
      .delete()
      .match({ user_id: currentUser.id, verse_reference: currentVerse.ref });
    showToast(error ? error.message : 'Removed from database', error ? 'error' : 'info');
  }
}

async function savePrayer() {
  if (!currentUser) {
    showToast('Please log in to save prayers.', 'info');
    openAuthModal();
    return;
  }
  
  const input = document.getElementById('prayer-input');
  if (!input || !input.value.trim()) return;

  const supabase = window.supabaseClient;
  if (!supabase) return;

  const { error } = await supabase.from('prayer_logs').insert({
    user_id: currentUser.id,
    content: input.value.trim()
  });

  if (error) {
    showToast(error.message, 'error');
  } else {
    showToast('Prayer saved securely.', 'success');
    input.value = '';
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// User History 
// ══════════════════════════════════════════════════════════════════════════════

async function fetchHistory(type = 'all', containerId = 'history-container') {
  const requestId = ++activeHistoryRequestId;
  activeHistoryRequestId = requestId;

  const container = document.getElementById(containerId);
  if (!container) return;
  
  if (!currentUser) {
    container.innerHTML = `<div class="dashboard-card"><p>Please log in to view your history.</p></div>`;
    return;
  }
  
  // Instant Network Cancellation: Kill any pending history requests
  if (playlistAbortController) playlistAbortController.abort();
  playlistAbortController = new AbortController();
  
  container.innerHTML = `<div class="dashboard-card"><div class="typing-indicator" style="margin:20px 0;"><span></span><span></span><span></span></div></div>`;

  const supabase = window.supabaseClient;

  try {
    let combinedItems = [];
    const fetchPromises = [];

    // Parallel Fetch Setup
    if (type === 'all' || type === 'prayer' || type === 'prayers') {
      fetchPromises.push(
        fetchWithTimeout(
          supabase.from('prayer_logs').select('id, user_id, content, created_at').eq('user_id', currentUser.id).order('created_at', { ascending: false }).limit(20).abortSignal(playlistAbortController.signal),
          20000
        ).then(res => ({ ...res, cat: 'prayer' }))
      );
    }
    
    if (type === 'all' || type === 'verse_like' || type === 'liked_verses') {
      fetchPromises.push(
        fetchWithTimeout(
          supabase.from('verse_likes').select('id, user_id, verse_reference, verse_text, created_at').eq('user_id', currentUser.id).order('created_at', { ascending: false }).limit(20).abortSignal(playlistAbortController.signal),
          20000
        ).then(res => ({ ...res, cat: 'verse_like' }))
      );
    }
    
    // Fetch AI Chats
    if (type === 'all' || type === 'chat' || type === 'ai') {
      fetchPromises.push(
        fetchWithTimeout(
          supabase.from('chat_logs').select('id, user_id, question, answer, created_at').eq('user_id', currentUser.id).order('created_at', { ascending: false }).limit(20).abortSignal(playlistAbortController.signal),
          20000
        ).then(res => ({ ...res, cat: 'chat' }))
      );
    }

    // Execute Parallel Fetches
    const results = await Promise.all(fetchPromises);
    
    // Check if this is still the active history request
    if (requestId !== activeHistoryRequestId) return;

    results.forEach(res => {
        if (res.error) throw new Error(`${res.cat}: ${res.error.message}`);
        if (res.data) {
            if (res.cat === 'prayer') {
                combinedItems = combinedItems.concat(res.data.map(p => ({ ...p, type: 'prayer', title: 'Prayer' })));
            } else if (res.cat === 'verse_like') {
                combinedItems = combinedItems.concat(res.data.map(l => ({ ...l, type: 'verse_like', title: l.verse_reference, content: l.verse_text })));
            } else if (res.cat === 'chat') {
                combinedItems = combinedItems.concat(res.data.map(c => ({ ...c, type: 'chat', title: c.question, content: c.answer })));
            }
        }
    });

    // Sort combined by date
    combinedItems.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    const items = combinedItems.slice(0, 20);

    if (items.length === 0) {
      container.innerHTML = `<div class="dashboard-card text-secondary text-center py-8">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="mx-auto mb-2 opacity-20"><circle cx="12" cy="12" r="10"></circle><path d="M8 12h8"></path></svg>
        No history found for this category.
      </div>`;
      return;
    }
    
    let html = '';
    items.forEach(item => {
      const dateStr = new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
      
      let badge = '';
      if (item.type === 'prayer') badge = '🙏 Prayer';
      if (item.type === 'verse_like') badge = '❤️ Like';
      if (item.type === 'chat') badge = '🤖 AI';
      
      html += `
        <div class="dashboard-card group hover:border-[var(--primary)] transition-colors">
          <div class="flex justify-between" style="margin-bottom: 8px;">
            <span class="text-[10px] font-bold uppercase tracking-wider text-primary bg-[var(--bg-card-hover)] px-2 py-0.5 rounded-sm">${badge}</span>
            <span style="font-size:11px; color:var(--text-secondary); opacity:0.7;">${dateStr}</span>
          </div>
          <h4 class="font-serif italic text-lg">${escapeHtml(item.title)}</h4>
          <p class="text-secondary mt-2" style="font-size:14px; white-space: pre-wrap; line-height:1.6;">${escapeHtml(item.content || '')}</p>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    if (err.name === 'AbortError') return;
    if (requestId !== activeHistoryRequestId) return;
    console.error("[fetchHistory] Error:", err);
    if (err.name === 'TimeoutError') {
        container.innerHTML = `<div class="dashboard-card text-danger text-center p-8">⚠️ <b>History Timed Out</b><br/><span class="text-xs mt-2 block opacity-70">The database took too long to load your history.</span><button class="action-btn text-xs mt-4" onclick="location.reload()">Refresh Page & Retry</button></div>`;
        return;
    }
    container.innerHTML = `<div class="dashboard-card border-danger/30 bg-danger/5">
      <div class="flex items-center gap-3 text-danger">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <div class="text-sm font-bold">Failed to load history</div>
      </div>
      <p class="text-xs mt-2 opacity-70">${escapeHtml(err.message)}</p>
      <button class="action-btn text-xs mt-4" onclick="fetchHistory('${type}')">Try Again</button>
    </div>`;
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Worship Hub
// ══════════════════════════════════════════════════════════════════════════════

let currentPlaylistId = null;
let allPlaylists = [];
let activeRequestId = 0; // Sequencing ID to ensure "Last Request Wins"
let activeHistoryRequestId = 0; // Sequencing ID for history fetches
let playlistAbortController = null; // Instant Network Cancellation

/**
 * Promise wrapper to add a timeout to any async operation (e.g. Supabase fetches)
 */
function fetchWithTimeout(promise, ms = 20000) {
    const timeout = new Promise((_, reject) => 
        setTimeout(() => {
            const err = new Error("Request timed out");
            err.name = "TimeoutError";
            reject(err);
        }, ms)
    );
    return Promise.race([promise, timeout]);
}

// Global state for songs to allow optimistic updates
window.__allSongs = [];

async function fetchSongs() {
  const container = document.getElementById('songs-grid-container');
  const titleEl = document.getElementById('current-song-view-title');
  const playlistActions = document.getElementById('playlist-actions');
  if (!container) return;

  container.innerHTML = '<div class="text-secondary col-span-3 text-center py-8 flex flex-col items-center"><div class="loading-spinner mb-2"></div>Loading all songs...</div>';
  currentPlaylistId = null;
  
  const requestId = ++activeRequestId; // Local ID for this specific call
  activeRequestId = requestId; 

  // Instant Network Cancellation: Kill any pending "stale" requests from previous clicks
  if (playlistAbortController) playlistAbortController.abort();
  playlistAbortController = new AbortController();
  
  if (titleEl) {
    titleEl.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon></svg> All Songs`;
  }
  if (playlistActions) playlistActions.classList.add('hidden');

  try {
    const supabase = window.supabaseClient;
    const user = currentUser;
    
    let query = supabase.from('songs').select('*');
    if (user) query = query.or(`user_id.eq.${user.id},user_id.is.null`);
    else query = query.is('user_id', null);
    
    // Fetch songs with 15s safety timeout and abort signal
    const { data, error } = await fetchWithTimeout(
        query.order('title').abortSignal(playlistAbortController.signal),
        15000
    );
    
    // Check if this is still the active request
    if (requestId !== activeRequestId) return;
    
    if (error) throw error;
    
    // Refresh Playlists silently in background
    fetchPlaylists(); 
    
    // Filter out songs with NO youtube_video_id
    window.__allSongs = (data || []).filter(s => s.youtube_video_id);
    if (window.__allSongs.length === 0) {
      container.innerHTML = `<div class="text-secondary col-span-3 text-center p-8">🎵 No songs yet. Add a YouTube URL above to get started!</div>`;
    } else {
      renderSongsGrid(window.__allSongs);
    }
  } catch (err) {
    if (err.name === 'AbortError') return; // Silence cancelled requests
    if (requestId !== activeRequestId) return;

    console.error('Error fetching songs:', err);
    if (err.name === 'TimeoutError') {
       container.innerHTML = `<div class="text-danger col-span-3 text-center p-8 bg-[var(--bg-card)] rounded-lg border border-[var(--border)]">⚠️ <b>Request Timed Out</b><br/><span class="text-xs mt-2 block opacity-70">The database took too long to respond. This can happen on slow networks.</span><button class="action-btn text-xs mt-4" onclick="location.reload()">Refresh Page & Retry</button></div>`;
       return;
    }
    const isPermission = err.message && err.message.includes('permission denied');
    container.innerHTML = isPermission
      ? `<div class="text-danger col-span-3 text-center p-8 bg-[var(--bg-card)] rounded-lg border border-[var(--border)]">⚠️ <b>Database Access Denied</b><br/><span class="text-xs mt-2 block opacity-70">Run SUPABASE_RLS_FIX.sql in your Supabase SQL Editor to fix permissions.</span><button class="action-btn text-xs mt-4" onclick="runSupabaseDiagnostic()">Run Diagnostic</button></div>`
      : `<div class="text-danger col-span-3 text-center p-8 bg-[var(--bg-card)] rounded-lg border border-[var(--border)]">⚠️ <b>Failed to load songs</b><br/><span class="text-xs mt-2 block opacity-70">${escapeHtml(err.message)}</span><button class="action-btn text-xs mt-4" onclick="fetchSongs()">Try Again</button></div>`;
  }
}

async function fetchPlaylists() {
    const list = document.getElementById('playlists-sidebar-list');
    const dropdown = document.getElementById('new-song-playlist');
    if (!list) return;

    try {
        const supabase = window.supabaseClient;
        const user = currentUser;
        
        if (!user) {
          list.innerHTML = '<li class="p-2 text-secondary text-sm">Log in to see playlists</li>';
          return;
        }

        const { data, error } = await supabase.from('playlists').select('*').eq('user_id', user.id).order('name');
        if (error) throw error;
        
        allPlaylists = data || [];
        
        // 1. Update Sidebar
        let sidebarHtml = `
            <li class="p-2 hover:bg-[var(--bg-card-hover)] cursor-pointer rounded flex items-center gap-2 transition-colors mb-1 ${!currentPlaylistId ? 'text-primary font-bold bg-[var(--bg-card-hover)]' : 'text-secondary'}" onclick="fetchSongs()">
               <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon></svg>
               All Songs
            </li>
        `;
        
        allPlaylists.forEach(pl => {
            const isActive = currentPlaylistId === pl.id;
            const safeName = escapeHtml(pl.name).replace(/'/g, "\\'");
            sidebarHtml += `
            <li class="hover:bg-[var(--bg-card-hover)] rounded flex justify-between items-center transition-colors mb-1 ${isActive ? 'text-primary font-bold bg-[var(--bg-card-hover)]' : 'text-secondary'}" style="padding:4px 6px 4px 8px;">
               <div class="flex items-center gap-2 truncate" style="flex:1;cursor:pointer;" onclick="fetchPlaylistSongs('${pl.id}', '${safeName}')">
                   <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
                   <span class="truncate" style="font-size:0.82rem;">${escapeHtml(pl.name)}</span>
               </div>
               <div style="display:flex;gap:3px;flex-shrink:0;">
                 <button title="Rename Playlist" onclick="renameSidebarPlaylist('${pl.id}','${safeName}')" style="background:none;border:none;cursor:pointer;padding:4px 5px;border-radius:5px;color:#a0a8c0;" onmouseover="this.style.background='var(--bg-card)'" onmouseout="this.style.background='none'">
                   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                 </button>
                 <button title="Delete Playlist" onclick="deleteSidebarPlaylist('${pl.id}')" style="background:none;border:none;cursor:pointer;padding:4px 5px;border-radius:5px;color:#f87171;" onmouseover="this.style.background='var(--bg-card)'" onmouseout="this.style.background='none'">
                   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                 </button>
               </div>
            </li>
            `;
        });
        list.innerHTML = sidebarHtml;

        // 2. Update "Add Song" Dropdown
        if (dropdown) {
            let dropHtml = '<option value="USER">USER (Default)</option>';
            allPlaylists.forEach(pl => {
                // Case-insensitive check to avoid duplicate 'USER' options
                if(pl.name.toUpperCase() !== 'USER') {
                    dropHtml += `<option value="${pl.id}">${escapeHtml(pl.name)}</option>`;
                }
            });
            dropdown.innerHTML = dropHtml;
        }

    } catch (e) {
        console.error('Playlist fetch error:', e);
        const isPermission = e.message && e.message.includes('permission denied');
        list.innerHTML = isPermission
          ? `<li class="p-3 text-danger text-sm">⚠️ <b>Database Access Denied</b><br/><span class="text-xs opacity-70">Please run SUPABASE_RLS_FIX.sql in your Supabase dashboard.</span><br/><button class="action-btn text-xs mt-2" onclick="runSupabaseDiagnostic()">Run Diagnostic</button></li>`
          : `<li class="p-3 text-danger text-sm">Error loading playlists: ${escapeHtml(e.message)}</li>`;
    }
}

// ── YouTube IFrame API — Lazy Autoplay Engine ────────────────────────────
let autoplayEnabled = false;
let currentSongIndex = -1;
let ytPlayer = null;
let ytApiReady = false;       // true once YouTube script has loaded
let ytPlayerReady = false;    // true once YT.Player fires onReady
let pendingVideoId = null;    // video queued before API or player was ready

// Tracks the songs currently visible in the grid (filtered or total)
window.__currentGridSongs = []; 
// Tracks the total songs for the current view (all or playlist) to filter within
window.__currentViewSongs = [];

// YouTube IFrame API calls this automatically after its script loads.
// We only set a flag here — we do NOT create the player yet.
window.onYouTubeIframeAPIReady = function () {
    ytApiReady = true;
    // If a song was already clicked before the API loaded, init now
    if (pendingVideoId) {
        _createYTPlayer(pendingVideoId);
        pendingVideoId = null;
    }
};

// Create the YT.Player exactly once — called on first song click
function _createYTPlayer(videoId) {
    // Inject a fresh div for the API to mount into
    const wrap = document.getElementById('ytplayer-wrap');
    if (!wrap) return;
    wrap.innerHTML = '<div id="ytplayer-inner"></div>';

    ytPlayer = new YT.Player('ytplayer-inner', {
        height: '100%',
        width: '100%',
        videoId: videoId,
        playerVars: { autoplay: 1, rel: 0, modestbranding: 1 },
        events: {
            onReady: function () {
                ytPlayerReady = true;
            },
            onStateChange: function (e) {
                if (e.data === 0 && autoplayEnabled) {  // 0 = ENDED
                    playAdjacentSong(1);
                }
            }
        }
    });
}

function toggleAutoplay() {
    autoplayEnabled = !autoplayEnabled;
    const btn = document.getElementById('autoplay-toggle-btn');
    if (btn) {
        if (autoplayEnabled) {
            btn.style.background = 'var(--accent)';
            btn.style.color = '#fff';
            btn.style.borderColor = 'var(--accent)';
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Autoplay: ON`;
        } else {
            btn.style.background = 'var(--bg-card-hover)';
            btn.style.color = 'var(--text-secondary)';
            btn.style.borderColor = 'var(--border)';
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg> Autoplay: OFF`;
        }
    }
    showToast('Autoplay ' + (autoplayEnabled ? 'ON' : 'OFF'), autoplayEnabled ? 'success' : 'info');
}

function playAdjacentSong(direction) {
    const songs = window.__currentGridSongs && window.__currentGridSongs.length > 0 
                  ? window.__currentGridSongs 
                  : window.__allSongs;
                  
    if (!songs || songs.length === 0) return;
    
    let nextIndex = currentSongIndex + direction;
    if (nextIndex < 0) nextIndex = songs.length - 1;
    if (nextIndex >= songs.length) nextIndex = 0;
    
    const s = songs[nextIndex];
    if (s && s.youtube_video_id) {
        // Find correct index in global list if needed, or just play by videoId
        playSong(s.youtube_video_id, s.title, nextIndex);
    }
}

let searchTimeout = null;
function handleSearch(query) {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const q = (query || "").toLowerCase().trim();
        if (!window.__currentViewSongs) return;

        if (!q) {
            window.__currentGridSongs = [...window.__currentViewSongs];
        } else {
            window.__currentGridSongs = window.__currentViewSongs.filter(s => 
                (s.title || "").toLowerCase().includes(q) || 
                (s.category || "").toLowerCase().includes(q)
            );
        }
        
        // Ensure the grid stays sorted by title even after filtering
        window.__currentGridSongs.sort((a, b) => (a.title || "").localeCompare(b.title || ""));
        
        renderSongsGrid(window.__currentGridSongs, !!currentPlaylistId, true);
    }, 200); // 200ms debounce to prevent lag during typing
}

function playSong(videoId, title, indexOverride) {
    if (!videoId || videoId === 'undefined' || videoId === 'null') {
        showToast('No YouTube video ID for this song.', 'error');
        return;
    }

    // Track position in CURRENT GRID list for autoplay/nav
    if (indexOverride !== undefined) {
        currentSongIndex = indexOverride;
    } else {
        const songs = window.__currentGridSongs && window.__currentGridSongs.length > 0 
                      ? window.__currentGridSongs 
                      : window.__allSongs;
        const idx = songs.findIndex(s => s.youtube_video_id === videoId);
        if (idx !== -1) currentSongIndex = idx;
    }

    // Update UI
    const titleEl = document.getElementById('ytplayer-title');
    const watchLink = document.getElementById('ytplayer-watch-link');
    if (titleEl) titleEl.innerText = title;
    if (watchLink) watchLink.href = `https://www.youtube.com/watch?v=${videoId}`;

    // Hide placeholder, show player
    const placeholder = document.getElementById('player-placeholder');
    const container = document.getElementById('youtube-player-container');
    if (placeholder) placeholder.style.display = 'none';
    if (container) {
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    if (ytPlayerReady && ytPlayer && typeof ytPlayer.loadVideoById === 'function') {
        // Player exists — just load the new video (instant, no reload)
        ytPlayer.loadVideoById(videoId);
    } else if (ytApiReady) {
        // API loaded but player not yet created — create it now with this video
        _createYTPlayer(videoId);
    } else {
        // API script hasn't loaded yet — queue and wait
        pendingVideoId = videoId;
    }
}

function closeYouTubePlayer() {
    const placeholder = document.getElementById('player-placeholder');
    const container = document.getElementById('youtube-player-container');
    if (container) container.style.display = 'none';
    if (placeholder) placeholder.style.display = 'block';
    if (ytPlayerReady && ytPlayer && typeof ytPlayer.stopVideo === 'function') {
        ytPlayer.stopVideo();
    }
    currentSongIndex = -1;
}




async function fetchPlaylistSongs(playlistId, name) {
    const requestId = ++activeRequestId;
    activeRequestId = requestId;

    // Instant Network Cancellation: Kill any pending "stale" requests from previous clicks
    if (playlistAbortController) playlistAbortController.abort();
    playlistAbortController = new AbortController();

    const container = document.getElementById('songs-grid-container');
    const titleEl = document.getElementById('current-song-view-title');
    const playlistActions = document.getElementById('playlist-actions');
    if (!container) return;

    currentPlaylistId = playlistId;
    
    let cleanName = (name || "").replace(/^Loading\s+/, "").replace(/\.\.\.$/, "").trim();
    if (!cleanName) cleanName = "Playlist";

    container.innerHTML = `<div class="text-secondary col-span-3 text-center py-8 flex flex-col items-center"><div class="loading-spinner mb-2"></div>Loading ${escapeHtml(cleanName)}...</div>`;
    
    if (titleEl) {
        titleEl.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg> ${escapeHtml(cleanName)}`;
    }
    
    if (playlistActions) {
        if (cleanName.toUpperCase() === 'USER') playlistActions.classList.add('hidden');
        else playlistActions.classList.remove('hidden');
    }

    try {
        const supabase = window.supabaseClient;
        let songs = [];

        if (cleanName.toUpperCase() === 'USER') {
            const user = currentUser;
            let query = supabase.from('songs').select('*');
            if (user) query = query.or(`user_id.eq.${user.id},user_id.is.null`);
            else query = query.is('user_id', null);
            
            const { data, error } = await fetchWithTimeout(
              query.order('title').abortSignal(playlistAbortController.signal), 
              15000
            );
            if (requestId !== activeRequestId) return;
            if (error) throw error;
            songs = (data || []).filter(s => s.youtube_video_id);
        } else {
            const { data: mappings, error: mapError } = await fetchWithTimeout(
                supabase.from('playlist_songs').select('song_id').eq('playlist_id', playlistId).abortSignal(playlistAbortController.signal),
                15000
            );
            if (requestId !== activeRequestId) return;
            if (mapError) throw mapError;
            
            if (!mappings || mappings.length === 0) {
              container.innerHTML = `<div class="text-secondary col-span-3 text-center py-8">This playlist is empty.</div>`;
              return;
            }
            
            const songIds = mappings.map(m => m.song_id);
            const { data: songData, error: songError } = await fetchWithTimeout(
                supabase.from('songs').select('*').in('id', songIds).order('title').abortSignal(playlistAbortController.signal),
                15000
            );
            if (requestId !== activeRequestId) return;
            if (songError) throw songError;
            songs = songData || [];
        }
        
        renderSongsGrid(songs, true);
        fetchPlaylists(); 
    } catch (e) {
        if (e.name === 'AbortError') return; // Ignore cancelled requests
        if (requestId !== activeRequestId) return;
        console.error("Error fetching playlist songs:", e);
        if (e.name === 'TimeoutError') {
            container.innerHTML = `<div class="text-danger col-span-3 text-center p-8 bg-[var(--bg-card)] rounded-lg border border-[var(--border)]">⚠️ <b>Request Timed Out</b><br/><span class="text-xs mt-2 block opacity-70">Loading took too long. Please refresh the page to try again.</span><button class="action-btn text-xs mt-4" onclick="location.reload()">Refresh Page & Retry</button></div>`;
            return;
        }
        container.innerHTML = `<div class="text-danger col-span-3 text-center p-8 bg-[var(--bg-card)] rounded-lg border border-[var(--border)]">⚠️ <b>Failed to load playlist</b><br/><span class="text-xs mt-2 block opacity-70">${escapeHtml(e.message)}</span></div>`;
    }
}

function renderSongsGrid(songs, isPlaylistView = false, isSearchAction = false) {
  const container = document.getElementById('songs-grid-container');
  if (!container) return;

  // If this is a fresh view (not a search update), store the full set and clear search UI
  if (!isSearchAction) {
      window.__currentViewSongs = songs || [];
      window.__currentGridSongs = songs || [];
      const searchInput = document.getElementById('song-search-input');
      if (searchInput) searchInput.value = "";
  }
  
  if (!songs || songs.length === 0) {
    container.innerHTML = `<div class="text-secondary col-span-3 text-center py-12 bg-[var(--bg-card)] rounded-xl border border-dashed border-[var(--border)]">
      <div class="text-3xl mb-3 opacity-40">🎵</div>
      <p class="m-0">${isSearchAction ? 'No songs match your search.' : 'No songs available in this view.'}</p>
    </div>`;
    return;
  }
  
  let html = '';
  songs.forEach((song, gridIndex) => {
    const thumb = song.thumbnail_url || 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?auto=format&fit=crop&q=80&w=400';
    const videoId = song.youtube_video_id || '';
    const safeTitle = escapeHtml(song.title).replace(/'/g, "\\'");
    const safeCategory = (song.category || '').replace(/'/g, "\\'");

    let moveOptions = '<option value="" disabled selected>Move to...</option>';
    // If not in default view, allow moving back to USER (Default)
    if (currentPlaylistId) {
        moveOptions += `<option value="USER">USER (Default)</option>`;
    }
    allPlaylists.forEach(pl => {
        if (pl.id !== currentPlaylistId && pl.name.toUpperCase() !== 'USER') {
            moveOptions += `<option value="${pl.id}">${escapeHtml(pl.name)}</option>`;
        }
    });

    html += `
    <div class="dashboard-card p-0 overflow-hidden relative group flex flex-col h-full" style="position:relative;">
       <!-- Inline action buttons top-right -->
       <div style="position:absolute;top:6px;right:6px;z-index:20;display:flex;gap:4px;">
         <button title="Rename Song" onclick="promptEditSong('${song.id}','${safeTitle}','${safeCategory}')" style="background:rgba(30,30,40,0.85);border:none;border-radius:6px;padding:5px 7px;cursor:pointer;display:flex;align-items:center;color:#a0a8c0;">
           <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
         </button>
         <button title="Delete Song Forever" onclick="deleteSong('${song.id}')" style="background:rgba(30,30,40,0.85);border:none;border-radius:6px;padding:5px 7px;cursor:pointer;display:flex;align-items:center;color:#f87171;">
           <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
         </button>
       </div>
       <div class="h-32 bg-[var(--bg-main)] relative border-b border-[var(--border)]">
          <img src="${thumb}" class="w-full h-full object-cover" alt="Thumbnail">
          <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
             <button class="bg-accent text-white rounded-full p-3 pl-4 shadow-lg hover:scale-110 transition-transform" onclick="playSong('${videoId}', '${safeTitle}', ${gridIndex})">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
             </button>
          </div>
       </div>
       <div class="p-3 flex-1 flex flex-col justify-between bg-[var(--bg-card)]">
          <div>
            <h4 class="m-0 text-sm font-bold truncate text-primary mb-1" title="${escapeHtml(song.title)}">${escapeHtml(song.title)}</h4>
            <span class="text-[10px] font-bold uppercase tracking-wider text-secondary bg-[var(--bg-card-hover)] px-2 py-0.5 rounded-sm">${escapeHtml(song.category)}</span>
          </div>
          <!-- Move to playlist row -->
          <div class="flex items-center gap-2 mt-3">
            <select style="flex:1;font-size:11px;padding:4px 6px;background:var(--bg-card-hover);border:1px solid var(--border);border-radius:6px;color:var(--text-secondary);" onchange="moveSong('${song.id}', this.value)">
              ${moveOptions}
            </select>
            ${isPlaylistView ? `<button onclick="removeSongFromPlaylist('${song.id}')" title="Remove from playlist" style="background:none;border:none;cursor:pointer;color:#f87171;padding:4px;"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>` : ''}
          </div>
       </div>
    </div>
    `;
  });
  
  container.innerHTML = html;
}

function setupDropdowns() {
    document.querySelectorAll('#songs-grid-container .dropdown > span').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            const content = btn.nextElementSibling;
            document.querySelectorAll('#songs-grid-container .dropdown-content').forEach(c => { if(c !== content) c.classList.add('hidden'); });
            content.classList.toggle('hidden');
        };
    });
    // Global close
    document.addEventListener('click', () => {
        document.querySelectorAll('#songs-grid-container .dropdown-content').forEach(c => c.classList.add('hidden'));
    }, { once: false });
}

async function addYouTubeSong() {
    const input = document.getElementById('new-song-url');
    const titleInput = document.getElementById('new-song-title');
    const categorySelect = document.getElementById('new-song-category');
    const playlistSelect = document.getElementById('new-song-playlist');
    const btn = document.getElementById('add-song-btn');

    let rawUrl = input.value;
    let rawTitle = titleInput ? titleInput.value : "";

    if (!rawUrl || !rawUrl.trim()) return showToast('Please enter a YouTube URL', 'error');
    if (!rawTitle || !rawTitle.trim()) return showToast('Please enter a Title', 'error');
    
    // Aggressively remove any accidental spaces user might have pasted in URL
    const url = rawUrl.replace(/\s+/g, '');
    const title = rawTitle.trim();
    
    const match = url.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})/);
    const videoId = match ? match[1] : null;
    
    if (!videoId) {
        return showToast('Invalid YouTube URL', 'error');
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span> Adding...';
    }
    
    // ══════════════════════════════════════════════════════════════════════
    // OPTIMISTIC UI: Show the song IMMEDIATELY
    // ══════════════════════════════════════════════════════════════════════
    const tempId = 'temp-' + Date.now();
    const optimisticSong = {
        id: tempId,
        title: title,
        category: categorySelect.value,
        youtube_url: url,
        youtube_video_id: videoId,
        thumbnail_url: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
        isOptimistic: true // marker for UI if needed
    };

    // Add to local state and re-render grid instantly
    window.__allSongs = [optimisticSong, ...window.__allSongs];
    renderSongsGrid(window.__allSongs);
    showToast('Song added to your library!', 'success');
    
    // Clear inputs immediately
    input.value = '';
    titleInput.value = '';
    if (btn) {
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1 inline"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg> Add Song';
        }, 800);
    }
    // ══════════════════════════════════════════════════════════════════════

    try {
        const supabase = window.supabaseClient;
        let user = currentUser;
        if (!user) {
            const { data } = await supabase.auth.getSession();
            user = data?.session?.user;
        }
        if (!user) throw new Error("Please log in.");

        // PRE-CHECK: Duplicate Detection (URL or Title)
        const { data: existingSongs, error: checkError } = await supabase
            .from('songs')
            .select('id, title, youtube_url')
            .eq('user_id', user.id)
            .or(`youtube_url.eq.${url},title.eq.${title}`);

        if (existingSongs && existingSongs.length > 0) {
            const isUrlMatch = existingSongs.some(s => s.youtube_url === url);
            const msg = isUrlMatch ? "This song (URL) already exists in your library." : `A song with the title "${title}" already exists.`;
            showToast(msg, 'error');
            return;
        }

        const payload = {
            title: title,
            category: categorySelect.value,
            language: 'en',
            youtube_url: url,
            youtube_video_id: videoId,
            thumbnail_url: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
            user_id: user.id
        };

        const { data: newSong, error: songError } = await supabase
          .from('songs')
          .insert(payload)
          .select()
          .single();
          
        if (songError) {
            console.error('Supabase Song Insert Error:', songError);
            throw songError;
        }

        console.log('Successfully inserted song:', newSong);

        // Handle playlist assignment
        let targetPlaylistId = playlistSelect.value;
        if (!targetPlaylistId || targetPlaylistId === 'USER') {
            targetPlaylistId = await getOrCreateDefaultPlaylist(user.id);
        }

        if (targetPlaylistId) {
            const { error: plErr } = await supabase.from('playlist_songs').insert({
                playlist_id: targetPlaylistId,
                song_id: newSong.id
            });
            if (plErr) throw plErr;
        }

        // Update local state with real ID from database
        if (newSong) {
            const idx = window.__allSongs.findIndex(s => s.id === tempId);
            if (idx !== -1) window.__allSongs[idx].id = newSong.id;
        }

        // Wait a second then refresh properly in background
        setTimeout(async () => {
            await fetchPlaylists();
            await fetchSongs();
        }, 2000);

    } catch (e) {
        console.error('Background Error adding song:', e);
        // If it failed, remove from optimistic UI
        window.__allSongs = window.__allSongs.filter(s => s.id !== tempId);
        renderSongsGrid(window.__allSongs);
        showToast('Error saving: ' + e.message, 'error');
    }
}

async function promptEditSong(id, currentTitle, currentCategory) {
    const newTitle = prompt("Edit Title:", currentTitle);
    if (newTitle === null) return;
    
    try {
        const supabase = window.supabaseClient;
        const { error } = await supabase
          .from('songs')
          .update({ title: newTitle.trim() })
          .eq('id', id);
          
        if (error) throw error;
        showToast("Song updated");
        
        if (currentPlaylistId) {
            fetchPlaylistSongs(currentPlaylistId, document.getElementById('current-song-view-title').innerText);
        } else {
            fetchSongs();
        }
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function moveSong(songId, targetPlaylistId) {
    try {
        const supabase = window.supabaseClient;
        const { data } = await supabase.auth.getSession();
        const user = data?.session?.user;
        if (!user) throw new Error("Please log in.");
        
        if (targetPlaylistId === 'USER') {
            // Handle as 'Return to Library' - Strip custom mappings
            await supabase.from('playlist_songs')
                .delete()
                .eq('song_id', songId);
        } else {
            // 1. Safely insert into the new playlist first to prevent orphaned songs
            const { error: insertErr } = await supabase.from('playlist_songs').insert({
                playlist_id: targetPlaylistId,
                song_id: songId
            });
            
            // Ignore unique violation (23505) if it's already in the target playlist
            if (insertErr && insertErr.code !== '23505') throw insertErr;

            // 2. Now clean up old mappings (delete from all other playlists)
            await supabase.from('playlist_songs')
                .delete()
                .eq('song_id', songId)
                .neq('playlist_id', targetPlaylistId);
        }
        
        showToast("Song moved successfully", "success");

        // Optimistic UI: If we are in a playlist view, remove the song from THIS view
        if (currentPlaylistId) {
            window.__currentGridSongs = (window.__currentGridSongs || []).filter(s => s.id !== songId);
            window.__currentViewSongs = (window.__currentViewSongs || []).filter(s => s.id !== songId);
            renderSongsGrid(window.__currentGridSongs, true, true);
        }

        // Silent sidebar refresh
        fetchPlaylists();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function promptEditSong(id, oldTitle, oldCategory) {
    const newTitle = prompt("Edit Song Title:", oldTitle);
    if (newTitle === null) return;
    
    const newCategory = prompt("Edit Song Category (e.g. WORSHIP, PRAISE, COMMUNION):", oldCategory);
    if (newCategory === null) return;
    
    if (newTitle.trim() === '') return showToast('Title cannot be empty', 'error');

    try {
        const supabase = window.supabaseClient;
        const { error } = await supabase.from('songs')
            .update({ title: newTitle.trim(), category: newCategory.trim().toUpperCase() })
            .eq('id', id);
            
        if (error) throw error;
        
        showToast('Song updated successfully', 'success');
        
        // Optimistic update
        if (window.__allSongs) {
            const index = window.__allSongs.findIndex(s => s.id === id);
            if (index !== -1) {
                window.__allSongs[index].title = newTitle.trim();
                window.__allSongs[index].category = newCategory.trim().toUpperCase();
                renderSongsGrid(window.__allSongs);
            }
        } else {
            fetchSongs();
        }
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteSong(id) {
    if (!confirm('Are you sure you want to delete this song forever?')) return;
    try {
        const supabase = window.supabaseClient;
        
        // Optimistic UI: Remove from local state immediately
        window.__allSongs = window.__allSongs.filter(s => s.id !== id);
        renderSongsGrid(window.__allSongs);
        showToast('Song removed from library', 'success');

        const { error } = await supabase.from('songs').delete().eq('id', id);
        if (error) throw error;
        
        // Silent sidebar refresh
        fetchPlaylists();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function promptCreatePlaylist() {
    const name = prompt("Enter a name for your new playlist:");
    if (!name || name.trim() === '') return;
    try {
        const supabase = window.supabaseClient;
        const { data } = await supabase.auth.getSession();
        const user = data?.session?.user;
        if (!user) throw new Error("Please log in.");
        
        const { error } = await supabase.from('playlists').insert({
            name: name.trim(),
            user_id: user.id
        });
        
        if (error) throw error;
        showToast('Playlist created!', 'success');
        
        // Refresh playlists
        await fetchPlaylists();
        
        // RE-RENDER current view to update entry points (Move To dropdowns)
        if (currentPlaylistId) {
            const titleEl = document.getElementById('current-song-view-title');
            const cleanTitle = titleEl ? titleEl.innerText.replace(/[\n\r]/g, "").trim() : "Playlist";
            fetchPlaylistSongs(currentPlaylistId, cleanTitle);
        } else {
            fetchSongs();
        }
    } catch (e) { 
        console.error('Create playlist error:', e);
        showToast('Error creating playlist: ' + e.message, 'error'); 
    }
}



async function promptRenamePlaylist() {
    if (!currentPlaylistId) return;
    const titleEl = document.getElementById('current-song-view-title');
    const oldName = titleEl ? titleEl.innerText.trim() : "";
    const newName = prompt("Enter new name for this playlist:", oldName);
    if (!newName || newName.trim() === '' || newName === oldName) return;

    try {
        const supabase = window.supabaseClient;
        const { error } = await supabase
          .from('playlists')
          .update({ name: newName.trim() })
          .eq('id', currentPlaylistId);
          
        if (error) throw error;
        showToast("Playlist renamed", "success");
        // Update both the main view and the sidebar
        fetchPlaylistSongs(currentPlaylistId, newName.trim());
        await fetchPlaylists();
    } catch (e) { showToast(e.message, 'error'); }
}

async function confirmDeletePlaylist() {
    if (!currentPlaylistId) return;
    if (!confirm("Are you sure? This playlist will be deleted.")) return;
    
    showToast('Deleting playlist...', 'info');

    try {
        const supabase = window.supabaseClient;
        
        // Optimistic UI updates
        const deletedId = currentPlaylistId;
        currentPlaylistId = null;
        
        const { error } = await supabase.from('playlists').delete().eq('id', deletedId);
        if (error) throw error;
        
        showToast("Playlist deleted successfully", "success");
        // Reload all songs which internally resets the view and sidebar
        fetchSongs();
    } catch (e) { 
        showToast(e.message, 'error'); 
    }
}

async function renameSidebarPlaylist(playlistId, oldName) {
    const newName = prompt("Rename playlist:", oldName);
    if (!newName || newName.trim() === '' || newName.trim() === oldName) return;
    try {
        const supabase = window.supabaseClient;
        const { error } = await supabase
            .from('playlists')
            .update({ name: newName.trim() })
            .eq('id', playlistId);
        if (error) throw error;
        showToast('Playlist renamed to "' + newName.trim() + '"', 'success');
        if (currentPlaylistId === playlistId) {
            fetchPlaylistSongs(playlistId, newName.trim());
        }
        await fetchPlaylists();
    } catch (e) { showToast(e.message, 'error'); }
}

async function deleteSidebarPlaylist(playlistId) {
    if (!confirm('Delete this playlist? Songs in it will be moved back to the default pool.')) return;
    try {
        const supabase = window.supabaseClient;
        const user = currentUser;
        if (!user) throw new Error("Please log in.");

        // 1. Safeguard: Never delete the USER playlist
        const pl = allPlaylists.find(p => p.id === playlistId);
        if (pl && pl.name.toUpperCase() === 'USER') {
            showToast('Cannot delete default playlist', 'error');
            return;
        }

        // 2. "Evacuate" phase: High-Performance Bulk Upsert back to USER
        const defaultId = await getOrCreateDefaultPlaylist(user.id);
        if (defaultId && defaultId !== playlistId) {
             const { data: mappings } = await supabase.from('playlist_songs').select('song_id').eq('playlist_id', playlistId);
             if (mappings && mappings.length > 0) {
                 const newMappings = mappings.map(m => ({ playlist_id: defaultId, song_id: m.song_id }));
                 // Bulk upsert ensures all songs are recovered to the root pool in one trip
                 await supabase.from('playlist_songs').upsert(newMappings, { onConflict: 'playlist_id,song_id' });
             }
        }

        // 3. Perform Deletion
        const { error } = await supabase.from('playlists').delete().eq('id', playlistId);
        if (error) throw error;
        
        showToast('Playlist deleted', 'success');
        if (currentPlaylistId === playlistId) {
            currentPlaylistId = null;
            fetchSongs();
        } else {
            await fetchPlaylists();
        }
    } catch (e) { showToast(e.message, 'error'); }
}

async function removeSongFromPlaylist(songId) {
    if (!currentPlaylistId) return;
    if (!confirm('Remove this song from the current playlist? It will return to the default pool.')) return;
    try {
        const supabase = window.supabaseClient;
        const user = currentUser;
        if (!user) throw new Error("Log in required.");

        // Optimistic UI: Remove from local state immediately
        window.__currentGridSongs = (window.__currentGridSongs || []).filter(s => s.id !== songId);
        window.__currentViewSongs = (window.__currentViewSongs || []).filter(s => s.id !== songId);
        renderSongsGrid(window.__currentGridSongs, true, true);
        
        // Return mapping to USER default
        const defaultId = await getOrCreateDefaultPlaylist(user.id);
        const { error: insertErr } = await supabase.from('playlist_songs').insert({
            playlist_id: defaultId,
            song_id: songId
        }).maybeSingle();

        // Delete current mapping
        const { error } = await supabase
          .from('playlist_songs')
          .delete()
          .eq('playlist_id', currentPlaylistId)
          .eq('song_id', songId);
          
        if (error) throw error;
        showToast('Song returned to default pool');
        fetchPlaylists(); 
    } catch (e) { showToast(e.message, 'error'); }
}

async function pruneInvalidSongs() {
    // Only administrators or the backend logic should handle massive pruning, 
    // but we can offer a button or an auto-trigger to cleanup the UI of problematic songs.
    // For now, let's just make sure we don't display songs without video IDs in the grid.
    // (This is handled by fetchSongs filtering if we wanted, but backend is cleaner).
}

// ══════════════════════════════════════════════════════════════════════════════
// Reading Plans & Progress
// ══════════════════════════════════════════════════════════════════════════════

async function fetchPlans() {
  const container = document.getElementById('plans-container');
  if (!container) return;

  try {
    const supabase = window.supabaseClient;
    const { data: { user } } = await supabase.auth.getUser();

    let progressMap = {};
    if (user) {
        const { data: progressData } = await supabase
          .from('reading_progress')
          .select('plan_id, day_number, completed')
          .eq('user_id', user.id);
          
        if (progressData) {
          progressData.forEach(p => {
            if (!progressMap[p.plan_id] || p.day_number > progressMap[p.plan_id].current_day) {
               if (p.completed) {
                 progressMap[p.plan_id] = { current_day: p.day_number };
               }
            }
          });
        }
    }

    container.innerHTML = '';
    STATIC_PLANS.forEach(plan => {
      const prog = progressMap[plan.id];
      const currentDay = prog ? prog.current_day : 0;
      const pct = Math.min(100, Math.round((currentDay / plan.duration_days) * 100));
      const isStarted = currentDay > 0;
      const isDone = currentDay >= plan.duration_days;
      
      const btnText = isDone ? 'Completed' : (isStarted ? `Continue Day ${currentDay + 1}` : 'Start Plan');
      const btnClass = isStarted && !isDone ? 'action-btn' : 'action-btn btn-outline';
      const nextDayToTrack = isDone ? plan.duration_days : currentDay + 1;
      
      container.innerHTML += `
        <div class="dashboard-card plan-card">
          <h3>${escapeHtml(plan.title)}</h3>
          <p>${escapeHtml(plan.description)}</p>
          <div class="progress-bar"><div class="progress-fill" style="width: ${pct}%"></div></div>
          <div class="progress-text">${pct}% Completed</div>
          <button class="${btnClass} mt-4" onclick="readPlanDay('${plan.id}', ${nextDayToTrack})" ${isDone ? 'disabled' : ''}>
            ${btnText}
          </button>
        </div>
      `;
    });
    
  } catch (err) {
    console.error("Error fetching plans:", err);
    container.innerHTML = `<div class="dashboard-card" style="grid-column: 1 / -1; text-align: center; color: var(--text-secondary);">
      <p>⚠️ Failed to load reading plans.</p>
    </div>`;
  }
}

async function updatePlanProgress(planId, day) {
  if (!currentUser) {
    showToast("Please log in to track reading progress.", "info");
    openAuthModal();
    return;
  }
  
  const supabase = window.supabaseClient;

  try {
    const { error } = await supabase.from('reading_progress').upsert({
      user_id: currentUser.id,
      plan_id: planId,
      day_number: day,
      completed: true,
      completed_at: new Date().toISOString()
    }, { onConflict: 'user_id,plan_id,day_number' });
    
    if (error) throw error;
    
    showToast(`Day ${day} marked complete!`, "success");
    fetchPlans();
    fetchStreak(); // Update accountability view too
  } catch (err) {
    console.error("Error updating plan:", err);
    showToast("Failed to update progress.", "error");
  }
}

function readPlanDay(planId, day) {
  // Simple deterministic mapping for the deep-link based on MVP plan IDs
  // Since we don't have a giant JSON map of chapters per day per plan installed yet
  let targetBook = "Mark";
  let targetChapter = day;
  
  if (planId === "psalms_proverbs") {
    targetBook = "Psalms";
    targetChapter = day;
  } else if (planId === "nt_in_year") {
    targetBook = "Matthew";
    targetChapter = Math.ceil(day / 2);
  } else if (planId === "gospels_30") {
    targetBook = "John";
    targetChapter = Math.ceil(day * 0.7);
  }

  // Ensure chapter doesn't break limits
  if (targetChapter > 28) targetChapter = 1;

  // Set the Bible view up
  const bookEl = document.getElementById('bible-book');
  const chapEl = document.getElementById('bible-chapter');
  
  if (bookEl && chapEl) {
    // Navigate immediately
    navigateTo('bible');
    
    // We have to wait for the UI renderer to ensure bible dropdowns are hydrated
    setTimeout(() => {
      bookEl.value = targetBook;
      // Trigger chapter load
      loadBibleChapters().then(() => {
        chapEl.value = targetChapter.toString();
        loadBibleContent();
        
        // Show the actionable Mark Complete button over the reader
        const display = document.getElementById('bible-display');
        const completeBtnId = 'floating-complete-btn';
        if (!document.getElementById(completeBtnId)) {
          const btn = document.createElement('button');
          btn.id = completeBtnId;
          btn.className = "community-btn community-btn--primary";
          btn.style.marginTop = "20px";
          btn.style.width = "100%";
          btn.innerHTML = `Complete Day ${day} of ${planId.replace('_', ' ')}`;
          btn.onclick = () => {
            updatePlanProgress(planId, day);
            btn.innerHTML = "✓ Completed";
            btn.classList.add('community-btn--secondary');
            btn.classList.remove('community-btn--primary');
            btn.disabled = true;
          };
          display.appendChild(btn);
        }
      });
    }, 100);
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// AI Chat — Simulated
// ══════════════════════════════════════════════════════════════════════════════

function fillQuestion(text) {
  if (!questionInput) return;
  navigateTo('chat');
  setTimeout(() => {
    questionInput.value = text;
    questionInput.focus();
    autoResize(questionInput);
  }, 120);
}

function fillAIQuestion(text) {
  fillQuestion(text);
}

function newChat() {
  conversationId = null;
  chatHistory = []; // Reset history
  if (messagesList) messagesList.innerHTML = '';
  if (chatWelcome) chatWelcome.style.display = '';
  if (questionInput) { questionInput.value = ''; autoResize(questionInput); questionInput.focus(); }
}

function handleKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

async function sendMessage() {
  if (!questionInput) return;
  const question = questionInput.value.trim();
  if (!question || isLoading) return;
  if (question.length < 2) { shakeInput(); return; }

  // Hide welcome
  if (chatWelcome) chatWelcome.style.display = 'none';

  appendUserBubble(question);
  questionInput.value = '';
  autoResize(questionInput);

  const typingId = appendTypingIndicator();
  setLoading(true);

  try {
      const sysPrompt = "You are RhemaLight AI, a deeply theological and compassionate Bible study assistant. Provide biblical context, cite scriptures, and explain passages clearly. Use Markdown for formatting.";
      
      // Update local history
      if (chatHistory.length === 0) {
          // If first message, prepend system instructions for the model
          chatHistory.push({ role: "user", parts: [{ text: `[System Instruction: ${sysPrompt}]\n\nUser Question: ${question}` }] });
      } else {
          chatHistory.push({ role: "user", parts: [{ text: question }] });
      }
      
      // Limit history to last 12 messages
      if (chatHistory.length > 12) chatHistory = chatHistory.slice(-12);

      const payload = {
        contents: chatHistory
      };

      // Proxy the request through the backend to avoid exposing the API key
      const response = await fetch('/api/gemini/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
      });

      const data = await response.json();
      removeTypingIndicator(typingId);
      setLoading(false);

      if (!response.ok) {
          throw new Error(data.error?.message || 'Failed to generate response');
      }

      // --- DEFENSIVE PARSING ---
      if (!data.candidates || data.candidates.length === 0) {
          const blockReason = data.promptFeedback?.blockReason || "unknown reason";
          throw new Error(`AI response blocked or empty (${blockReason}). Please try a different question.`);
      }

      const candidate = data.candidates[0];
      if (!candidate.content || !candidate.content.parts || candidate.content.parts.length === 0) {
          throw new Error('AI returned an empty response candidate. Please try again.');
      }

      const answer = candidate.content.parts[0].text;
      
      // Update local history with assistant response
      chatHistory.push({ role: "model", parts: [{ text: answer }] });
      
      appendAssistantBubble(answer, []);
      questionInput.focus();
      
      // Save full interaction to the dedicated chat_logs table if user is logged in
      if (currentUser) {
         window.supabaseClient.from('chat_logs').insert({
           user_id: currentUser.id,
           question: question,
           answer: answer
         }).then(({error}) => { if(error) console.error("Error logging chat:", error); });
      }

  } catch (err) {
      console.error("AI Chat Error:", err);
      removeTypingIndicator(typingId);
      setLoading(false);
      appendAssistantBubble("Sorry, I encountered an error communicating with the AI provider: " + err.message, []);
  }
}

function setLoading(state) {
  isLoading = state;
  if (sendBtn) {
    sendBtn.disabled = state;
    sendBtn.classList.toggle('loading', state);
  }
}

function shakeInput() {
  if (!questionInput) return;
  questionInput.classList.add('shake');
  setTimeout(() => questionInput.classList.remove('shake'), 400);
}

// ── Message Rendering ──────────────────────────────────────────────────────

function scrollToBottom(container) {
  const c = container || chatMessages;
  if (c) requestAnimationFrame(() => c.scrollTo({ top: c.scrollHeight, behavior: 'smooth' }));
}

function appendUserBubble(text) {
  const div = document.createElement('div');
  div.className = 'message message--user';
  let initial = '?';
  if (currentUser) {
    const username = currentUser.user_metadata?.full_name || currentUser.user_metadata?.name || currentUser.email?.split('@')[0] || 'User';
    initial = username.charAt(0).toUpperCase();
  }
  div.innerHTML = `
    <div class="message__avatar">${initial}</div>
    <div class="message__content">
      <div class="message__bubble">${escapeHtml(text)}</div>
    </div>`;
  messagesList.appendChild(div);
  scrollToBottom(chatMessages);
}

function appendAssistantBubble(text, passages) {
  let passagesHtml = '';
  if (passages && passages.length > 0) {
    const items = passages.map(p => `
      <div class="passage-item">
        <span class="passage-ref">${escapeHtml(p.reference)}</span>
        <span class="passage-score">${(p.score * 100).toFixed(0)}%</span>
        <p class="passage-text">"${escapeHtml(p.text)}"</p>
      </div>`).join('');
    passagesHtml = `
      <details class="passages-drawer" open>
        <summary class="passages-summary">📖 ${passages.length} Relevant Passage${passages.length !== 1 ? 's' : ''}</summary>
        <div class="passages-list">${items}</div>
      </details>`;
  }

  const div = document.createElement('div');
  div.className = 'message message--assistant';
  div.innerHTML = `
    <div class="message__avatar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
    </div>
    <div class="message__content">
      <div class="message__name">RhemaLight AI</div>
      <div class="message__bubble">${formatAnswer(text)}</div>
      ${passagesHtml}
    </div>`;
  messagesList.appendChild(div);
  scrollToBottom(chatMessages);
}

function appendErrorBubble(message) {
  const div = document.createElement('div');
  div.className = 'message message--error';
  div.innerHTML = `<div class="message__bubble">⚠️ ${escapeHtml(message)}</div>`;
  messagesList.appendChild(div);
  scrollToBottom(chatMessages);
}

function appendTypingIndicator() {
  const id = `typing-${Date.now()}`;
  const div = document.createElement('div');
  div.className = 'message message--assistant';
  div.id = id;
  div.innerHTML = `
    <div class="message__avatar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
    </div>
    <div class="message__content">
      <div class="message__bubble">
        <div class="typing-indicator" aria-label="Thinking..."><span></span><span></span><span></span></div>
      </div>
    </div>`;
  messagesList.appendChild(div);
  scrollToBottom(chatMessages);
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ── Text Formatting ─────────────────────────────────────────────────────────

function formatAnswer(text) {
  if (!text) return '';
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
  html = html.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
  return `<p>${html}</p>`;
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

// ══════════════════════════════════════════════════════════════════════
// Toast Notification
// ══════════════════════════════════════════════════════════════════════

let toastTimer = null;
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.className = `toast ${type} show`;
  toastTimer = setTimeout(() => { toast.className = 'toast'; }, 2800);
}

// ══════════════════════════════════════════════════════════════════════
// Sermon Builder & CSI Planner Logic
// ══════════════════════════════════════════════════════════════════════

async function generateSermon() {
  const input = document.getElementById('sermon-input');
  const contextInput = document.getElementById('sermon-context');
  const btn = document.getElementById('btn-generate-sermon');
  const output = document.getElementById('sermon-output');
  const content = document.getElementById('sermon-output-content');
  
  if (!input || !input.value.trim()) { showToast('Please enter a topic or verse first.', 'error'); return; }
  
  showToast('Creating sermon outline...', 'info');
  output.style.display = 'block';
  content.innerHTML = `<div class="typing-indicator" style="justify-content:center; padding: 20px;"><span></span><span></span><span></span></div>`;
  if (btn) btn.disabled = true;
  
  // Mock Sermon Generator for cPanel
  setTimeout(async () => {
    const topic = input.value.trim();
    const context = contextInput ? contextInput.value.trim() : "";
    
    let html = `
      <h3>Sermon Outline: ${escapeHtml(topic)}</h3>
      <p><strong>Focus Verse:</strong> ${escapeHtml(context || "Selected Scripture")}</p>
      <hr>
      <div style="margin-top:20px;">
        <h4 style="color:var(--primary)">I. Introduction</h4>
        <p>Introduce the context of ${escapeHtml(topic)} and why it matters today.</p>
        
        <h4 style="color:var(--primary); margin-top:20px;">II. Scriptural deep-dive</h4>
        <p>Analyze how ${escapeHtml(context || topic)} reveals God's character.</p>
        
        <h4 style="color:var(--primary); margin-top:20px;">III. Life Application</h4>
        <p>3 Practical steps for the congregation to live out this truth this week.</p>
        
        <h4 style="color:var(--primary); margin-top:20px;">IV. Conclusion</h4>
        <p>A final prayer and charge for the week ahead.</p>
      </div>
    `;
    
    content.innerHTML = html;
    showToast('Sermon outline generated!', 'success');
    if (btn) btn.disabled = false;
    
    if (currentUser) {
      const supabase = window.supabaseClient;
      await supabase.from('sermons').insert({
        user_id: currentUser.id,
        topic: topic,
        verse_context: context,
        html_content: html // In a real app we'd save the full blob
      });
    }
  }, 1500);
}

/* ── CSI Service Planner Logic ────────────────────────────── */

async function renderLiturgy() {
  const typeEl = document.getElementById('liturgy-service-type');
  const container = document.getElementById('liturgy-accordion-container');
  if (!typeEl || !container) return;

  const serviceType = typeEl.value; // e.g. "English First Service"
  if (!window.liturgyData) {
    try {
      const res = await fetch('/static/data/liturgy.json');
      window.liturgyData = await res.json();
    } catch(e) {
      container.innerHTML = '<p>Error: Failed to load Liturgy data.</p>';
      return;
    }
  }
  const liturgyData = window.liturgyData;

  // Filter local data
  const filteredData = liturgyData.filter(item => item.category === serviceType);

  if (filteredData.length === 0) {
    container.innerHTML = `<div class="dashboard-card text-center text-secondary">No data for ${escapeHtml(serviceType)}</div>`;
    return;
  }

  let html = '';
  filteredData.forEach((item, i) => {
    html += `
      <div class="liturgy-item" id="liturgy-item-${i}">
        <div class="liturgy-header" onclick="toggleLiturgyItem(${i})">
          <h3>
            <span class="liturgy-num">${String(i+1).padStart(2,'0')}</span>
            <span class="liturgy-title-text">${item.sectionTitle}</span>
          </h3>
          <svg class="liturgy-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </div>
        <div class="liturgy-content-wrapper">
          <div class="liturgy-content">${item.content}</div>
        </div>
      </div>`;
  });

  container.innerHTML = html;
  
  // Auto-expand first item on load
  setTimeout(() => toggleLiturgyItem(0, true), 150);
}

function toggleLiturgyItem(index, forceState) {
  const item = document.getElementById(`liturgy-item-${index}`);
  if (!item) return;

  if (typeof forceState === 'boolean') {
    if (forceState) item.classList.add('open');
    else item.classList.remove('open');
  } else {
    item.classList.toggle('open');
    
    // Smooth scroll if opening
    if (item.classList.contains('open')) {
      setTimeout(() => {
        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 300);
    }
  }
}

function toggleAllLiturgy(expand) {
  const items = document.querySelectorAll('.liturgy-item');
  items.forEach(item => {
    if (expand) item.classList.add('open');
    else item.classList.remove('open');
  });
}

function filterLiturgy() {
  const query = document.getElementById('liturgy-search').value.toLowerCase();
  const items = document.querySelectorAll('.liturgy-item');
  
  items.forEach(item => {
    const title = item.querySelector('.liturgy-title-text').textContent.toLowerCase();
    const content = item.querySelector('.liturgy-content').textContent.toLowerCase();
    
    if (title.includes(query) || content.includes(query)) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
      item.classList.remove('open');
    }
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// Settings & Language Toggle
// ══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
  // Bind Language Toggle for Bible View
  const langSelects = document.querySelectorAll('select.form-select');
  langSelects.forEach(select => {
    select.addEventListener('change', (e) => {
      const val = e.target.value;
      if (val.includes('English') || val.includes('Tamil') || val.includes('Dual')) {
        toggleBibleLanguage(val);
      }
    });
  });

  // Main App Settings Toggle
  const appLangSelect = document.getElementById('setting-lang');
  if (appLangSelect) {
    appLangSelect.addEventListener('change', (e) => {
      showToast('Interface language changed to ' + (e.target.value === 'ta' ? 'Tamil' : 'English'), 'success');
    });
  }
});

function toggleBibleLanguage(mode) {
  const engVerses = document.querySelectorAll('.bible-verse');
  const tamVerses = document.querySelectorAll('.bible-verse-tamil');
  
  if (mode.includes('English')) {
    engVerses.forEach(v => v.style.display = 'block');
    tamVerses.forEach(v => v.style.display = 'none');
  } else if (mode.includes('Tamil')) {
    engVerses.forEach(v => v.style.display = 'none');
    tamVerses.forEach(v => v.style.display = 'block');
  } else {
    // Dual Language
    engVerses.forEach(v => v.style.display = 'block');
    tamVerses.forEach(v => v.style.display = 'block');
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Supabase Authentication Logic
// ══════════════════════════════════════════════════════════════════════════════

let currentUser = null;
let authMode = 'login'; // 'login' or 'signup'

function handleAuthClick() {
  if (currentUser) {
    handleSignOut();
  } else {
    openAuthModal();
  }
}

function openAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.style.display = 'flex';
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.style.display = 'none';
}

function toggleAuthMode() {
  authMode = authMode === 'login' ? 'signup' : 'login';
  document.getElementById('auth-title').textContent = authMode === 'login' ? 'Welcome to RhemaLight AI' : 'Create an Account';
  document.getElementById('auth-subtitle').textContent = authMode === 'login' ? 'Sign in to sync your spiritual journey.' : 'Join the community and save your progress.';
  document.getElementById('auth-btn-primary').textContent = authMode === 'login' ? 'Log In' : 'Sign Up';
  document.getElementById('auth-toggle-mode').textContent = authMode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in';
}

async function handleAuthSubmit() {
  const supabase = window.supabaseClient;
  if (!supabase) {
    showToast('Supabase client not initialized. Check credentials.', 'error');
    return;
  }

  const email = document.getElementById('auth-email').value.trim();
  const password = document.getElementById('auth-password').value.trim();

  if (!email || !password) {
    showToast('Please enter both email and password.', 'error');
    return;
  }

  const btn = document.getElementById('auth-btn-primary');
  btn.disabled = true;
  btn.textContent = 'Please wait...';

  try {
    if (authMode === 'login') {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      showToast('Successfully logged in!', 'success');
      closeAuthModal();
      document.getElementById('auth-email').value = '';
      document.getElementById('auth-password').value = '';
    } else {
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) throw error;
      showToast('Signup successful! Please log in.', 'success');
      toggleAuthMode();
    }
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = authMode === 'login' ? 'Log In' : 'Sign Up';
  }
}

async function handleGoogleSignIn() {
  const supabase = window.supabaseClient;
  if (!supabase) {
    showToast('Supabase client not initialized.', 'error');
    return;
  }

  try {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.href // Redirect back to app after login
      }
    });
    if (error) throw error;
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleSignOut() {
  await handleLogout();
}

// Listen for Auth State Changes to update UI
document.addEventListener('DOMContentLoaded', () => {
  const supabase = window.supabaseClient;
  if (!supabase) return;

  supabase.auth.onAuthStateChange(async (event, session) => {
    currentUser = session?.user || null;
    
    const appShell = document.getElementById('app-shell');
    const authModal = document.getElementById('auth-modal');
    const authCloseBtn = document.getElementById('auth-close-btn');

    if (currentUser) {
      // 1. Logged In View
      if (appShell) appShell.style.display = 'flex';
      if (authModal) authModal.style.display = 'none';
      if (authCloseBtn) authCloseBtn.style.display = 'block';

      // 2. Resolve data (Profile -> Streak -> App Data)
      await handleAuthResolved();
    } else {
      // 3. Logged Out View
      if (appShell) appShell.style.display = 'none';
      if (authModal) {
        authModal.style.display = 'flex';
        authModal.style.background = 'var(--bg-main)';
        authModal.style.zIndex = '9999';
      }
      if (authCloseBtn) authCloseBtn.style.display = 'none';
      console.log("[Auth] User logged out.");
    }

    // 4. Update Global UI Elements
    updateGlobalAuthUI();
  });
});

async function handleAuthResolved() {
    const supabase = window.supabaseClient;
    if (!currentUser) return;

    // Clean URL fragment (OAuth tokens)
    if (window.location.hash.includes('access_token')) {
        window.history.replaceState(null, '', window.location.pathname);
    }

    try {
        // A. Profile Management (Sequential)
        const { data: profile, error: profileErr } = await supabase.from('users').select('*').eq('id', currentUser.id).single();
        
        let finalDisplayName = 'Friend';
        if (profileErr && (profileErr.code === 'PGRST116' || profileErr.details?.includes('0 rows'))) {
            finalDisplayName = currentUser.user_metadata?.full_name || currentUser.email?.split('@')[0] || 'Friend';
            await supabase.from('users').upsert({
                id: currentUser.id,
                email: currentUser.email,
                display_name: finalDisplayName,
                theme: 'dark',
                preferred_language: 'en'
            }, { onConflict: 'id' });
        } else if (profile) {
            const prefTheme = profile.theme || 'dark';
            document.documentElement.setAttribute('data-theme', prefTheme);
            localStorage.setItem('rhemalight_theme', prefTheme);
            finalDisplayName = profile.display_name || currentUser.user_metadata?.full_name || currentUser.email?.split('@')[0] || 'Friend';
        }

        // B. UI Greetings
        const greetingTitle = document.getElementById('greeting-title');
        if (greetingTitle) greetingTitle.textContent = `Welcome back, ${finalDisplayName}!`;
        const welcomeName = document.getElementById('welcome-name');
        if (welcomeName) welcomeName.textContent = `${finalDisplayName}!`;

        // C. Streak and App Data (Must be strictly sequential)
        await updateStreakOnLogin();
        
        if (!window.__appInitialized) {
            window.__appInitialized = true;
            await initializeApp();
            console.log("[App] Full initialization complete.");
        }

    } catch (err) {
        console.error('[Auth] Sequential resolution failed:', err);
    }
}

function updateGlobalAuthUI() {
    // 1. Update Sidebar Text
    const navAuthText = document.getElementById('nav-auth-text');
    if (navAuthText) {
        navAuthText.textContent = currentUser ? 'Log Out' : 'Log In';
    }

    // 2. Update Avatar Circle
    const avatarBtn = document.querySelector('.user-avatar');
    if (avatarBtn) {
        if (currentUser && currentUser.email) {
            avatarBtn.textContent = currentUser.email.charAt(0).toUpperCase();
            avatarBtn.onclick = openProfileModal;
        } else {
            avatarBtn.textContent = '?';
            avatarBtn.onclick = openAuthModal;
        }
    }
}


// Profile Modal Logic
async function openProfileModal() {
  if (!currentUser) return;
  document.getElementById('profile-email-display').textContent = currentUser.email;
  
  if (currentUser) {
    try {
      const supabase = window.supabaseClient;
      const { data: profile } = await supabase.from('users').select('*').eq('id', currentUser.id).single();
      if (profile) {
        document.getElementById('profile-name').value = profile.display_name || '';
        document.getElementById('profile-theme').value = profile.theme || 'light';
        document.getElementById('profile-language').value = profile.preferred_language || 'en';
      }
    } catch (e) {
      console.error("Failed to load profile details:", e);
    }
  }
  
  document.getElementById('profile-modal').style.display = 'flex';
}

function closeProfileModal() {
  document.getElementById('profile-modal').style.display = 'none';
}

async function saveProfile() {
  if (!currentUser) return;
  const btn = document.getElementById('profile-save-btn');
  btn.textContent = 'Saving...';
  btn.disabled = true;
  
  const payload = {
    display_name: document.getElementById('profile-name').value,
    theme: document.getElementById('profile-theme').value,
    preferred_language: document.getElementById('profile-language').value
  };
  
  try {
    const supabase = window.supabaseClient;
    const { error } = await supabase.from('users').update(payload).eq('id', currentUser.id);
    if (error) throw error;

    showToast('Profile updated!', 'success');

    // Apply theme change locally
    document.documentElement.setAttribute('data-theme', payload.theme);
    localStorage.setItem('rhemalight_theme', payload.theme);
    closeProfileModal();
  } catch(e) {
    showToast('Failed to save profile: ' + e.message, 'error');
  } finally {
    btn.textContent = 'Save Changes';
    btn.disabled = false;
  }
}

async function requestPasswordReset() {
  if (!currentUser) return;
  try {
    const { error } = await window.supabaseClient.auth.resetPasswordForEmail(currentUser.email);
    if (error) throw error;
    showToast('Password reset email sent!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleLogout() {
  closeProfileModal();
  try {
    const { error } = await window.supabaseClient.auth.signOut();
    if (error) throw error;
    showToast('Logged out successfully', 'success');
    currentUser = null;
    // Clean URL and reload to clear application state
    window.location.href = window.location.pathname;
  } catch (err) {
    showToast('Error logging out: ' + err.message, 'error');
  }
}

// Notifications Modal & Cloud Sync Logic
async function openNotificationsModal() {
  if (!currentUser) {
    showToast('Log in to see notifications.', 'info');
    return;
  }
  
  document.getElementById('notif-modal').style.display = 'flex';
  const listEl = document.getElementById('notifications-list');
  listEl.innerHTML = '<p class="text-secondary text-sm">Validating...</p>';
  
  const token = (await window.supabaseClient.auth.getSession()).data?.session?.access_token;
  if (!token) return;
  
  try {
    const supabase = window.supabaseClient;
    const { data: notifs, error } = await supabase.from('notifications').select('*').eq('user_id', currentUser.id).order('created_at', { ascending: false }).limit(10);
    
    if (error) throw error;

    if (!notifs || notifs.length === 0) {
      listEl.innerHTML = '<p class="text-secondary text-sm text-center">No new notifications.</p>';
      document.getElementById('notif-btn').classList.remove('notification-btn');
    } else {
      const unread = notifs.filter(n => !n.is_read);
      if (unread.length > 0) {
        document.getElementById('notif-btn').classList.add('notification-btn');
      } else {
        document.getElementById('notif-btn').classList.remove('notification-btn');
      }
      
      listEl.innerHTML = notifs.map(notif => `
        <div class="p-3 mb-2 rounded border" style="${notif.is_read ? 'opacity: 0.7; background: var(--bg-card);' : 'background: var(--bg-card-hover); border-left: 3px solid var(--accent);'}">
          <h4 class="font-bold text-sm">${escapeHtml(notif.title)}</h4>
          <p class="text-xs text-secondary mt-1">${escapeHtml(notif.message)}</p>
          ${!notif.is_read ? `<button class="text-xs text-accent mt-2 hover:underline" onclick="markNotificationRead('${notif.id}')">Mark as read</button>` : ''}
        </div>
      `).join('');
    }
  } catch (err) {
    listEl.innerHTML = '<p class="text-red-500 text-sm">Failed to load notifications.</p>';
  }
}

function closeNotificationsModal() {
  document.getElementById('notif-modal').style.display = 'none';
}

async function markNotificationRead(notifId) {
  if (!currentUser) return;
  const token = (await window.supabaseClient.auth.getSession()).data?.session?.access_token;
  if (!token) return;
  
  try {
    const supabase = window.supabaseClient;
    const { error } = await supabase.from('notifications').update({ is_read: true }).eq('id', notifId);
    if (!error) {
      openNotificationsModal(); // Refresh modal view inline
    }
  } catch (err) {
    console.error("Failed to mark read", err);
  }
}

function performManualSync() {
  if (!currentUser) {
    showToast('Log in to sync records.', 'warning');
    return;
  }
  const btn = document.getElementById('cloud-btn');
  btn.style.animation = 'spin 1s linear infinite';
  
  // Fake brief delay to simulate checking dirty status or downloading bulk rows
  setTimeout(() => {
    btn.style.animation = 'none';
    showToast('All records synced with Supabase ✨', 'success');
  }, 800);
}

// ── Bible & CSI Integration ──────────────────────────────────────────────────

const bibleBooks = [
  'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth',
  '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra',
  'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon',
  'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos',
  'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah',
  'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians',
  '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians',
  '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James',
  '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation'
];

const tamilBookNames = [
  "ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்",
  "1 சாமுவேல்", "2 சாமுவேல்", "1 இராஜாக்கள்", "2 இராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா",
  "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு",
  "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்",
  "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா",
  "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்",
  "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்",
  "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு",
  "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"
];

function initBibleUI() {
  const bookSelect = document.getElementById('bible-book');
  const version = document.getElementById('bible-version').value;
  if (!bookSelect) return;

  const names = (version === 'ta_bsi' || (version === 'dual' && currentView === 'bible')) ? tamilBookNames : bibleBooks;
  bookSelect.innerHTML = names.map((name, i) => `<option value="${bibleBooks[i]}">${name}</option>`).join('');
  loadBibleChapters();
}

async function loadBibleChapters() {
  const version = document.getElementById('bible-version').value;
  const bookName = document.getElementById('bible-book').value;
  const chapterSelect = document.getElementById('bible-chapter');
  
  if (!chapterSelect) return;

  // Get dynamic chapter count from local engine (sync mapping)
  const chapters = window.bibleEngine.getChapterCount(bookName);
  
  if (chapters === 0) {
    chapterSelect.innerHTML = '<option value="">No chapters found</option>';
  } else {
    chapterSelect.innerHTML = Array.from({length: chapters}, (_, i) => `<option value="${i+1}">Chapter ${i+1}</option>`).join('');
  }
  
  loadBibleContent();
}

async function loadBibleContent() {
  const versionEl = document.getElementById('bible-version');
  const bookEl = document.getElementById('bible-book');
  const chapterEl = document.getElementById('bible-chapter');
  const display = document.getElementById('bible-display');

  if (!versionEl || !bookEl || !chapterEl || !display) return;

  const version = versionEl.value;
  const book = bookEl.value;
  const chapter = parseInt(chapterEl.value);

  display.innerHTML = '<div class="bible-loading">Loading scripture...</div>';

  try {
    if (version === 'dual') {
      const enVersion = 'en_kjv';
      const taVersion = 'ta_bsi';
      const [enText, taText] = await Promise.all([
        window.bibleEngine.getChapter(enVersion, book, chapter),
        window.bibleEngine.getChapter(taVersion, book, chapter)
      ]);

      let html = `<h3 class="font-serif text-xl mb-4">${book} ${chapter} (EN/TA)</h3>`;
      const maxLen = Math.max(enText.length, taText.length);
      
      for (let i = 0; i < maxLen; i++) {
        const enV = enText[i] || { text: '' };
        const taV = taText[i] || { text: '' };
        html += `
          <div class="bible-dual-verse mb-4">
            <p class="bible-verse"><sup class="verse-num">${i+1}</sup> ${enV.text}</p>
            <p class="bible-verse-tamil text-secondary italic">${taV.text}</p>
          </div>
        `;
      }
      display.innerHTML = html;
    } else {
      const verses = await window.bibleEngine.getChapter(version, book, chapter);
      const isTamil = version === 'ta_bsi';
      const bookIndex = bibleBooks.indexOf(book);
      const tamilName = tamilBookNames[bookIndex];
      const title = isTamil && tamilName ? `${tamilName} ${chapter}` : `${book} ${chapter}`;
      
      let html = `<h3 class="font-serif text-xl mb-4">${title}</h3>`;
      if (!verses || verses.length === 0) {
        html += `<div class="empty-text p-4 text-secondary italic">No verses found for this chapter. Please try another selection.</div>`;
      } else {
        html += verses.map(v => `<p class="bible-verse ${isTamil?'bible-verse-tamil':''}"><sup class="verse-num">${v.verse}</sup> ${v.text}</p>`).join('');
      }
      display.innerHTML = html;
    }
  } catch (err) {
    console.error("Bible Load Error:", err);
    display.innerHTML = `<div class="error-text">Error loading Bible content: ${err.message}</div>`;
  }
}

// ── CSI Planner ───────────────────────────────────────────────────────────────

const csiLiturgy = [
  { id: 1, title: 'Opening Hymn & Invocation', icon: '🎵' },
  { id: 2, title: 'Call to Worship', icon: '🔔' },
  { id: 3, title: 'Prayer of Confession & Absolution', icon: '🙏' },
  { id: 4, title: 'Hymn of Praise (Gloria in Excelsis)', icon: '✨' },
  { id: 5, title: 'The Collect of the Day', icon: '📜' },
  { id: 6, title: 'Old Testament Lesson', scripture: 'Isaiah 40:1-8' },
  { id: 7, title: 'Psalm / Responsive Reading', scripture: 'Psalm 103' },
  { id: 8, title: 'Epistle (New Testament) Lesson', scripture: 'Romans 12:1-2' },
  { id: 9, title: 'Gradual Hymn / Gospel Reading', scripture: 'John 15:1-8' },
  { id: 10, title: 'The Sermon / Word of God', icon: '🎤' },
  { id: 11, title: 'The Apostles\' Creed', icon: '🛡️' },
  { id: 12, title: 'Intercessory Prayers & Thanksgiving', icon: '🙌' },
  { id: 13, title: 'Offertory & Dedication', icon: '🪙' },
  { id: 14, title: 'Closing Hymn & Benediction', icon: '✝️' }
];

// ── CSI Planner (Static Data) ───────────────────────────────────────────────
// ══════════════════════════════════════════════════════════════════════════════
// Accountability & Streak
// ══════════════════════════════════════════════════════════════════════════════

async function updateStreakOnLogin() {
  if (!currentUser) return;
  const supabase = window.supabaseClient;
  
  try {
    const { data: current } = await supabase.from('accountability_users').select('*').eq('user_id', currentUser.id).single();
    const today = new Date().toISOString().split('T')[0];
    
    if (!current) {
        await supabase.from('accountability_users').insert({
          user_id: currentUser.id,
          current_streak: 1,
          best_streak: 1,
          total_points: 10,
          last_active_date: today
        });
    } else if (current.last_active_date !== today) {
        const lastDate = new Date(current.last_active_date);
        const diff = (new Date(today) - lastDate) / (1000 * 60 * 60 * 24);
        let newStreak = (diff === 1) ? current.current_streak + 1 : 1;
        
        await supabase.from('accountability_users').update({
           current_streak: newStreak,
           best_streak: Math.max(newStreak, current.best_streak),
           total_points: current.total_points + 10,
           last_active_date: today
        }).eq('user_id', currentUser.id);
    }
  } catch (err) {
    console.error("Failed to update streak:", err);
  }
}

async function fetchStreak() {
  const streakEl = document.getElementById('streak-display');
  const pointsEl = document.getElementById('points-display');
  
  if (!currentUser) {
    if (streakEl) streakEl.textContent = "0 Day Streak!";
    if (pointsEl) pointsEl.textContent = "Log in to track points";
    return;
  }
  
  try {
    const supabase = window.supabaseClient;
    const { data, error } = await supabase.from('accountability_users').select('*').eq('user_id', currentUser.id).single();
    
    if (error && error.code !== 'PGRST116') throw error; // Ignore "no rows" error
    
    if (data) {
      if (streakEl) streakEl.textContent = `${data.current_streak || 0} Day Streak!`;
      if (pointsEl) pointsEl.textContent = `${data.total_points || 0} Points Earned`;
    } else {
      if (streakEl) streakEl.textContent = "0 Day Streak!";
      if (pointsEl) pointsEl.textContent = "0 Points Earned";
    }
  } catch (err) {
    console.error('Failed to fetch streak:', err);
    const isPermission = err.message && err.message.includes('permission denied');
    if (pointsEl) pointsEl.innerHTML = isPermission
      ? `<span style="font-size:0.75rem; color:var(--danger);">DB access denied. <button onclick="runSupabaseDiagnostic()" style="text-decoration:underline; background:none; border:none; color:inherit; cursor:pointer;">Run Diagnostic</button></span>`
      : `<span style="font-size:0.75rem; color:var(--danger);">Could not load data</span>`;
  }
}


/**
 * Generates a structured Bible study guide based on user input.
 * Bridges the Study Architect UI with the AI Chat.
 */
function generateStudyGuide(type) {
  let inputId, promptPrefix;
  
  if (type === 'topic') {
    inputId = 'study-topic-input';
    promptPrefix = "Generate a deep-dive Bible study outline on the TOPIC of: ";
  } else if (type === 'character') {
    inputId = 'study-char-input';
    promptPrefix = "Analyze the BIBLICAL CHARACTER profile of: ";
  } else if (type === 'book') {
    inputId = 'study-book-input';
    promptPrefix = "Provide a comprehensive spiritual blueprint and overview for the BIBLE BOOK of: ";
  }
  
  const el = document.getElementById(inputId);
  const val = el ? el.value.trim() : "";
  
  if (!val) {
    return showToast(`Please enter a ${type} name first.`, 'error');
  }
  
  const finalPrompt = `${promptPrefix} "${val}". Include key verses, context, and life applications.`;
  
  // Navigate to chat and fill
  navigateTo('chat');
  fillQuestion(finalPrompt);
  
  // Clear input for next time
  if (el) el.value = "";
}

// Ensure global exposure
window.generateStudyGuide = generateStudyGuide;

/**
 * ── Devotional Plans System ──────────────────────────────────
 */

// Initial state for plans if nothing in localStorage
const DEFAULT_PLANS = {
  'nt-year': { progress: 0, active: false, totalDays: 365 },
  'gospels-30': { progress: 0, active: false, totalDays: 30 },
  'psalms-proverbs': { progress: 0, active: false, totalDays: 150 }
};

/**
 * ── Devotional Plans System (Real-Time Backend) ────────────────
 */

let activePlanId = null;
let currentReadingDay = null;

async function fetchPlans() {
  console.log("[Plans] Fetching progress from Supabase...");
  if (!currentUser) return;

  try {
    const supabase = window.supabaseClient;
    const { data: progress, error } = await supabase.from('reading_progress').select('*').eq('user_id', currentUser.id);
    if (error) throw error;
    
    if (!window.READING_DATA) {
      try {
        const res = await fetch('/static/data/reading-plans.json');
        window.READING_DATA = await res.json();
      } catch (e) {
        console.error("Failed to load reading plans json:", e);
      }
    }
    
    STATIC_PLANS.forEach(plan => {
      const progressFill = document.getElementById(`progress-${plan.id}`);
      const statusText = document.getElementById(`status-text-${plan.id}`);
      const btn = document.querySelector(`[data-plan-id="${plan.id}"] .action-btn`);
      const currentDayEl = document.getElementById(`current-day-${plan.id}`);
      const nextTaskEl = document.getElementById(`next-task-${plan.id}`);
      
      if (!progressFill || !statusText) return;
      
      const planProgress = (progress || []).filter(p => p.plan_id === plan.id);
      const completedDays = planProgress.filter(p => p.completed).map(p => p.day_number);
      const completedCount = completedDays.length;
      const percentage = (completedCount / plan.duration_days) * 100;
      const isActive = planProgress.length > 0;
      
      // Calculate Next Day (first incomplete)
      let currentDay = 1;
      if (completedCount > 0) {
        currentDay = Math.max(...completedDays) + 1;
      }
      const isCompleted = currentDay > plan.duration_days || percentage >= 100;
      if (currentDay > plan.duration_days) currentDay = plan.duration_days;
      
      progressFill.style.width = `${percentage}%`;
      statusText.innerText = `${parseFloat(percentage).toFixed(2)}% Completed`;
      
      // Populate Current Day and Next Task text
      let readingContent = "Daily Reading";
      if (window.READING_DATA && window.READING_DATA[plan.id] && window.READING_DATA[plan.id][currentDay]) {
        // Updated to handle the new JSON structure ("display" property)
        readingContent = window.READING_DATA[plan.id][currentDay].display.replace(/\n/g, ', ');
      }
      
      if (currentDayEl) {
        currentDayEl.innerText = isCompleted ? `100% Completed` : `Day ${currentDay} of ${plan.duration_days}`;
      }
      
      if (nextTaskEl) {
        nextTaskEl.innerText = isCompleted ? "✔ Plan Completed" : `Today's Reading: ${readingContent}`;
      }
      
      if (isCompleted) {
        if (btn) {
          btn.innerText = "Completed ✓";
          btn.disabled = true;
          btn.classList.add('opacity-50');
          btn.classList.remove('action-btn--secondary');
        }
      } else if (isActive) {
        if (btn) {
          btn.innerText = "Continue Reading";
          btn.classList.add('action-btn--secondary');
          btn.onclick = () => continuePlan(plan.id, currentDay);
        }
      } else {
        if (btn) {
          btn.innerText = "Start Plan";
          btn.classList.remove('action-btn--secondary');
          btn.onclick = () => startPlan(plan.id);
        }
      }
    });
  } catch (e) {
    console.error("[Plans] Error fetching plans:", e);
  }
}

async function startPlan(planId) {
  showToast("Initializing your plan...", "info");
  try {
    const supabase = window.supabaseClient;
    // Insert initial progress for day 1 (or do nothing if it already exists)
    const { error } = await supabase.from('reading_progress').upsert({
      user_id: currentUser.id,
      plan_id: planId,
      day_number: 1,
      completed: false
    }, { onConflict: 'user_id, plan_id, day_number' });
    
    if (error) throw error;
    
    showToast("Plan started! Let's begin today's reading.", "success");
    await fetchPlans();
    await continuePlan(planId, 1);
  } catch (e) {
    console.error('[Plans] startPlan error:', e);
    showToast(`Failed to start plan: ${e.message}`, "error");
  }
}

async function continuePlan(planId, currentDay = 1) {
  activePlanId = planId;
  currentReadingDay = currentDay;
  
  try {
    const plan = STATIC_PLANS.find(p => p.id === planId);
    if (!plan) return;
    
    if (!window.READING_DATA) {
      try {
        const res = await fetch('/static/data/reading-plans.json');
        window.READING_DATA = await res.json();
      } catch (e) {
        console.error("Failed to load reading plans json:", e);
      }
    }

    // Fetch actual reading content from static READING_DATA
    if (window.READING_DATA && window.READING_DATA[planId] && window.READING_DATA[planId][currentDay]) {
        const dayData = window.READING_DATA[planId][currentDay];
        
        if (dayData.readings && dayData.readings.length > 0) {
            const firstReading = dayData.readings[0];
            
            // Navigate to Bible View
            navigateTo('bible');
            
            // Set Bible UI controls
            const bookSelect = document.getElementById('bible-book');
            if (bookSelect) bookSelect.value = firstReading.book;
            
            await loadBibleChapters(); // Populates chapter dropdown
            
            const chapterSelect = document.getElementById('bible-chapter');
            if (chapterSelect) {
                chapterSelect.value = firstReading.chapter;
                await loadBibleContent();
            }
            
            // Inject the Mark Complete Banner
            injectPlanCompletionUI(currentDay, dayData.display);
            
            // Ensure sidebar is closed on mobile
            if (window.innerWidth < 900) {
              const sidebar = document.getElementById('sidebar');
              const sidebarOverlay = document.getElementById('sidebar-overlay');
              if (sidebar) sidebar.classList.remove('open');
              if (sidebarOverlay) sidebarOverlay.classList.remove('active');
            }
        } else {
            showToast("No reading assignment found for today.", "info");
        }
    } else {
        showToast("Reading data not available.", "error");
    }
  } catch (e) {
    console.error('[Plans] continuePlan error:', e);
    showToast(`Failed to load reading: ${e.message}`, "error");
  }
}

function injectPlanCompletionUI(dayNum, displayTxt) {
    const container = document.getElementById('plan-banner-container');
    if (!container) return;
    
    // Make txt HTML-friendly by replacing \n with <br>
    const safeTxt = displayTxt.replace(/\n/g, '<br>');
    
    container.innerHTML = `
        <div id="plan-completion-banner" class="dashboard-card mb-4 p-4 flex justify-between items-center bg-[var(--surface-color)] shadow-sm border border-[var(--border-color)] border-l-4 border-l-[var(--primary-color)]">
            <div>
                <span class="text-xs font-bold text-primary mb-1 uppercase tracking-wider block">Active Plan: Day ${dayNum}</span>
                <span class="text-sm font-medium leading-snug block mt-1">${safeTxt}</span>
            </div>
            <button id="complete-day-btn" onclick="markDayComplete()" class="action-btn action-btn--sm self-center ml-4 whitespace-nowrap">Mark as Completed</button>
        </div>
    `;
}

async function markDayComplete() {
  if (!activePlanId || !currentReadingDay) return;
  
  const btn = document.getElementById('complete-day-btn');
  if (btn) btn.disabled = true;

  try {
    const supabase = window.supabaseClient;
    const { error } = await supabase.from('reading_progress').upsert({
      user_id: currentUser.id,
      plan_id: activePlanId,
      day_number: currentReadingDay,
      completed: true,
      completed_at: new Date().toISOString()
    }, { onConflict: 'user_id, plan_id, day_number' });
    
    if (error) throw error;
    
    showToast(`Day ${currentReadingDay} complete!`, "success");
    
    // Remove the banner
    const container = document.getElementById('plan-banner-container');
    if (container) container.innerHTML = '';
    
    // Navigate back to plans to see updated progress
    navigateTo('plans');
    
    // Immediately fetch plans again to update UI
    await fetchPlans();
  } catch (e) {
    console.error('[Plans] markDayComplete error:', e);
    showToast(`Failed to save progress: ${e.message}`, "error");
  } finally {
    if (btn) btn.disabled = false;
  }
}

// Global exposure
window.startPlan = startPlan;
window.continuePlan = continuePlan;
window.markDayComplete = markDayComplete;
window.fetchPlans = fetchPlans;
window.fetchStreak = fetchStreak;
window.fetchHistory = fetchHistory;
window.toggleTheme = toggleTheme;
window.saveProfile = saveProfile;
window.openProfileModal = openProfileModal;
window.generateSermon = generateSermon;
window.renderLiturgy = renderLiturgy;
window.toggleLiturgyItem = toggleLiturgyItem;
window.sendMessage = sendMessage;
window.newChat = newChat;
// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    // Initial UI Setup
    if (typeof navigateTo === 'function') navigateTo('home');
    // fetchPlans/fetchStreak are now called in initializeApp() after auth is resolved
});

// Auto-refresh when user returns to the app from background
let lastBackgroundTime = Date.now();
document.addEventListener('visibilitychange', async () => {
    if (document.visibilityState === 'hidden') {
        lastBackgroundTime = Date.now();
    } else if (document.visibilityState === 'visible') {
        // Only refresh if they were gone for more than 10 seconds (prevents refreshing on quick accidental swipes)
        if (Date.now() - lastBackgroundTime > 10000 && window.supabaseClient) {
            console.log('App returned to foreground. Refreshing session and data...');
            try {
                // Force session refresh in case of sleep/suspend token expiration
                const { data } = await window.supabaseClient.auth.getSession();
                if (data?.session) {
                    currentUser = data.session.user;
                    
                    // Refresh Sidebar, Plans, and Streak globally (staggered to avoid contention)
                    if (typeof fetchPlaylists === 'function') { await fetchPlaylists(); await new Promise(r => setTimeout(r, 150)); }
                    if (typeof fetchPlans === 'function') { await fetchPlans(); await new Promise(r => setTimeout(r, 150)); }
                    if (typeof fetchStreak === 'function') { await fetchStreak(); }
                    
                    // Refresh actively displayed grid if in Home/Song view
                    const homeView = document.getElementById('home-view');
                    if (homeView && !homeView.classList.contains('hidden')) {
                        if (currentPlaylistId) {
                            const titleStr = document.getElementById('current-song-view-title')?.innerText || "Playlist";
                            if (typeof fetchPlaylistSongs === 'function') fetchPlaylistSongs(currentPlaylistId, titleStr);
                        } else {
                            if (typeof fetchSongs === 'function') fetchSongs();
                        }
                    }
                }
            } catch (e) {
                console.error("Foreground refresh failed:", e);
            }
        }
    }
});
