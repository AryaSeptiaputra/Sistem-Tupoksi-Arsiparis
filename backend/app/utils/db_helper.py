from sqlalchemy.engine import make_url

def parse_db_url(url_string):
    """Parses a SQLAlchemy connection string into a dictionary.

    Args:
        url_string (str): The full DSN (e.g., mysql://user:pass@localhost/db).

    Returns:
        dict: A dictionary containing 'user', 'password', 'host', 'port', and 'name'.
    """
    url = make_url(url_string)
    return {
        'user': url.username,
        'password': url.password,
        'host': url.host,
        'port': url.port or 3306,
        'name': url.database
    }