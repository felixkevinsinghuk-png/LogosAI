/**
 * group.js — Community Group Chat (Supabase Realtime Integration)
 */

// ── State ────────────────────────────────────────────────────────────────────
let currentRoomCode  = null;
let currentGroupId   = null;
let currentUserName  = 'Anonymous';
let realtimeChannel  = null;

// ── DOM Elements ──────────────────────────────────────────────────────────────
const mainArea             = document.getElementById('view-home') || document.querySelector('.view');
const groupArea            = document.getElementById('view-group');
const groupMessageList     = document.getElementById('group-messages-list');
const groupWelcomeScreen   = document.getElementById('group-welcome-screen');
const activeRoomCodeDisplay= document.getElementById('active-room-code');
const bigRoomCodeDisplay   = document.getElementById('big-room-code');
const groupInput           = document.getElementById('group-input');
const createError          = document.getElementById('create-error');
const joinError            = document.getElementById('join-error');
const groupChatTitle       = document.getElementById('group-chat-title');
const groupChatSubtitle    = document.getElementById('group-chat-subtitle');
const communityPanel       = document.getElementById('community-panel');

const stages = {
  create: document.getElementById('stage-create'),
  join:   document.getElementById('stage-join'),
};
const tabs = {
  create: document.getElementById('tab-create'),
  join:   document.getElementById('tab-join'),
};

let activeCommunityTab = null;

// ── Community Tab Toggle ──────────────────────────────────────────────────────

function switchCommunityStage(stageName) {
  if (!currentUser) {
    showToast('Please log in to use community features.', 'info');
    openAuthModal();
    return;
  }

  const target = stages[stageName];
  const tab    = tabs[stageName];

  // Toggle off if already active
  if (activeCommunityTab === stageName) {
    communityPanel.classList.remove('expanded');
    tab.classList.remove('active');
    setTimeout(() => {
      if (target) target.style.display = 'none';
    }, 400);
    activeCommunityTab = null;
    return;
  }

  // Open new stage
  communityPanel.classList.add('expanded');

  // Hide all stages, deactivate all tabs
  Object.values(stages).forEach(s => { if (s) s.style.display = 'none'; });
  Object.values(tabs).forEach(t => { if (t) t.classList.remove('active'); });

  // Show target (flex column layout)
  if (target && tab) {
    target.style.display = 'flex';
    target.style.flexDirection = 'column';
    tab.classList.add('active');
    activeCommunityTab = stageName;
    const firstInput = target.querySelector('input');
    if (firstInput) setTimeout(() => firstInput.focus(), 350);
  }

  clearErrors();
}

// Auto-uppercase room code input
const joinCodeEl = document.getElementById('join-code');
if (joinCodeEl) {
  joinCodeEl.addEventListener('input', e => {
    e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
  });
}

// ── Create Group ──────────────────────────────────────────────────────────────

async function submitCreateGroup() {
  const nameInput  = document.getElementById('create-name').value.trim();
  const groupName  = document.getElementById('create-group-name').value.trim();
  const btn        = document.getElementById('btn-submit-create');
  const btnText    = document.getElementById('create-btn-text');

  clearErrors();

  if (!nameInput) { showError('create', 'Please enter your display name.'); return; }
  if (!groupName) { showError('create', 'Please enter a group name.');      return; }
  
  const supabase = window.supabaseClient;
  if (!supabase || !currentUser) return;

  btn.disabled = true;
  btnText.textContent = 'Creating…';

  try {
    const roomCode = generateRoomCode();

    // Insert Group
    const { data: groupData, error: groupErr } = await supabase.from('groups').insert({
      room_code: roomCode,
      group_name: groupName,
      created_by: currentUser.id
    }).select().single();

    if (groupErr) throw groupErr;

    // Insert Member (Creator)
    const { error: memberErr } = await supabase.from('group_members').insert({
      group_id: groupData.id,
      user_id: currentUser.id
    });

    if (memberErr) throw memberErr;

    btnText.textContent = 'Created! ✓';
    setTimeout(() => {
      btn.disabled = false;
      btnText.textContent = 'Create Room';
      enterGroupRoom(groupData.id, roomCode, nameInput, groupName);
    }, 700);

  } catch (err) {
    showError('create', err.message);
    btn.disabled = false;
    btnText.textContent = 'Create Room';
  }
}

// ── Join Group ────────────────────────────────────────────────────────────────

async function submitJoinGroup() {
  const nameInput = document.getElementById('join-name').value.trim();
  const codeInput = document.getElementById('join-code').value.trim().toUpperCase();
  const btn       = document.getElementById('btn-submit-join');
  const btnText   = document.getElementById('join-btn-text');

  clearErrors();

  if (!nameInput)       { showError('join', 'Please enter your display name.');  return; }
  if (!codeInput)       { showError('join', 'Please enter the room code.');       return; }
  if (codeInput.length !== 6) { showError('join', 'Room code must be 6 characters.'); return; }

  const supabase = window.supabaseClient;
  if (!supabase || !currentUser) return;

  btn.disabled = true;
  btnText.textContent = 'Joining…';

  try {
    // Check if group exists
    const { data: groupData, error: groupErr } = await supabase.from('groups')
      .select('*').eq('room_code', codeInput).single();

    if (groupErr || !groupData) throw new Error('Room not found. Check the code.');

    // Count members
    const { count, error: countErr } = await supabase.from('group_members')
      .select('*', { count: 'exact', head: true })
      .eq('group_id', groupData.id);
      
    if (count >= 13) throw new Error('This room is full (max 13 members).');

    // Insert member (ignoring unique constraint errors if already a member)
    const { error: memberErr } = await supabase.from('group_members').upsert({
      group_id: groupData.id,
      user_id: currentUser.id
    }, { onConflict: 'group_id,user_id' });

    if (memberErr) throw memberErr;

    btnText.textContent = 'Joined! ✓';
    setTimeout(() => {
      btn.disabled = false;
      btnText.textContent = 'Join Room';
      enterGroupRoom(groupData.id, codeInput, nameInput, groupData.group_name);
    }, 600);

  } catch(err) {
    showError('join', err.message);
    btn.disabled = false;
    btnText.textContent = 'Join Room';
  }
}

// ── Room Entry / Exit ─────────────────────────────────────────────────────────

async function enterGroupRoom(groupId, roomCode, userName, roomTitle) {
  currentGroupId = groupId;
  currentRoomCode = roomCode;
  currentUserName = userName;

  // Update UI
  if (activeRoomCodeDisplay) activeRoomCodeDisplay.textContent = roomCode;
  if (bigRoomCodeDisplay)    bigRoomCodeDisplay.textContent    = roomCode;
  if (groupChatTitle)        groupChatTitle.textContent        = roomTitle;

  // Clear messages
  if (groupMessageList) groupMessageList.innerHTML = '';
  if (groupWelcomeScreen) groupWelcomeScreen.style.display = 'flex';

  navigateTo('group');

  // Load existing history and Setup Realtime
  await loadChatHistory(groupId);
  setupRealtimeSubscription(groupId);

  updateParticipantBadge(groupId);
}

function exitGroup() {
  if (realtimeChannel) {
    window.supabaseClient.removeChannel(realtimeChannel);
    realtimeChannel = null;
  }
  currentGroupId = null;
  currentRoomCode = null;
  navigateTo('home');
}

async function updateParticipantBadge(groupId) {
  if (!groupChatSubtitle) return;
  const { count } = await window.supabaseClient.from('group_members')
    .select('*', { count: 'exact', head: true }).eq('group_id', groupId);
  
  groupChatSubtitle.innerHTML = `Participants: <span class="badge-count">${count || 1}</span> / 13`;
}

// ── Chat Realtime & DB ────────────────────────────────────────────────────────

async function loadChatHistory(groupId) {
  const { data, error } = await window.supabaseClient.from('messages')
    .select('message, users(name, email), user_id')
    .eq('group_id', groupId)
    .order('created_at', { ascending: true });

  if (!error && data) {
    if (data.length > 0 && groupWelcomeScreen) groupWelcomeScreen.style.display = 'none';
    data.forEach(msg => {
      const isSelf = msg.user_id === currentUser.id;
      const senderName = isSelf ? 'You' : (msg.users?.name || msg.users?.email || 'Unknown');
      appendGroupMessage(senderName, msg.message, isSelf);
    });
  }
}

function setupRealtimeSubscription(groupId) {
  const supabase = window.supabaseClient;
  
  realtimeChannel = supabase.channel(`room:${groupId}`)
    .on('postgres_changes', { 
      event: 'INSERT', 
      schema: 'public', 
      table: 'messages',
      filter: `group_id=eq.${groupId}` 
    }, async (payload) => {
      // Ignore our own messages (handled optimistically)
      if (payload.new.user_id === currentUser.id) return;
      
      if (groupWelcomeScreen) groupWelcomeScreen.style.display = 'none';

      // Fetch the sender's name
      let senderName = 'Member';
      const { data } = await supabase.from('users').select('name, email').eq('id', payload.new.user_id).single();
      if (data) senderName = data.name || data.email;

      appendGroupMessage(senderName, payload.new.message, false);
    })
    .subscribe();
}

async function sendGroupMessage() {
  if (!groupInput || !currentGroupId) return;
  const text = groupInput.value.trim();
  if (!text) return;

  // Optimistic UI update
  appendGroupMessage('You', text, true);
  if (groupWelcomeScreen) groupWelcomeScreen.style.display = 'none';
  
  groupInput.value = '';
  groupInput.style.height = 'auto';
  groupInput.focus();

  // Send to DB
  const { error } = await window.supabaseClient.from('messages').insert({
    group_id: currentGroupId,
    user_id: currentUser.id,
    message: text
  });

  if (error) {
    showToast('Failed to send message: ' + error.message, 'error');
  }
}

function handleGroupKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendGroupMessage();
  }
}

// ── Room Code ─────────────────────────────────────────────────────────────────

function generateRoomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

async function copyRoomCode() {
  if (!currentRoomCode) return;
  try {
    await navigator.clipboard.writeText(currentRoomCode);
    const original = activeRoomCodeDisplay.textContent;
    activeRoomCodeDisplay.textContent = 'COPIED!';
    if (bigRoomCodeDisplay) bigRoomCodeDisplay.textContent = 'COPIED!';
    setTimeout(() => {
      activeRoomCodeDisplay.textContent = currentRoomCode;
      if (bigRoomCodeDisplay) bigRoomCodeDisplay.textContent = currentRoomCode;
    }, 1500);
    showToast('Room code copied!', 'success');
  } catch {
    showToast('Copy failed — code: ' + currentRoomCode, 'info');
  }
}

// ── Rendering ─────────────────────────────────────────────────────────────────

function appendSystemMessage(message) {
  if (!groupMessageList) return;
  const div = document.createElement('div');
  div.className = 'message message--system';
  div.innerHTML = `<div class="system-bubble">${escapeHtml(message)}</div>`;
  groupMessageList.appendChild(div);
  scrollGroupToBottom();
}

function appendGroupMessage(senderName, text, isSelf) {
  if (!groupMessageList) return;
  const initial = senderName && typeof senderName === 'string' ? senderName.charAt(0).toUpperCase() : '?';
  const escaped = escapeHtml(text).replace(/\n/g, '<br>');

  const div = document.createElement('div');
  div.className = `message ${isSelf ? 'message--user' : 'message--other'}`;
  div.innerHTML = `
    <div class="message__avatar">${initial}</div>
    <div class="message__content">
      <div class="message__name">${escapeHtml(senderName)}</div>
      <div class="message__bubble"><p>${escaped}</p></div>
    </div>`;
  groupMessageList.appendChild(div);
  scrollGroupToBottom();
}

function scrollGroupToBottom() {
  const container = document.getElementById('group-messages-window');
  if (container) requestAnimationFrame(() => container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' }));
}

// ── Error Helpers ─────────────────────────────────────────────────────────────

function showError(stage, msg) {
  const el = stage === 'create' ? createError : joinError;
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  el.classList.add('shake');
  setTimeout(() => el.classList.remove('shake'), 400);
}

function clearErrors() {
  if (createError) { createError.textContent = ''; createError.style.display = 'none'; }
  if (joinError)   { joinError.textContent   = ''; joinError.style.display   = 'none'; }
}
