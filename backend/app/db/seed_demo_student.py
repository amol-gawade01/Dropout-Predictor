from backend.app.db.session import (
    SessionLocal,
)

from backend.app.db.models import (
    Student,
)


def seed():

    db = SessionLocal()

    try:

        student_code = "SYN00001"

        existing = (
            db.query(Student)
            .filter(
                Student.student_code
                == student_code
            )
            .first()
        )


        if existing:

            print(
                "Already exists:",
                existing.student_code,
            )

            return


        student = Student(

            student_code=
                "SYN00001",

            display_name=
                "Demo Student",

            program_stream=
                "Artificial Intelligence "
                "and Data Science",

            institution_type=
                "Engineering College",

            residence_mode=
                "DAY_SCHOLAR",

            scholarship_holder=
                False,

            preferred_language=
                "en-IN",

            is_synthetic=
                True,
        )


        db.add(student)

        db.commit()

        db.refresh(student)


        print(
            "Created student:",
            student.student_code,
        )

        print(
            "Student ID:",
            student.student_id,
        )


    finally:

        db.close()


if __name__ == "__main__":
    seed()  