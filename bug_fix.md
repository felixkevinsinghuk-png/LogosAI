# 🛠 RhemaLight AI — Debug, Validate & Fix Guide (All Features)

## Objective

Review ALL features and ensure:

* Every function is working (no placeholders)
* Backend is properly connected
* Data is loading correctly
* No infinite loading states
* No silent failures

---

## GLOBAL CHECKS (APPLY TO ALL FEATURES)

Before checking individual modules, verify:

### ✅ Backend Health

* Check `/api/health` → must return success
* Backend must not crash during requests

---

### ✅ API Calls

For every feature:

* Open DevTools → Network tab
* Confirm API requests are actually sent
* Check response status (200, 401, 500)

---

### ✅ Response Format

All APIs must return:

```json id="a1check"
{
  "success": true,
  "data": {},
  "error": null
}
```

---

### ✅ Loading State Rule

Every async function MUST:

```javascript id="a2check"
try {
  // fetch
} catch (e) {
  console.error(e);
} finally {
  setLoading(false);
}
```

---

## FEATURE-BY-FEATURE DEBUG CHECKS

---

## 1. 🤖 Ask AI (Chat)

### 🔍 Check:

* Is `POST /chat` triggered?
* Is FAISS returning results?
* Is model crashing (memory issue)?

### ⚠️ Common Issues:

* Model out-of-memory (Mac M3 Metal error)
* No passages retrieved
* Response not rendered

### ✅ Fix:

* Limit context passages (max 3–5)
* Reduce token length
* Log response before sending to UI

---

## 2. 📖 Read Bible

### 🔍 Check:

* `GET /api/bible/passage` returns data?
* `chapter-count` API works?

### ⚠️ Issues:

* Wrong book/chapter params
* JSON file not loaded

### ✅ Fix:

* Validate query params
* Log returned verses before rendering

---

## 3. 📅 Reading Plans

### 🔍 Check:

* Is `/api/plans` called ONLY after user click?
* Are plans returned from DB?

### ⚠️ Issues:

* Showing "Loading..." without action
* Empty DB
* Static data used

### ✅ Fix:

* Implement lazy loading
* Add empty state:
  "No plans available"

---

## 4. ❤️ Streak System

### 🔍 Check:

* `POST /api/streak` triggered on activity?
* `GET /api/streak` returns correct value?

### ⚠️ Issues:

* Not incrementing
* Incrementing multiple times per day

### ✅ Fix:

* Enforce:

  * once per day increment
  * reset on missed day

---

## 5. 📚 Library

### 🔍 Check:

* Are saved items fetched from DB?
* Is `GET /api/history` working?

### ⚠️ Issues:

* Data saved but not displayed
* Wrong user filtering

### ✅ Fix:

* Filter by logged-in user ID
* Validate DB query

---

## 6. 🔍 Study Guides

### 🔍 Check:

* Does clicking guide load content?
* Do references open Bible reader?

### ⚠️ Issues:

* Static UI only
* Links not working

### ✅ Fix:

* Bind click events properly
* Connect to Bible API

---

## 7. ✏️ Sermon Builder

### 🔍 Check:

* Is `POST /api/sermon` called?
* Is response structured?

### ⚠️ Issues:

* Fake setTimeout used
* No real AI call

### ✅ Fix:

* Replace mock logic with real API call
* Validate JSON output

---

## 8. 🗓️ Service Orders

### 🔍 Check:

* `GET /api/service` returns correct data?
* Accordion expands?

### ⚠️ Issues:

* Sections not clickable
* Data not loaded

### ✅ Fix:

* Ensure event listeners attached
* Validate JSON structure

---

## 9. 🎵 Worship Hub

### 🔍 Check:

* `GET /api/songs` returns data?
* UI updates after fetch?

### ⚠️ Issues:

* "Loading songs..." forever
* No DB data
* Wrong response parsing

### ✅ Fix:

* Add empty state
* Ensure `setLoading(false)` runs
* Validate Supabase table

---

## 10. 👥 Community Chat

### 🔍 Check:

* WebSocket connects?
* Messages broadcast?

### ⚠️ Issues:

* Connection fails
* Messages not received

### ✅ Fix:

* Verify endpoint:
  `ws://localhost:8000/ws/{room}/{name}`
* Check server logs

---

## 11. 🔔 Notifications

### 🔍 Check:

* `GET /api/notifications` works?

### ⚠️ Issues:

* Modal opens but no data
* Badge not updating

### ✅ Fix:

* Ensure DB has records
* Update unread count logic

---

## 12. 👤 Auth & Profile

### 🔍 Check:

* JWT sent in headers?
* Profile API works?

### ⚠️ Issues:

* Unauthorized errors
* Token missing

### ✅ Fix:

```javascript id="authcheck"
Authorization: `Bearer ${token}`
```

---

## 🔥 CRITICAL SYSTEM CHECK

### Verify Full Flow:

```id="flowcheck"
Frontend → API → Backend → Supabase → Backend → Frontend
```

If any step fails → feature breaks

---

## 🧪 FINAL TEST CHECKLIST

* No 404 errors
* No console errors
* No infinite loading
* All buttons functional
* All APIs return data
* No static/mock data

---

## ❌ MUST REMOVE

* setTimeout fake responses
* hardcoded arrays
* placeholder UI
* duplicate files

---

## ✅ FINAL RESULT

Application should be:

* Fully dynamic
* Backend-driven
* Bug-free
* Clean and optimized
* MVP production-ready

---

## 🧠 Conclusion

If any feature is not working:

It is ALWAYS due to one of:

* API not called
* Backend not responding
* DB empty
* Loading state not handled
* Auth missing

Fix these → entire system becomes stable
