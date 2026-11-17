"""Catalog: the published subjects and their topics."""

from fastapi import APIRouter

from app.db.session import SessionDep
from app.routes.dependencies import CurrentUser, SettingsDep
from app.schemas.catalog import SubjectDetail, SubjectsResponse
from app.services.catalog import list_subjects, subject_detail

router = APIRouter(prefix="/subjects", tags=["catalog"])


@router.get("")
async def get_subjects(
    session: SessionDep, user: CurrentUser
) -> SubjectsResponse:
    return SubjectsResponse(subjects=await list_subjects(session, user))


@router.get("/{slug}")
async def get_subject(
    slug: str, session: SessionDep, user: CurrentUser, settings: SettingsDep
) -> SubjectDetail:
    """A subject's topics with the user's mastery of each."""
    return await subject_detail(session, user, slug, settings)
