# 🚀 LogosAI - cPanel Deployment Guide

This document explains how to deploy the refactored **LogosAI** platform to a cPanel shared hosting environment (e.g., `/public_html`).

## 1. Prerequisites
- **Supabase Account**: Ensure your Supabase project is active.
- **cPanel Access**: Credentials for your hosting provider.

## 2. Prepare the Files
I have restructured the project for a "Static Frontend" deployment. You only need to upload the contents of the `frontend/` directory.

### ✅ Do NOT Upload
- `backend/` folder
- `data/` or `database/` folders
- `.env` files (Supabase keys are now in `static/supabase-client.js`)
- `requirements.txt` or `main.py`

### ✅ Mandatory Files
- `index.html` (The main entry point)
- `.htaccess` (Handles routing)
- `static/` (All assets, styles, and logic)
  - `bible/` (Bible JSON data)
  - `app.js`
  - `bible-engine.js`
  - `liturgy-data.js`
  - `supabase-client.js`
  - `style.css`

## 3. Upload Steps
1. Log in to cPanel and open **File Manager**.
2. Navigate to `/public_html`.
3. Upload the `index.html` and `.htaccess` to the root of `/public_html`.
4. Create a folder named `static` inside `/public_html`.
5. Upload all content from the local `frontend/static/` folder into the remote `/static/` folder.
   - *Tip: ZIP the local `static` folder first, upload the ZIP, and then extract it in File Manager to save time.*

## 4. Supabase Configuration (Already Done)
The application is configured to connect directly to your Supabase instance using the JS SDK.
- **Client implementation**: `static/supabase-client.js`
- **Tables used**: `users`, `prayer_logs`, `sermons`, `verse_likes`, `songs`, `playlists`, `playlist_songs`, `reading_progress`, `accountability_users`.

## 5. Troubleshooting
- **404 on Refresh**: Ensure the `.htaccess` file was uploaded correctly to the root directory.
- **Bible Not Loading**: Check that the `static/bible/` folder contains the `.json` files (e.g., `en_kjv.json`).
- **Styles Missing**: Ensure `static/style.css` exists.

---
**LogosAI: Refactored for Speed and Portability.**
