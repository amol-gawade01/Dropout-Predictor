from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from backend.app.schemas.tutor import StartLearningSessionRequest
from backend.app.services import learning_session_service
from tutor.question_bank import (
    QUESTION_BANK,
    QUESTION_TRANSLATIONS,
    get_display_question,
)


def test_question_ids_are_unique_and_each_concept_has_enough_questions():
    question_ids = [question["question_id"] for question in QUESTION_BANK]
    assert len(question_ids) == len(set(question_ids))
    for concept_id in {question["concept_id"] for question in QUESTION_BANK}:
        assert sum(question["concept_id"] == concept_id for question in QUESTION_BANK) >= 7


@pytest.mark.parametrize("language_code", ["hi-IN", "mr-IN"])
def test_every_question_has_a_native_translation(language_code):
    translations = QUESTION_TRANSLATIONS[language_code]
    assert set(translations) == {question["question_id"] for question in QUESTION_BANK}
    assert all(
        any("\u0900" <= character <= "\u097f" for character in text)
        for text in translations.values()
    )


@pytest.mark.parametrize("language_code", ["hi-IN", "mr-IN"])
def test_first_session_question_uses_selected_language(monkeypatch, language_code):
    question = QUESTION_BANK[0]
    session = SimpleNamespace(
        status="ACTIVE",
        answered_questions=0,
        target_questions=5,
        student_id="student-id",
        active_concept_id=question["concept_id"],
        session_id="session-id",
        language_code=language_code,
    )
    concept = SimpleNamespace(concept_id=question["concept_id"], topic_name="Arrays")
    db = SimpleNamespace(get=lambda model, key: concept)
    monkeypatch.setattr(learning_session_service, "get_mastery_probability", lambda **kwargs: 0.2)
    monkeypatch.setattr(learning_session_service, "get_used_question_ids", lambda *args: set())
    monkeypatch.setattr(learning_session_service, "select_question", lambda **kwargs: question)

    result = learning_session_service.get_next_session_question(db, session)

    assert result["question"]["text"] == get_display_question(question, language_code)
    assert result["question"]["text"] != question["question"]


def test_unsupported_session_language_is_rejected():
    with pytest.raises(ValidationError):
        StartLearningSessionRequest(
            student_code="STU001",
            concept_id="dsa_arrays",
            language_code="fr-FR",
        )


def test_session_with_no_questions_is_rejected_before_creation(monkeypatch):
    concept = SimpleNamespace(concept_id="dsa_graphs", topic_name="Graphs")
    student = SimpleNamespace(student_id="student-id", student_code="STU001")
    db = SimpleNamespace(get=lambda model, key: concept)
    monkeypatch.setattr(learning_session_service, "find_student", lambda *args: student)

    with pytest.raises(ValueError, match="does not have practice questions"):
        learning_session_service.start_learning_session(
            db=db,
            student_code="STU001",
            concept_id="dsa_graphs",
            target_questions=5,
            language_code="en-IN",
        )
