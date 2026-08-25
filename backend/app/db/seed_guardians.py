from datetime import UTC, datetime

from backend.app.db.models import Student, StudentGuardian
from backend.app.db.session import SessionLocal

SAMPLE_GUARDIANS = [
    ("8779456230", "amolgawade56@gmail.com", "Sample Guardian 1"),
    ("7715818287", "amolgawade56@gmail.com", "Sample Guardian 2"),
    ("9326983772", "amolgawade56@gmail.com", "Sample Guardian 3"),
]


def seed():
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.student_code).limit(3).all()
        if len(students) < 3:
            raise RuntimeError("Seed at least three students before guardians")
        for student, (phone, email, name) in zip(students, SAMPLE_GUARDIANS, strict=True):
            exists = (
                db.query(StudentGuardian)
                .filter(
                    StudentGuardian.student_id == student.student_id,
                    StudentGuardian.phone_number == phone,
                )
                .first()
            )
            if exists:
                exists.email_address = email
                exists.email_opt_in = True
                exists.consent_recorded_at = exists.consent_recorded_at or datetime.now(UTC)
                print("Updated:", student.student_code, email)
                continue
            db.add(
                StudentGuardian(
                    student_id=student.student_id,
                    guardian_name=name,
                    phone_number=phone,
                    email_address=email,
                    relationship="GUARDIAN",
                    preferred_language="en-IN",
                    email_opt_in=True,
                    consent_recorded_at=datetime.now(UTC),
                )
            )
            print("Created:", student.student_code, phone)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
