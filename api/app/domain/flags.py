"""Feature flags: is a flag on for this user?"""

from app.enums import FlagState, UserRole


def flag_is_on(state: FlagState, role: UserRole | None) -> bool:
    """A flag is on for everyone, for staff only, or for nobody.

    role is None for a visitor without an account.
    """
    if state is FlagState.ON:
        return True
    return state is FlagState.STAFF and role is UserRole.STAFF
