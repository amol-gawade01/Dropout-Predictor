from sqlalchemy import text

from backend.app.db.session import engine


def main():
    statements = (
        "ALTER TABLE student_guardians ADD COLUMN IF NOT EXISTS email_address VARCHAR(255)",
        "ALTER TABLE student_guardians ADD COLUMN IF NOT EXISTS email_opt_in BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE parent_report_deliveries ADD COLUMN IF NOT EXISTS email_message_id VARCHAR(255)",
    )
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
    print("Guardian email columns are ready.")


if __name__ == "__main__":
    main()
