-- 🚀 LogosAI - Comprehensive Supabase RLS & Permissions Fix (V3)
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql)

-- 1. Ensure Schema Permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- 2. Enable Row Level Security (RLS) on all core tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE playlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE playlist_songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE accountability_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE verse_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE prayer_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 3. Drop existing problematic policies (to prevent duplicates/conflicts)
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname, tablename FROM pg_policies WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON "' || r.tablename || '"';
    END LOOP;
END $$;

-- 4. Create Public/Shared Policies (Available to all logged-in users)
CREATE POLICY "Public Read Songs" ON songs FOR SELECT TO authenticated, anon USING (true);
CREATE POLICY "User Manage Own Songs" ON songs FOR ALL TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Public Read Users" ON users FOR SELECT TO authenticated, anon USING (true);
CREATE POLICY "Public Read Groups" ON groups FOR SELECT TO authenticated USING (true);
CREATE POLICY "Public Read Group Members" ON group_members FOR SELECT TO authenticated USING (true);
CREATE POLICY "Public Read Messages" ON messages FOR SELECT TO authenticated USING (true);

-- 5. Create Private Policies (User-specific data)
-- User Profiles
CREATE POLICY "User Manage Profile" ON users FOR ALL TO authenticated 
    USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

-- Worship Hub
CREATE POLICY "User Manage Playlists" ON playlists FOR ALL TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "User Manage Playlist Songs" ON playlist_songs FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- Personal Progress & Accountability
CREATE POLICY "User Manage Streak" ON accountability_users FOR ALL TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "User Manage Progress" ON reading_progress FOR ALL TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "User Manage Likes" ON verse_likes FOR ALL TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "User Manage Prayers" ON prayer_logs FOR ALL TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Community (Groups & Messaging)
CREATE POLICY "User Create Groups" ON groups FOR INSERT TO authenticated WITH CHECK (auth.uid() = created_by);
CREATE POLICY "User Join Groups" ON group_members FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "User Send Messages" ON messages FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);

-- 6. Important: Specifically for 'users' table (Common pitfall)
-- Allow authenticated users to insert their own profile (happens on first login)
CREATE POLICY "Allow Insert Profile" ON users FOR INSERT TO authenticated WITH CHECK (auth.uid() = id);
