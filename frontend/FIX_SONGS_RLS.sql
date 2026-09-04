-- 🚀 LogosAI - Worship Songs (songs table) RLS Fix
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql)

-- 1. Ensure RLS is enabled on the songs table
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;

-- 2. Drop any existing conflicting policies for write operations on songs
DROP POLICY IF EXISTS "User Manage Songs" ON songs;
DROP POLICY IF EXISTS "Users can insert songs" ON songs;
DROP POLICY IF EXISTS "Users can update songs" ON songs;
DROP POLICY IF EXISTS "Users can delete songs" ON songs;

-- 3. Create Private Policies (User-specific data management)
-- Allow users to insert new songs (user_id must match their auth uid)
CREATE POLICY "User Insert Songs" ON songs FOR INSERT TO authenticated 
    WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own songs
CREATE POLICY "User Update Songs" ON songs FOR UPDATE TO authenticated 
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own songs
CREATE POLICY "User Delete Songs" ON songs FOR DELETE TO authenticated 
    USING (auth.uid() = user_id);

-- 4. Note: The Public Read policy should already exist from the previous script.
-- If not, you can safely run it again:
DROP POLICY IF EXISTS "Public Read Songs" ON songs;
CREATE POLICY "Public Read Songs" ON songs FOR SELECT TO authenticated, anon USING (true);

