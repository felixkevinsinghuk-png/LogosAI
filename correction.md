# LogosAI — Interactive CSI Order of Service (Clickable Sections)

## Objective

Build a fully interactive **Order of Service module** where:

- Each service element is shown as a **clickable section**
- On click → it expands and displays its **full content**
- Works for:
  - English services
  - Tamil services
  - Special services (e.g., Wedding)

The system must be structured, reusable, and faithful to CSI traditions.

---

## 1. CORE FUNCTIONALITY (CRITICAL)

Each service item should behave like:

### Default View:
- Show only the section title

Example:
- Apostles’ Creed
- Confession
- Psalm Reading
- Gospel Reading

---

### On Click:
Expand and display FULL content

Example:

User clicks → "Apostles’ Creed"

System shows:

"I believe in God, the Father Almighty,
Maker of heaven and earth..."

---

## 2. APPLY THIS TO ALL SECTIONS

The following must be clickable and expandable:

- Invocation
- Opening Prayer
- Confession
- Absolution
- Apostles’ Creed
- Lord’s Prayer
- Scripture Readings (OT, Psalm, Epistle, Gospel)
- Sermon
- Offering Prayer
- Intercession
- Benediction

---

## 3. CONTENT SOURCE REQUIREMENTS

### English Service (Primary References)

Use structure and wording based on:

- CSI English Order of Service (Reference 1)
- CSI English Order of Service (Reference 2)

IMPORTANT:
- Do NOT hardcode random text
- Maintain authenticity of CSI liturgy
- Structure must match real church flow

---

### Tamil Service (CRITICAL)

Use Tamil content from:

- Goldwyn Sudhakar website → "ஆராதனை முறைகள்"

Requirement:
- Include proper Tamil liturgical text
- Maintain correct script (no translation errors)

---

### Wedding Service (SPECIAL CASE)

Use:

- CSI Wedding Order (Tamil)

Include sections like:
- Marriage declaration
- Vows
- Ring exchange
- Blessing

---

## 4. DATA STRUCTURE (IMPORTANT)

Store service as structured JSON:

Example:

{
  "section": "Apostles Creed",
  "language": "EN",
  "content": "Full text here...",
  "type": "static"
}

For scripture-based sections:

{
  "section": "Gospel Reading",
  "reference": "John 3:16",
  "text_en": "...",
  "text_ta": "...",
  "type": "scripture"
}

---

## 5. UI / UX BEHAVIOR

### Accordion Style (Recommended):

- Only one section open at a time (optional)
- Smooth expand/collapse animation

### Visual Design:

- Section title → bold
- Expand icon (arrow or +)
- Open state → highlighted background

---

## 6. LANGUAGE SUPPORT

Allow user to switch:

- English
- Tamil
- Bilingual

### Bilingual Mode:
- Show both English + Tamil content together

---

## 7. SCRIPTURE INTEGRATION

For reading sections:

- Automatically fetch verses from Bible dataset
- Display:
  - Reference
  - Full verse text
  - Language toggle support

---

## 8. REUSABILITY

System must support:

- Sunday Service
- Special Service (Wedding, Funeral, etc.)
- Custom Service Plan (user-created)

---

## 9. SEARCH / QUICK NAVIGATION (OPTIONAL)

- Allow user to jump to section
- Example:
  - Search "Creed"
  - Scroll to Apostles’ Creed

---

## 10. VALIDATION RULES

Ensure:

- No missing sections
- Proper order maintained
- Content matches CSI tradition
- Tamil text properly rendered

---

## 11. EXPECTED RESULT

The system should:

- Display full Order of Service
- Allow users to click any section
- Instantly show full liturgical content
- Support English + Tamil
- Include wedding service structure
- Maintain real CSI format and authenticity



# 🚨 Static File 404 Error — Fix, Cleanup & Optimization Guide

## Problem Summary

Your server logs show multiple **404 (File Not Found) errors**:

```bash
GET /static/app_v2.js → 404
GET /static/style.css → 404
GET /static/supabase-client.js → 404
GET /static/group.js → 404
GET /static/bible-engine.js → 404
GET /static/liturgy-data.js → 404
GET /favicon.ico → 404
```

### What This Means (Fact)

* The browser is requesting files that are not being found
* Either the files are missing, misnamed, or not being served correctly
* Because of this, your frontend logic is **not loading at all**, which breaks the entire app

---

## 🎯 Objective

Fix all errors and ensure:

* All static files load correctly
* No 404 errors remain
* All features work end-to-end
* Unused and duplicate code is removed
* Application becomes stable and production-ready (MVP level)

---

## ✅ STEP 1: Fix File Path Issues

Open your HTML file and verify all file references:

```html
<link rel="stylesheet" href="/static/style.css">

<script src="/static/supabase-client.js"></script>
<script src="/static/app_v2.js"></script>
<script src="/static/group.js"></script>
<script src="/static/bible-engine.js"></script>
<script src="/static/liturgy-data.js"></script>
```

### Rules:

* Paths must exactly match filenames (case-sensitive)
* Use `/static/...` consistently
* Ensure no typos or outdated filenames

---

## ✅ STEP 2: Confirm Files Are Actually Available

Manually verify that each referenced file exists.

If any file is missing:

* Restore it
* Or remove its reference from HTML if unused

---

## ✅ STEP 3: Run Server Correctly

If using a simple Python server:

```bash
python3 -m http.server 3000
```

### Important (Fact):

* Files are served only from the current working directory
* If launched from the wrong place, files will not be found

---

## ✅ STEP 4: Fix Static File Serving (FastAPI)

If using FastAPI, ensure static files are properly mounted:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

---

## ✅ STEP 5: Fix Loading Issues (CRITICAL)

If UI shows "Loading..." forever:

Use proper async handling:

```javascript
setLoading(true);

try {
  const res = await fetch("/api/songs");
  const data = await res.json();

  setSongs(data.data || []);
} catch (err) {
  console.error(err);
} finally {
  setLoading(false);
}
```

### Key Rule:

* `setLoading(false)` must always run (use `finally`)

---

## ✅ STEP 6: Handle Empty Data Properly

Instead of showing "Loading..." forever:

```javascript
if (!loading && songs.length === 0) {
  showMessage("No songs available");
}
```

---

## 🧹 STEP 7: Remove Unwanted Files

Identify and remove:

* Duplicate files (e.g., multiple versions like `app_old.js`, `app_v2.js`)
* Unused scripts not referenced anywhere
* Dead code and test files
* Unused CSS files

### Rule:

If a file is not:

* Imported
* Used
* Needed

→ Remove it

---

## ⚙️ STEP 8: Optimize Code

### Improvements:

* Merge repeated logic into reusable functions
* Remove unnecessary API calls
* Avoid duplicate fetch requests
* Use consistent naming

---

## 🔐 STEP 9: Fix Backend Connectivity

Verify:

* Backend is running
* API URLs are correct
* No CORS issues

If using FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 STEP 10: Debug Using Browser Tools

Open DevTools:

### Network Tab:

* Check if files return 200 or 404

### Console Tab:

* Look for:

  * JS errors
  * fetch failures
  * undefined variables

---

## ⚠️ STEP 11: Fix favicon Error (Optional)

Add this to HTML to prevent error:

```html
<link rel="icon" href="data:,">
```

---

## 🚀 FINAL RESULT

After fixing everything:

* No 404 errors
* All scripts load successfully
* UI renders correctly
* Features work properly
* No infinite loading states
* Clean and optimized code

---

## ❌ Common Mistakes to Avoid

* Wrong file names (case-sensitive)
* Incorrect script paths
* Missing files
* Running server incorrectly
* Forgetting to handle loading states

---

## ✅ Definition of Done

Application is considered fixed only when:

* All static files load without errors
* No console errors exist
* All features are functional
* No placeholder or fake logic remains
* Codebase is clean and optimized

---

## 🧠 Conclusion

This issue is caused by:

* Missing or incorrectly referenced files
* Improper serving of static assets

Once corrected, the entire system will function normally.
