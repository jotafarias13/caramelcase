"""GET /config: what the web app needs before it draws anything."""

from decimal import Decimal

from pydantic import BaseModel

from app.domain.entitlements import Entitlements
from app.enums import PlanKey
from app.settings import PlanLimits


class PlanModel(BaseModel):
    key: str
    price_month_brl: Decimal
    price_year_brl: Decimal | None
    price_semester_brl: Decimal | None
    limits: PlanLimits


class EntitlementsModel(BaseModel):
    """What this user may do. The server enforces it; the app mirrors it."""

    plan_key: PlanKey | None  # null while billing is off
    sessions_per_day: int | None  # null means no limit
    ads: bool
    tutor_messages_per_day: int | None  # null means no limit
    exam_mode: bool
    exam_tracks: bool

    @classmethod
    def of(cls, entitlements: Entitlements) -> "EntitlementsModel":
        return cls(
            plan_key=entitlements.plan_key,
            sessions_per_day=entitlements.sessions_per_day,
            ads=entitlements.ads,
            tutor_messages_per_day=entitlements.tutor_messages_per_day,
            exam_mode=entitlements.exam_mode,
            exam_tracks=entitlements.exam_tracks,
        )


class ConfigResponse(BaseModel):
    # Flag key -> is the feature on for whoever is asking.
    flags: dict[str, bool]
    plans: list[PlanModel]
    entitlements: EntitlementsModel
    # Is "Continue with Google" available on this server.
    google_sign_in: bool
    session_length: int
    daily_goal_options: list[int]
    xp_per_level: int
