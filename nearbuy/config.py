import os, sys, shutil
from pathlib import Path

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_NAME = "NEARBUY"
IS_VERCEL = os.getenv("VERCEL", "").lower() == "1"
if IS_VERCEL:
    # Only temporary runtime files may be written by Vercel Functions. User data lives in PostgreSQL.
    DATA_DIR = Path("/tmp") / APP_NAME
elif getattr(sys, "frozen", False):
    DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / APP_NAME
else:
    DATA_DIR = Path(os.getenv("NEARBUY_DATA_DIR", Path(__file__).resolve().parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
# Preserve the original prototype database when moving to the new data location.
_new_db = DATA_DIR / "nearbuy.db"
_old_db = Path(__file__).resolve().parent / "nearbuy.db"
if not _new_db.exists() and _old_db.exists() and _old_db.resolve() != _new_db.resolve():
    shutil.copy2(_old_db, _new_db)

def _load_or_create_secret():
    path = DATA_DIR / ".secret_key"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    import secrets
    value = secrets.token_urlsafe(48)
    path.write_text(value, encoding="utf-8")
    try: path.chmod(0o600)
    except OSError: pass
    return value


def _database_uri():
    value = os.getenv("DATABASE_URL")
    if IS_VERCEL and not value:
        raise RuntimeError("DATABASE_URL is required on Vercel. Connect a persistent PostgreSQL database and add its URL in Project Environment Variables.")
    if not value:
        return f"sqlite:///{(DATA_DIR / 'nearbuy.db').as_posix()}"
    # Providers commonly supply postgres:// or postgresql:// URLs. Use psycopg 3.
    if value.startswith("postgres://"):
        value = "postgresql+psycopg://" + value[len("postgres://"):]
    elif value.startswith("postgresql://"):
        value = "postgresql+psycopg://" + value[len("postgresql://"):]
    return value


if IS_VERCEL and not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY is required on Vercel. Set a long random value in Project Environment Variables.")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or _load_or_create_secret()
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_VERCEL or os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
