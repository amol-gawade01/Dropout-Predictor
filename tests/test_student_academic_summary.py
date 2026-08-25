from datetime import date
from types import SimpleNamespace

from backend.app.db.models import Student
from backend.app.services.student_dashboard_service import get_student_academic_summary


class FakeQuery:
    def __init__(self, value):
        self.value = value

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self.value


class FakeDb:
    def __init__(self, student, snapshot):
        self.student = student
        self.snapshot = snapshot

    def query(self, model):
        return FakeQuery(self.student if model is Student else self.snapshot)


def make_student():
    return SimpleNamespace(student_id="student-id", student_code="STU001")


def test_academic_summary_returns_latest_attendance_and_results():
    snapshot = SimpleNamespace(
        semester=4,
        week_start_date=date(2026, 8, 24),
        current_gpa=8.126,
        failed_subjects=1,
        backlog_count=0,
        credits_completion_ratio=0.875,
        attendance_pct=82.456,
        attendance_velocity_14d=-3.2,
        consecutive_absent_days=2,
        assignment_completion_pct=91.4,
        missed_assessments=1,
        source="COLLEGE",
    )

    result = get_student_academic_summary(FakeDb(make_student(), snapshot), "STU001")

    assert result == {
        "available": True,
        "semester": 4,
        "week_start_date": date(2026, 8, 24),
        "current_gpa": 8.13,
        "failed_subjects": 1,
        "backlog_count": 0,
        "credits_completion_percentage": 87.5,
        "attendance_percentage": 82.46,
        "attendance_change_14d": -3.2,
        "consecutive_absent_days": 2,
        "assignment_completion_percentage": 91.4,
        "missed_assessments": 1,
        "source": "COLLEGE",
    }


def test_academic_summary_has_safe_empty_state():
    result = get_student_academic_summary(FakeDb(make_student(), None), "STU001")
    assert result["available"] is False
    assert "uploaded" in result["message"]
