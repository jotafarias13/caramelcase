import pytest

from app.settings import Settings


def test_cors_origins_are_read_as_a_comma_separated_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS", "https://caramelcase.app, https://www.caramelcase.app"
    )

    assert Settings().cors_origins == [
        "https://caramelcase.app",
        "https://www.caramelcase.app",
    ]


def test_a_tunable_is_overridden_by_its_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SESSION_LENGTH", "5")
    monkeypatch.setenv("REVIEW_INTERVALS_DAYS", "[1, 2, 4]")

    settings = Settings()

    assert settings.session_length == 5
    assert settings.review_intervals_days == (1, 2, 4)


def test_question_ratings_rise_with_the_difficulty_prior() -> None:
    ratings = Settings().question_rating_by_prior

    assert list(ratings) == sorted(ratings)
    assert ratings[2] == Settings().user_rating_start
