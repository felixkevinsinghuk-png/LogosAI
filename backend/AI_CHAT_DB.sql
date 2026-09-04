-- Create the chat_logs table
CREATE TABLE IF NOT EXISTS public.chat_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.chat_logs ENABLE ROW LEVEL SECURITY;

-- Create policy so users can only see and insert their own chat history
CREATE POLICY "Users can insert their own chat logs" 
    ON public.chat_logs FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own chat logs" 
    ON public.chat_logs FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chat logs" 
    ON public.chat_logs FOR DELETE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own chat logs" 
    ON public.chat_logs FOR UPDATE 
    USING (auth.uid() = user_id);

-- GRANT permissions to the API roles so the frontend can access the table
GRANT ALL ON TABLE public.chat_logs TO anon, authenticated, service_role;
