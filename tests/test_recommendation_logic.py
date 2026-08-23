from backend.app.services.recommendation_service import (
    recommendation_priority,
)


class FakeRisk:

    def __init__(
        self,
        risk_tier,
    ):
        self.risk_tier = risk_tier


def test_critical_priority():

    risk = FakeRisk(
        "CRITICAL"
    )

    assert (
        recommendation_priority(
            risk
        )
        == "HIGH"
    )


def test_moderate_priority():

    risk = FakeRisk(
        "MODERATE"
    )

    assert (
        recommendation_priority(
            risk
        )
        == "MEDIUM"
    )


def test_low_priority():

    risk = FakeRisk(
        "LOW"
    )

    assert (
        recommendation_priority(
            risk
        )
        == "NORMAL"
    )


def test_missing_risk_priority():

    assert (
        recommendation_priority(
            None
        )
        == "NORMAL"
    )