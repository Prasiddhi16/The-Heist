if (window.supabase) {
    const { createClient } = window.supabase;

    window.supabaseClient = createClient(
        window.SUPABASE_URL,
        window.SUPABASE_ANON_KEY
    );

    console.log("Supabase client initialized successfully.");

    window.getSupabaseUserId = async function () {
        const { data, error } = await window.supabaseClient.auth.getUser();

        if (error) {
            console.error("Supabase user error:", error);
            return null;
        }

        return data?.user?.id || null;
    };

    (async () => {
    const userId = await window.getSupabaseUserId();

    console.log("Supabase UID:", userId);

    if (!userId) return;

    const response = await fetch("/api/set-session-user/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "same-origin",
        body: JSON.stringify({
            user_id: userId
        })
    });

    const result = await response.json();

    console.log("Session response:", result);

    if (result.success) {
        window.location.reload();
    }
})();

} else {
    console.error("Supabase library failed to load.");
}