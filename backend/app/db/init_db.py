from sqlalchemy import text

from backend.app.db.base import Base
from backend.app.db.session import engine

# Important: importing models registers all SQLAlchemy tables.
from backend.app.db import models  # noqa: F401


def init_database():
    with engine.begin() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()