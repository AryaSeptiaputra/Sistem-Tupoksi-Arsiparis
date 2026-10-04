document.addEventListener("DOMContentLoaded", () => {
    const avatarEl = document.querySelector(".user-avatar, #dashboard-avatar");
    const nameEl = document.getElementById("profile-name");
    const roleEl = document.getElementById("profile-role");

    if (!avatarEl || typeof api === "undefined") return;

    const user = api.auth.getUserData();
    if (!user) return;

    const fullName =
        user.full_name ||
        (user.teacher && user.teacher.full_name) ||
        "Pengguna";

    const initial = fullName.charAt(0).toUpperCase();

    // Set avatar huruf
    avatarEl.textContent = initial;
    avatarEl.style.cursor = "pointer";

    // Klik avatar → profile
    avatarEl.addEventListener("click", () => {
        window.location.href = "/page/user_profile";
    });

    // Optional: set nama & role kalau elemennya ada
    if (nameEl) nameEl.textContent = fullName;
    if (roleEl && user.role) {
        roleEl.textContent =
            user.role.charAt(0).toUpperCase() + user.role.slice(1);
    }
});
