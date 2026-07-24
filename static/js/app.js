
(function () {
  "use strict";

  function waitForSupabase(timeoutMs = 5000) {
    return new Promise((resolve, reject) => {
      if (window.supabaseClient) return resolve(window.supabaseClient);
      const start = Date.now();
      const interval = setInterval(() => {
        if (window.supabaseClient) {
          clearInterval(interval);
          resolve(window.supabaseClient);
        } else if (Date.now() - start > timeoutMs) {
          clearInterval(interval);
          reject(new Error("supabaseClient not available after timeout"));
        }
      }, 50);
    });
  }

  function formatRank(rank) {
    const r = rank || "Rookie";
    return r.charAt(0).toUpperCase() + r.slice(1);
  }

  function getLastName(fullName, username) {
    if (fullName) {
      const parts = fullName.trim().split(/\s+/);
      if (parts.length) return parts[parts.length - 1];
    }
    if (username) {
      const parts = username.split(/[_-]/);
      if (parts.length) return parts[parts.length - 1];
    }
    return "";
  }

  function setText(selector, text) {
    document.querySelectorAll(selector).forEach((el) => {
      el.textContent = text;
    });
  }

  function setHTML(selector, html) {
    document.querySelectorAll(selector).forEach((el) => {
      el.innerHTML = html;
    });
  }

  async function loadProfile() {
    const cachedName = localStorage.getItem("loggedInUser");
    if (cachedName) {
      setText(".js-username", cachedName);
      setText(".js-avatar", cachedName.substring(0, 2).toUpperCase());
      setText("#dash-name", cachedName);
    }

    let supabase;
    try {
      supabase = await waitForSupabase();
    } catch (e) {
      console.error("Supabase client never became available:", e);
      return;
    }

    try {
      const { data: { user }, error: authErr } = await supabase.auth.getUser();
      if (authErr) {
        console.error("auth.getUser error:", authErr);
        return;
      }
      if (!user) return;

      // maybeSingle() instead of single() -- single() throws a 406 if the
      // 'users' row is missing or if more than one row matches the filter.
      const { data: profile, error: profErr } = await supabase
        .from("users")
        .select("username, full_name, rank, score, cases_solved")
        .eq("user_id", user.id)
        .maybeSingle();

      if (profErr) {
        console.error("users profile query error:", profErr);
        return;
      }
      if (!profile) {
        console.warn(
          "No matching row in 'users' for this auth user. Check that a row exists with user_id =",
          user.id,
          "and that your RLS SELECT policy allows it (auth.uid() = user_id)."
        );
        return;
      }

      const formattedRank = formatRank(profile.rank);
      const lastName = getLastName(profile.full_name, profile.username);
      const displayName = profile.username || cachedName || "Detective";

      // Sidebar + header (shared classes, updates both at once)
      setText(".js-username", displayName);
      setText(".js-avatar", displayName.substring(0, 2).toUpperCase());
      setHTML(".js-rank", `<i class="fa-solid fa-star"></i> ${formattedRank}`);
      setText(".js-rank-plain", `${formattedRank} Detective`);

      // Dashboard welcome line -> "{{rank}} {{lastname}}"
      setText("#dash-name", `${formattedRank} ${lastName || "Detective"}`);
      setText("#stat-solved", profile.cases_solved || 0);
      setText("#stat-score", profile.score || 0);
      setText("#stat-rank", formattedRank);

      window.HeistApp = window.HeistApp || {};
      window.HeistApp.profile = profile;
    } catch (err) {
      console.error("Profile sync failed:", err);
    }
  }

  async function loadActiveCasesCount() {
    let supabase;
    try {
      supabase = await waitForSupabase();
    } catch (e) {
      return;
    }

    try {
      const { count, error } = await supabase
        .from("cases")
        .select("*", { count: "exact", head: true })
        .eq("status", "Active");

      if (error) {
        console.error("active cases count error:", error);
        return;
      }

      setText(".js-active-count", count ?? 0);
      window.HeistApp = window.HeistApp || {};
      window.HeistApp.activeCasesCount = count ?? 0;
    } catch (err) {
      console.error("Active case count sync failed:", err);
    }
  }

  window.handleLogout = async function handleLogout() {
    if (window.supabaseClient) {
      try {
        await window.supabaseClient.auth.signOut();
      } catch (err) {
        console.error("Signout error:", err);
      }
    }
    try {
      localStorage.removeItem("loggedInUser");
    } catch (e) {
      console.warn("Storage access denied by browser, skipping local storage clear.");
    }
    window.location.href = window.HEIST_LOGIN_URL || "/login/";
  };

  document.addEventListener("DOMContentLoaded", () => {
    loadProfile();
    loadActiveCasesCount();
  });
})();