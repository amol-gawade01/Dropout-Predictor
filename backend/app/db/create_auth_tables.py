from backend.app.db.models import Base
from backend.app.db.session import engine

import backend.app.db.models  # noqa: F401


def create_tables():

    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Authentication tables created."
    )


if __name__ == "__main__":
    create_tables()