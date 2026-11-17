"""The content test: every line under content/bank is a valid question
that fits the catalog and passed the pipeline. It runs in CI with the
other tests, so a broken question cannot reach main.
"""

from app.services.catalog_file import CATALOG_FILE_NAME, load_catalog
from app.services.question_files import BANK_DIR_NAME, load_bank
from app.settings import Settings


def test_every_line_of_the_question_bank_is_valid() -> None:
    content_dir = Settings().content_dir
    catalog = load_catalog(content_dir / CATALOG_FILE_NAME)

    _, problems = load_bank(content_dir / BANK_DIR_NAME, catalog)

    assert [str(problem) for problem in problems] == []
