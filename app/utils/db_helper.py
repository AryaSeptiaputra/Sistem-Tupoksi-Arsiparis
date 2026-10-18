from typing import Any

from sqlalchemy.engine import make_url

def parse_db_url(url_string: str) -> dict[str, Any]:
    """Memecah URL koneksi SQLAlchemy menjadi bagian-bagiannya.

    Args:
        url_string: URL lengkap, misalnya `mysql+pymysql://user:pass@localhost/db`.

    Returns:
        Dict berisi `user`, `password`, `host`, `port` (default 3306), dan `name`.
    """
    url = make_url(url_string)
    return {
        'user': url.username,
        'password': url.password,
        'host': url.host,
        'port': url.port or 3306,
        'name': url.database
    }
