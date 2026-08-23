from backend.app.db.session import engine
from backend.app.db.models import Base

# Importing models registers all tables
import backend.app.db.models  # noqa: F401


def create_tables():

    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Learning session tables created."
    )


if __name__ == "__main__":
    create_tables()