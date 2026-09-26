from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Account

from app.core.password import get_password_hash


def seed_account(db: Session):
    """Create the first manager account, reading username/email/password from .env."""
    username = settings.ST_USERNAME
    email = settings.ST_EMAIL
    password = settings.ST_PASSWORD

    if not username or not email or not password:
        print("⚠️ ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD not found in .env, skipping seed_account!")
        return

    existing = db.query(Account).filter(Account.username == username).first()
    if existing:
        print(f"ℹ️ Account '{username}' already exists, skipping.")
        return

    account = Account(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
    )
    db.add(account)
    print("✅ seed_account ready!")
