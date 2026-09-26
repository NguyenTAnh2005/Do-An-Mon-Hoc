from app.db_connection import SessionLocal  # TODO: adjust to match the project's actual SessionLocal path

from app.seed.account import seed_account
from app.seed.area import seed_area
from app.seed.trash_bin import seed_trash_bin
from app.seed.classification_log import seed_classification_log


def run_seed():
    db = SessionLocal()
    print("📢 Starting seed data ...........")
    try:
        seed_account(db)
        seed_area(db)
        db.flush()  # need area ids to assign FK for trash_bin / classification_log below

        seed_trash_bin(db)
        seed_classification_log(db)

        db.commit()
        print("✅ Seed data succeeded, everything committed!")
    except Exception as e:
        db.rollback()
        print(f"❌ Oops, error while seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
