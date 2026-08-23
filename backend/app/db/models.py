import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


# ============================================================
# 1. STUDENT MASTER
# ============================================================


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    program_stream: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    institution_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    residence_mode: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    scholarship_holder: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    preferred_language: Mapped[str] = mapped_column(
        String(20),
        default="en",
    )

    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ============================================================
# 2. WEEKLY STUDENT RISK FEATURES
# ============================================================


class StudentFeatureSnapshot(Base):
    __tablename__ = "student_feature_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "week_start_date",
            name="uq_student_snapshot_week",
        ),
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "students.student_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    week_start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    semester: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # --------------------------------------------------------
    # FACTOR 1 — ACADEMIC DIFFICULTY
    # --------------------------------------------------------

    current_gpa: Mapped[float] = mapped_column(Float)

    failed_subjects: Mapped[int] = mapped_column(Integer)

    backlog_count: Mapped[int] = mapped_column(Integer)

    credits_completion_ratio: Mapped[float] = mapped_column(Float)

    # --------------------------------------------------------
    # FACTOR 2 — ATTENDANCE DECLINE
    # --------------------------------------------------------

    attendance_pct: Mapped[float] = mapped_column(Float)

    attendance_velocity_14d: Mapped[float] = mapped_column(Float)

    consecutive_absent_days: Mapped[int] = mapped_column(Integer)

    # --------------------------------------------------------
    # FACTOR 3 — LOW LEARNING ENGAGEMENT
    # --------------------------------------------------------

    lms_active_hours_week: Mapped[float] = mapped_column(Float)

    lms_activity_velocity_pct: Mapped[float] = mapped_column(Float)

    assignment_completion_pct: Mapped[float] = mapped_column(Float)

    avg_assignment_delay_days: Mapped[float] = mapped_column(Float)

    missed_assessments: Mapped[int] = mapped_column(Integer)

    # --------------------------------------------------------
    # FACTOR 4 — FINANCIAL STRESS
    # --------------------------------------------------------

    fee_overdue_days: Mapped[int] = mapped_column(Integer)

    scholarship_delay_days: Mapped[int] = mapped_column(Integer)

    financial_support_requested: Mapped[bool] = mapped_column(Boolean)

    # --------------------------------------------------------
    # FACTOR 5 — EMPLOYMENT / WORK PRESSURE
    # --------------------------------------------------------

    paid_work_hours_week: Mapped[float] = mapped_column(Float)

    # --------------------------------------------------------
    # FACTOR 6 — FAMILY RESPONSIBILITY
    # --------------------------------------------------------

    family_responsibility_hours_week: Mapped[float] = mapped_column(Float)

    # --------------------------------------------------------
    # FACTOR 7 — COURSE MISMATCH
    # --------------------------------------------------------

    course_satisfaction_1_5: Mapped[float] = mapped_column(Float)

    career_uncertainty_1_5: Mapped[float] = mapped_column(Float)

    # --------------------------------------------------------
    # FACTOR 8 — TRANSITION / LANGUAGE GAP
    # --------------------------------------------------------

    prerequisite_gap_score: Mapped[float] = mapped_column(Float)

    language_transition_score: Mapped[float] = mapped_column(Float)

    # --------------------------------------------------------
    # FACTOR 9 — COMMUTE / HOUSING
    # --------------------------------------------------------

    commute_minutes_one_way: Mapped[int] = mapped_column(Integer)

    hostel_issue_score: Mapped[float] = mapped_column(Float)

    # --------------------------------------------------------
    # FACTOR 10 — BELONGING / SUPPORT
    # --------------------------------------------------------

    campus_belonging_1_5: Mapped[float] = mapped_column(Float)

    mentor_interactions_month: Mapped[int] = mapped_column(Integer)

    # --------------------------------------------------------
    # FACTOR 11 — WELLBEING / SUPPORT NEED
    # --------------------------------------------------------

    overwhelmed_score_1_5: Mapped[float] = mapped_column(Float)

    support_requested: Mapped[bool] = mapped_column(Boolean)

    # Synthetic factor values from our generated dataset.
    # Later these can instead be computed dynamically.
    factor_scores: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        default="COLLEGE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ============================================================
# 3. MODEL PREDICTIONS
# ============================================================


class RiskInference(Base):
    __tablename__ = "risk_inferences"

    inference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "students.student_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "student_feature_snapshots.snapshot_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    model_version: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    risk_tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    decision_threshold: Mapped[float] = mapped_column(Float)

    predicted_dropout: Mapped[bool] = mapped_column(Boolean)

    top_features: Mapped[list | dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    top_factors: Mapped[list | dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ============================================================
# 4. CONFIRMED STUDENT EXIT
# ============================================================


class StudentExitRecord(Base):
    __tablename__ = "student_exit_records"

    exit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "students.student_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    outcome_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    confirmed_reason: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    secondary_reasons: Mapped[list | dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
    )

    exit_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ============================================================
# 5. LANGGRAPH INTERVENTION TASK
# ============================================================


class InterventionTask(Base):
    __tablename__ = "intervention_tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "students.student_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    inference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_inferences.inference_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    routed_domain: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    remediation_plan: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    outreach_message_draft: Mapped[str | None] = mapped_column(
        Text,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING_REVIEW",
    )

    mentor_notes: Mapped[str | None] = mapped_column(
        Text,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# 6. TUTOR CONCEPT GRAPH
# ============================================================


class Concept(Base):
    __tablename__ = "concepts"

    concept_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    topic_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    grade_level: Mapped[int | None] = mapped_column(Integer)

    prerequisite_concept_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("concepts.concept_id"),
        nullable=True,
    )

    concept_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Change 384 if your final embedding model
    # uses a different vector dimension.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True,
    )


# ============================================================
# 7. STUDENT CONCEPT MASTERY
# ============================================================


class StudentConceptMastery(Base):
    __tablename__ = "student_concept_mastery"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "students.student_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    concept_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey(
            "concepts.concept_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    mastery_prob: Mapped[float] = mapped_column(
        Float,
        default=0.20,
    )

    total_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    consecutive_correct: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# 8. SOCRATIC TUTOR DIALOGUE LOGS
# ============================================================


class SocraticDialogueLog(Base):
    __tablename__ = "socratic_dialogue_logs"

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "students.student_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    concept_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("concepts.concept_id"),
        nullable=False,
    )

    student_raw_input: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language_code: Mapped[str] = mapped_column(
        String(20),
        default="en-IN",
    )

    diagnosed_error: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    socratic_prompt_returned: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    mastery_prior: Mapped[float] = mapped_column(Float)

    mastery_post: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

# ============================================================
# STUDENT LEARNING SESSION
# ============================================================


class StudentLearningSession(Base):

    __tablename__ = "student_learning_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )

    # Concept the student originally wanted to learn.
    primary_concept_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("concepts.concept_id"),
        nullable=False,
    )

    # Concept currently being practiced.
    # This can change temporarily when a prerequisite gap
    # is detected.
    active_concept_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("concepts.concept_id"),
        nullable=False,
    )

    language_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="en-IN",
    )

    target_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    answered_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    starting_mastery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.20,
    )

    final_mastery: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
        index=True,
    )

    completion_reason: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


# ============================================================
# LEARNING SESSION ATTEMPT
# ============================================================


class StudentLearningSessionAttempt(Base):

    __tablename__ = "student_learning_session_attempts"

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "student_learning_sessions.session_id"
        ),
        nullable=False,
        index=True,
    )

    # Links this attempt to your existing
    # SocraticDialogueLog.
    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "socratic_dialogue_logs.interaction_id"
        ),
        nullable=True,
    )

    question_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    concept_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("concepts.concept_id"),
        nullable=False,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    diagnosis: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    mastery_before: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    mastery_after: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

# ============================================================
# USER ACCOUNT / AUTH
# ============================================================


class UserAccount(Base):

    __tablename__ = "user_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # STUDENT | FACULTY | ADMIN
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    # Only STUDENT accounts need this.
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.student_id"),
        nullable=True,
        unique=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )