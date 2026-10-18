from flask_jwt_extended import get_jwt

def get_current_user_id() -> int | None:
    """
    Mengambil id akun dari claim `id` di JWT request yang sedang berjalan.

    Claim `id` sudah ada sejak sebelum perubahan satu pengguna, jadi token
    lama yang belum kedaluwarsa tetap terbaca dengan benar.

    Returns:
        int | None: Id akun, atau None bila claim tidak ada.
    """
    user_id = get_jwt().get("id")
    return int(user_id) if user_id is not None else None
