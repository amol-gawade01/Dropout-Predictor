from dataclasses import dataclass


@dataclass(frozen=True)
class BKTParameters:
    learn: float = 0.10
    slip: float = 0.10
    guess: float = 0.20


DEFAULT_BKT_PARAMETERS = BKTParameters()


def update_mastery(
    prior_mastery: float,
    correct: bool,
    params: BKTParameters = DEFAULT_BKT_PARAMETERS,
) -> float:

    prior = max(
        0.01,
        min(0.99, float(prior_mastery))
    )

    if correct:

        numerator = (
            prior
            * (1.0 - params.slip)
        )

        denominator = (
            numerator
            + (1.0 - prior)
            * params.guess
        )

    else:

        numerator = (
            prior
            * params.slip
        )

        denominator = (
            numerator
            + (1.0 - prior)
            * (1.0 - params.guess)
        )

    if denominator <= 0:
        posterior = prior
    else:
        posterior = numerator / denominator

    mastery_after_learning = (
        posterior
        + (1.0 - posterior)
        * params.learn
    )

    return round(
        max(
            0.01,
            min(
                0.99,
                mastery_after_learning
            )
        ),
        4
    )