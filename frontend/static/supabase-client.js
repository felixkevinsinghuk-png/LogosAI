// supabase-client.js
// Initializes the Supabase client, preventing the auth token "Stolen Lock" race condition.

const SUPABASE_URL = 'https://kszsjsqexdxhjchtvoho.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzenNqc3FleGR4aGpjaHR2b2hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQzMDcwOTcsImV4cCI6MjA4OTg4MzA5N30.Q7LkNLdi8xkVeJb99fvU-yGVNi0otbdOByZgTlGuD0Q';

let sbClient = null;

try {
  sbClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
      // FIX: Use a unique storageKey to prevent cross-tab BroadcastChannel lock conflicts.
      // The default key is shared across all tabs, causing "lock stolen" errors when
      // multiple tabs or multiple concurrent auth calls fight for the same token.
      storageKey: 'rhemalight-sb-session',
      storage: window.localStorage,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      // FIX: Disable the BroadcastChannel lock by using a no-op lock function.
      // This prevents the "Lock was released because another request stole it" error
      // which occurs when multiple Supabase calls compete for the auth token simultaneously.
      lock: async (name, acquireTimeout, fn) => fn(),
    }
  });
  console.log('[Supabase] Client initialized (lock contention disabled).');
} catch (error) {
  console.error('[Supabase] Failed to initialize client.', error);
}

window.supabaseClient = sbClient;
