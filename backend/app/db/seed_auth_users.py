import os

from dotenv import load_dotenv

load_dotenv()

from backend.app.db.session import (
    SessionLocal,
)
from backend.app.services.auth_service import (
    create_user_account,
)


def seed():

    admin_password = os.getenv("DEMO_ADMIN_PASSWORD")

    faculty_password = os.getenv("DEMO_FACULTY_PASSWORD")

    student_password = os.getenv("DEMO_STUDENT_PASSWORD")

    if not all(
        [
            admin_password,
            faculty_password,
            student_password,
        ]
    ):
        raise RuntimeError(
            "Set DEMO_ADMIN_PASSWORD, DEMO_FACULTY_PASSWORD and DEMO_STUDENT_PASSWORD in .env"
        )

    db = SessionLocal()

    users = [
        {
            "email": "admin@sih.demo",
            "password": admin_password,
            "display_name": "SIH Admin",
            "role": "ADMIN",
            "student_code": None,
        },
        {
            "email": "faculty@sih.demo",
            "password": faculty_password,
            "display_name": "Demo Faculty",
            "role": "FACULTY",
            "student_code": None,
        },
        {
            "email": "student@sih.demo",
            "password": student_password,
            "display_name": "Demo Student",
            "role": "STUDENT",
            "student_code": "SYN00001",
        },
        {
            "email": "faculty.reports@sih.demo",
            "password": faculty_password,
            "display_name": "Reports Faculty",
            "role": "FACULTY",
            "student_code": None,
        },
        {
            "email": "admin.operations@sih.demo",
            "password": admin_password,
            "display_name": "Operations Admin",
            "role": "ADMIN",
            "student_code": None,
        },
    ]

    try:
        for item in users:
            try:
                create_user_account(
                    db=db,
                    **item,
                )

                print(
                    "Created:",
                    item["email"],
                )

            except ValueError as exc:
                if "already registered" in str(exc):
                    print(
                        "Already exists:",
                        item["email"],
                    )

                else:
                    raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
