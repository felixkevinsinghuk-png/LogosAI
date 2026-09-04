-- ==============================================================================
-- LOGOSAI SUPABASE SCHEMA
-- Directions: Copy this entire file and paste it into the Supabase SQL Editor,
-- then click "Run" to automatically build your entire database and security rules.
-- ==============================================================================

-- 1. USERS Table (Public Extension of Supabase Auth)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  display_name TEXT,
  email TEXT NOT NULL,
  preferred_language TEXT DEFAULT 'en',
  theme TEXT DEFAULT 'light',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to automatically create a public user when someone signs up
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, display_name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();


-- 2. VERSE_LIKES Table
CREATE TABLE IF NOT EXISTS public.verse_likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  verse_reference TEXT NOT NULL,
  verse_text TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- 3. READING_PROGRESS Table
CREATE TABLE IF NOT EXISTS public.reading_progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  plan_id TEXT NOT NULL,
  current_day INTEGER NOT NULL DEFAULT 1,
  last_read_date DATE DEFAULT CURRENT_DATE,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, plan_id)
);


-- 4. PRAYER_LOGS Table
CREATE TABLE IF NOT EXISTS public.prayer_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- 5. SERMONS Table
CREATE TABLE IF NOT EXISTS public.sermons (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  topic TEXT NOT NULL,
  verse_context TEXT,
  generated_content JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- 6. SERVICE_PLANS Table (CSI)
CREATE TABLE IF NOT EXISTS public.service_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  content JSONB NOT NULL,
  language TEXT DEFAULT 'en',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. DAILY_VERSES Table
CREATE TABLE IF NOT EXISTS public.daily_verses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  verse_date DATE UNIQUE NOT NULL,
  language TEXT NOT NULL,
  verse_reference TEXT NOT NULL,
  verse_text TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. NOTIFICATIONS Table
CREATE TABLE IF NOT EXISTS public.notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type TEXT DEFAULT 'system',
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. ACCOUNTABILITY_USERS Table
CREATE TABLE IF NOT EXISTS public.accountability_users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  current_streak INTEGER DEFAULT 0,
  best_streak INTEGER DEFAULT 0,
  total_points INTEGER DEFAULT 0,
  last_active_date DATE DEFAULT CURRENT_DATE
);


-- 10. SONGS Table (Globally Readable)
CREATE TABLE IF NOT EXISTS public.songs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'custom',
  language TEXT DEFAULT 'en',
  lyrics TEXT,
  youtube_url TEXT,
  youtube_video_id TEXT,
  thumbnail_url TEXT,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE
);

-- 11. PLAYLISTS Table
CREATE TABLE IF NOT EXISTS public.playlists (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. PLAYLIST_SONGS Table
CREATE TABLE IF NOT EXISTS public.playlist_songs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  playlist_id UUID REFERENCES public.playlists(id) ON DELETE CASCADE NOT NULL,
  song_id UUID REFERENCES public.songs(id) ON DELETE CASCADE NOT NULL,
  UNIQUE(playlist_id, song_id)
);

-- Turn on Realtime for Notifications (instead of generic messages)
alter publication supabase_realtime add table public.notifications;

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.verse_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prayer_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sermons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.service_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_verses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.accountability_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.playlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.playlist_songs ENABLE ROW LEVEL SECURITY;

-- Policies (idempotent — drop first then recreate)
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Users can manage own likes" ON public.verse_likes;
DROP POLICY IF EXISTS "Users can manage own progress" ON public.reading_progress;
DROP POLICY IF EXISTS "Users can manage own prayer logs" ON public.prayer_logs;
DROP POLICY IF EXISTS "Users can manage own sermons" ON public.sermons;
DROP POLICY IF EXISTS "Users can manage own service plans" ON public.service_plans;
DROP POLICY IF EXISTS "Users can manage own accountability" ON public.accountability_users;
DROP POLICY IF EXISTS "Users can manage own playlists" ON public.playlists;
DROP POLICY IF EXISTS "Users can manage own notifications" ON public.notifications;
DROP POLICY IF EXISTS "Anyone can read daily verses" ON public.daily_verses;
DROP POLICY IF EXISTS "Anyone can read songs" ON public.songs;
DROP POLICY IF EXISTS "Users can add custom songs" ON public.songs;
DROP POLICY IF EXISTS "Users can update own songs" ON public.songs;
DROP POLICY IF EXISTS "Users can delete own songs" ON public.songs;
DROP POLICY IF EXISTS "Users can manage own playlist songs" ON public.playlist_songs;

CREATE POLICY "Users can view own profile" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can manage own likes" ON public.verse_likes FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own progress" ON public.reading_progress FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own prayer logs" ON public.prayer_logs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own sermons" ON public.sermons FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own service plans" ON public.service_plans FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own accountability" ON public.accountability_users FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own playlists" ON public.playlists FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own notifications" ON public.notifications FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Anyone can read daily verses" ON public.daily_verses FOR SELECT USING (true);
CREATE POLICY "Anyone can read songs" ON public.songs FOR SELECT USING (true);
CREATE POLICY "Users can add custom songs" ON public.songs FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can update own songs" ON public.songs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own songs" ON public.songs FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own playlist songs" ON public.playlist_songs FOR ALL USING (
  EXISTS (SELECT 1 FROM public.playlists p WHERE p.id = playlist_songs.playlist_id AND p.user_id = auth.uid())
);
