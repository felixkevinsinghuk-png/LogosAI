/**
 * group.js
 * Handles the Group Chat functionality.
 * - Modals for creating/joining
 * - WebSocket connection logic
 * - Rendering messages
 */

let groupSocket = null;
let currentRoomCode = null;
let currentUserName = "Anonymous";

// DOM Elements
const mainArea = document.querySelector(".chat-area:not(.group-area)");
const groupArea = document.getElementById("group-area");
const groupMessageList = document.getElementById("group-messages-list");
const groupWelcomeScreen = document.getElementById("group-welcome-screen");
const activeRoomCodeDisplay = document.getElementById("active-room-code");
const bigRoomCodeDisplay = document.getElementById("big-room-code");
const groupInput = document.getElementById("group-input");
const joinError = document.getElementById("join-error");
const groupChatTitle = document.getElementById("group-chat-title");
const groupChatSubtitle = document.getElementById("group-chat-subtitle");

const stages = {
    create: document.getElementById("community-stage-create"),
    join: document.getElementById("community-stage-join")
};

const tabs = {
    create: document.getElementById("tab-create"),
    join: document.getElementById("tab-join")
};

const expandWrapper = document.getElementById("community-expand-wrapper");

// --- Unified Sidebar Management ---

function switchCommunityStage(stageName) {
    const target = stages[stageName];
    const tab = tabs[stageName];

    // Check if we are clicking the already active tab to collapse
    if (tab && tab.classList.contains("active")) {
        // Collapse
        expandWrapper.classList.remove("expanded");
        tab.classList.remove("active");
        setTimeout(() => {
            if (target) target.style.display = "none";
        }, 500); // Match CSS transition
        return;
    }

    // Otherwise, handle switching/opening

    // 1. Mark as expanded
    expandWrapper.classList.add("expanded");

    // 2. Clear old state
    Object.values(stages).forEach(s => {
        if (s) s.style.display = "none";
    });
    Object.values(tabs).forEach(t => {
        if (t) t.classList.remove("active");
    });

    // 3. Show target stage
    if (target && tab) {
        target.style.display = "block";
        tab.classList.add("active");

        // Focus first input in stage after expansion starts
        const firstInput = target.querySelector('input');
        if (firstInput) setTimeout(() => firstInput.focus(), 300);
    }

    // Reset errors
    if (joinError) joinError.style.display = "none";
}

// Auto-format room code input
const joinCodeEl = document.getElementById('join-code');
if (joinCodeEl) {
    joinCodeEl.addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    });
}

// --- Create / Join Logic ---

async function submitCreateGroup() {
    const nameInput = document.getElementById("create-name").value.trim();
    const groupName = document.getElementById("create-group-name").value.trim();
    const btn = document.getElementById("btn-submit-create");

    if (!nameInput || !groupName) {
        showSidebarError("All fields are required.");
        return;
    }

    btn.disabled = true;
    btn.querySelector('span').textContent = "Creating...";

    try {
        const res = await fetch("/group/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ group_name: groupName })
        });

        if (!res.ok) throw new Error("Failed to create room.");

        const data = await res.json();
        const roomCode = data.room_code;

        // "Stylish Reveal" Success State
        btn.querySelector('span').textContent = "Success!";
        btn.style.background = "linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)";

        setTimeout(() => {
            enterGroupRoom(roomCode, nameInput, groupName);
            // Reset button style
            btn.disabled = false;
            btn.querySelector('span').textContent = "Create Room";
            btn.style.background = "";
        }, 800);

    } catch (error) {
        showSidebarError(error.message);
        btn.disabled = false;
        btn.querySelector('span').textContent = "Create Room";
    }
}

async function submitJoinGroup() {
    const nameInput = document.getElementById("join-name").value.trim();
    const codeInput = document.getElementById("join-code").value.trim().toUpperCase();
    const btn = document.getElementById("btn-submit-join");

    if (!nameInput || !codeInput) {
        showSidebarError("All fields are required.");
        return;
    }

    if (codeInput.length !== 6) {
        showSidebarError("Code must be 6 characters.");
        return;
    }

    btn.disabled = true;
    btn.querySelector('span').textContent = "Joining...";
    if (joinError) joinError.style.display = "none";

    try {
        const res = await fetch(`/group/validate/${codeInput}`);
        const data = await res.json();

        if (!res.ok) {
            showSidebarError(data.detail || "Room not found.");
            return;
        }

        if (data.valid) {
            btn.style.background = "linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)";
            setTimeout(() => {
                enterGroupRoom(data.room_code, nameInput, data.info.name);
                btn.disabled = false;
                btn.querySelector('span').textContent = "Join Room";
                btn.style.background = "";
            }, 600);
        } else if (data.full) {
            showSidebarError("Room is full.");
        } else {
            showSidebarError("Invalid code.");
        }
    } catch (error) {
        showSidebarError("Connection error.");
    } finally {
        btn.disabled = false;
        btn.querySelector('span').textContent = "Join Room";
    }
}

function showSidebarError(msg) {
    if (joinError) {
        joinError.textContent = msg;
        joinError.style.display = "block";
    }

    // Shake animation on the active stage container
    const activeStage = document.querySelector('.community-stage-inline[style*="display: block"]') || document.querySelector('.community-stage-inline:not([style*="display: none"])');
    if (activeStage) {
        activeStage.classList.remove('shake');
        void activeStage.offsetWidth; // trigger reflow
        activeStage.classList.add('shake');
    }
}


// --- Room Transition ---

function enterGroupRoom(roomCode, userName, roomTitle) {
    // Disconnect existing if any
    if (groupSocket) {
        groupSocket.close();
    }

    currentRoomCode = roomCode;
    currentUserName = userName;

    // Update UI
    mainArea.style.display = "none";
    groupArea.style.display = "flex";

    // Set Text
    activeRoomCodeDisplay.textContent = roomCode;
    bigRoomCodeDisplay.textContent = roomCode;
    groupChatTitle.textContent = roomTitle;
    groupChatSubtitle.innerHTML = `Participants: <span id="participant-count">0</span> / 13`;

    // Clear old UI
    groupMessageList.innerHTML = "";
    groupWelcomeScreen.style.display = "flex";

    // Establish WebSocket
    connectWebSocket(roomCode, userName);
}

function exitGroup() {
    if (groupSocket) {
        groupSocket.close();
        groupSocket = null;
    }
    currentRoomCode = null;

    groupArea.style.display = "none";
    mainArea.style.display = "flex";
}

async function copyRoomCode() {
    if (!currentRoomCode) return;
    try {
        await navigator.clipboard.writeText(currentRoomCode);
        const originalText = activeRoomCodeDisplay.textContent;
        activeRoomCodeDisplay.textContent = "COPIED!";
        setTimeout(() => {
            activeRoomCodeDisplay.textContent = currentRoomCode;
        }, 1500);
    } catch (err) {
        console.error("Failed to copy:", err);
    }
}


// --- WebSocket Logic ---

function connectWebSocket(roomCode, userName) {
    // Determine ws protocol based on http protocol
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/group/${roomCode}?name=${encodeURIComponent(userName)}`;

    groupSocket = new WebSocket(wsUrl);

    groupSocket.onopen = function (event) {
        console.log("Connected to group:", roomCode);
    };

    groupSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === "system") {
            updateParticipantCount(data.participants, data.max);
            appendSystemMessage(data.message);
        } else {
            appendGroupMessage(data.name, data.message);
        }
    };

    groupSocket.onclose = function (event) {
        console.log("Disconnected from group:", roomCode);
        if (event.code === 1008) {
            alert("Connection denied: " + event.reason);
            exitGroup();
        }
    };

    groupSocket.onerror = function (error) {
        console.error("WebSocket Error: ", error);
    };
}

function updateParticipantCount(current, max) {
    const pCount = document.getElementById("participant-count");
    if (pCount) {
        pCount.textContent = current;
    }
    groupChatSubtitle.innerHTML = `Participants: <span id="participant-count" class="badge-count">${current}</span> / ${max}`;
}

function sendGroupMessage() {
    const text = groupInput.value.trim();
    if (!text || !groupSocket || groupSocket.readyState !== WebSocket.OPEN) return;

    const payload = { message: text };
    groupSocket.send(JSON.stringify(payload));

    groupInput.value = "";
    groupInput.style.height = "auto";
    groupInput.focus();
}

function handleGroupKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendGroupMessage();
    }
}


// --- Rendering Chat ---

function appendSystemMessage(message) {
    // Hide welcome screen if it's the first message
    if (groupWelcomeScreen.style.display !== "none") {
        groupWelcomeScreen.style.display = "none";
    }

    const msgDiv = document.createElement("div");
    msgDiv.className = "message message--system";

    msgDiv.innerHTML = `
        <div class="system-bubble">${message}</div>
    `;

    groupMessageList.appendChild(msgDiv);
    scrollToBottom();
}

function appendGroupMessage(senderName, text) {
    // Hide welcome screen if it's the first message
    if (groupWelcomeScreen.style.display !== "none") {
        groupWelcomeScreen.style.display = "none";
    }

    const isSelf = senderName === currentUserName;

    const msgDiv = document.createElement("div");
    // Distinguish styling depending on if sent by us or another user
    msgDiv.className = `message ${isSelf ? "message--user" : "message--other"}`;

    // Create avatar from first letter (or ? if empty)
    const initial = senderName ? senderName.charAt(0).toUpperCase() : "?";

    // Format text securely (escape HTML, convert line breaks)
    const escapedText = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    const formattedText = `<div class="message__text"><p>${escapedText.replace(/\n/g, "<br>")}</p></div>`;

    let avatarHtml = `<div class="message__avatar">${initial}</div>`;
    let contentHtml = `<div class="message__name" style="text-align: ${isSelf ? "right" : "left"}">${isSelf ? "You" : senderName}</div>
                       <div class="message__bubble">${formattedText}</div>`;

    msgDiv.innerHTML = `
        ${avatarHtml}
        <div class="message__content">
            ${contentHtml}
        </div>
    `;

    groupMessageList.appendChild(msgDiv);
    scrollToBottom();
}

function scrollToBottom() {
    const windowDiv = document.getElementById("group-messages-window");
    requestAnimationFrame(() => {
        windowDiv.scrollTo({
            top: windowDiv.scrollHeight,
            behavior: "smooth"
        });
    });
}
