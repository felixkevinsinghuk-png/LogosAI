-- Update reading_progress to track individual days
DROP TABLE IF EXISTS public.reading_progress;

CREATE TABLE public.reading_progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  plan_id TEXT NOT NULL,
  day_number INTEGER NOT NULL,
  completed BOOLEAN DEFAULT false,
  completed_at TIMESTAMPTZ,
  UNIQUE(user_id, plan_id, day_number)
);

-- Realtime for progress updates
alter publication supabase_realtime add table public.reading_progress;

-- RLS
ALTER TABLE public.reading_progress ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can manage own progress" ON public.reading_progress;
CREATE POLICY "Users can manage own progress" ON public.reading_progress FOR ALL USING (auth.uid() = user_id);

-- Permissions for service role (backend)
GRANT ALL ON public.reading_progress TO service_role;
GRANT ALL ON public.reading_progress TO anon;
GRANT ALL ON public.reading_progress TO authenticated;
