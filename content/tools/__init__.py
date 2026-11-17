"""The content pipeline's tools: python -m content.tools <command>.

Run from the repository root, in the API's environment:

    uv run --project api python -m content.tools --help

The tools read questions through the API's QuestionDoc, so a file the
tools accept is a file the importer accepts. The API is not an installed
package: the lines below put api/ on the import path.
"""

import sys
from pathlib import Path

_API_DIR = Path(__file__).resolve().parents[2] / "api"
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))
