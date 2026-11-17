"""Business rules as pure functions: no database, no HTTP, no clock.

Each module has unit tests in tests/domain/, and every number comes from
app.settings.

- question_doc.py   the format of a question in the content files
- rating.py         how the two ratings move after an answer
- selection.py      which questions a session gets; option order
- xp.py             XP per answer and per session; levels
- daily_goal.py     questions today against the goal
- local_time.py     the student's own calendar day
- streak.py         days in a row with a finished session
- mastery.py        new, learning, practiced, mastered
- review.py         when a missed question is due again
- flags.py          off, staff, on
- entitlements.py   what a user may do (completed in milestone 10)
"""
