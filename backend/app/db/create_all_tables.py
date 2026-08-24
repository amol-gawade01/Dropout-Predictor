from backend.app.db.session import engine

from backend.app.db.models import Base

import backend.app.db.models  # noqa: F401


def main():
    Base.metadata.create_all(
        bind=engine
    )

    print(
        "All database tables created."
    )


if __name__ == "__main__":
    main()