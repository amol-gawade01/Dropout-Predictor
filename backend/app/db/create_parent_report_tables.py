from backend.app.db.session import engine

from backend.app.db.models import (
    GuardianContact,
    ParentReportDelivery,
)


def main():

    GuardianContact.__table__.create(
        bind=engine,
        checkfirst=True,
    )

    ParentReportDelivery.__table__.create(
        bind=engine,
        checkfirst=True,
    )

    print(
        "Parent report tables created."
    )


if __name__ == "__main__":
    main()