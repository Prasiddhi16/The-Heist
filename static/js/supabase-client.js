// supabase-client.js

// Check if the supabase global object is available
if (window.supabase) {
    const { createClient } = window.supabase;
    
    // Initialize the client
    window.supabaseClient = createClient(
        window.SUPABASE_URL, 
        window.SUPABASE_ANON_KEY
    );
    console.log("Supabase client initialized successfully.");
} else {
    console.error("Supabase library failed to load.");
}