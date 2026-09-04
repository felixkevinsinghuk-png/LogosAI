# 🚀 cPanel Deployment Guide for LogosAI

This guide provides the steps to deploy the refactored **LogosAI** platform to your cPanel `/public_html` directory.

## 1. Prepare Your Files
The project has been refactored to be **completely static**. You only need the following files and folders:

*   `index.html` (Primary entry point)
*   `static/` (Contains all JS, CSS, and Bible JSON data)
*   `.htaccess` (Ensures smooth navigation/SPA routing)

> [!IMPORTANT]
> You **do NOT** need the `backend/` folder, `data/` folder, or any `.py`, `.env`, or `.sh` files for the production site.

## 2. Uploading to cPanel
1.  **Compress**: Select `index.html`, `static/`, and `.htaccess` and create a ZIP file (e.g., `logosai_deploy.zip`).
2.  **Upload**: Go to cPanel → **File Manager** → `/public_html`.
3.  **Extract**: Upload the ZIP and extract it directly into `/public_html`.
4.  **Verify**: Your directory structure should look like this:
    ```text
    /public_html
    ├── index.html
    ├── .htaccess
    └── static/
        ├── app.js
        ├── bible-engine.js
        ├── bible/
        │   ├── en_kjv.json
        │   ├── en_esv.json
        │   └── ta_bsi.json
        └── (other JS/CSS files)
    ```

## 3. Fix "Permission Denied" (Supabase RLS)
The browser debugging confirmed that your data (Songs, Playlists, Reading Plans) is currently blocked by Supabase **Row Level Security (RLS)**.

1.  Go to your **Supabase Dashboard**.
2.  Open the **SQL Editor**.
3.  Copy and run the contents of [**SUPABASE_RLS_FIX.sql**](file:///Volumes/FELIX%20SSD/LogosAI/frontend/SUPABASE_RLS_FIX.sql).

This will grant the necessary permissions for:
*   `songs` & `playlists`
*   `users` (Profile management)
*   `reading_progress` & `accountability_users` (Streak tracking)

## 4. Troubleshooting
*   **Bible Not Loading**: Ensure the `static/bible/` folder exists and contains the `.json` files.
*   **404 Errors on Refresh**: If you refresh a page and get a 404, check that your `.htaccess` file was uploaded correctly.
*   **Google Sign-In**: Ensure your site URL (e.g., `https://yourdomain.com`) is added to the **Authorized Redirect URIs** in both Google Cloud Console and Supabase Auth settings.
