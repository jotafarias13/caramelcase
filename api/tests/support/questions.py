"""Questions for the tests: the spec's sample line and variations of it."""

import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from app.domain.question_doc import QuestionDoc
from app.services.catalog_file import CATALOG_FILE_NAME, Catalog, load_catalog
from app.settings import Settings

# The sample line of docs/initial-spec.md. The spec abbreviates its
# English text to "..." and an empty list; here it is written out.
SPEC_SAMPLE_LINE = """
{
  "id": "estruturas-de-dados.pilhas.0001",
  "subject": "estruturas-de-dados",
  "topic": "pilhas",
  "type": "mcq",
  "difficulty_prior": 1,
  "correct_key": "b",
  "code_language": null,
  "source": "generated",
  "version": 1,
  "locales": {
    "pt-BR": {
      "stem": "Qual estrutura de dados segue a política LIFO?",
      "code": null,
      "options": [
        {"key": "a", "text": "Fila", "reason": "A fila é FIFO: quem entra primeiro sai primeiro."},
        {"key": "b", "text": "Pilha", "reason": "Na pilha, o último elemento inserido é o primeiro a sair."},
        {"key": "c", "text": "Lista ligada", "reason": "A lista ligada não impõe ordem de remoção."},
        {"key": "d", "text": "Árvore binária", "reason": "A árvore organiza hierarquia, não ordem de chegada."}
      ],
      "explanation": "LIFO significa que o último a entrar é o primeiro a sair, como uma pilha de pratos."
    },
    "en": {
      "stem": "Which data structure follows the LIFO policy?",
      "code": null,
      "options": [
        {"key": "a", "text": "Queue", "reason": "A queue is FIFO: the first element in is the first out."},
        {"key": "b", "text": "Stack", "reason": "In a stack, the last element pushed is the first one popped."},
        {"key": "c", "text": "Linked list", "reason": "A linked list does not impose a removal order."},
        {"key": "d", "text": "Binary tree", "reason": "A tree organizes a hierarchy, not an order of arrival."}
      ],
      "explanation": "LIFO means last in, first out, like a stack of plates."
    }
  },
  "verification": {"blind_key": "b", "blind_agrees": true, "code_ran": null, "human_checked": false}
}
"""  # noqa: E501

# Stems different enough that no two are near-duplicates. Question n of a
# test gets the nth one.
STEMS = (
    "Qual estrutura de dados segue a política LIFO?",
    "Em que ordem uma fila entrega os elementos que recebeu?",
    "Quanto custa buscar uma chave em uma tabela de dispersão sem colisões?",
    "O que acontece ao desempilhar de uma pilha vazia?",
    "Por que a busca binária exige um vetor ordenado?",
    "Quantos ponteiros tem cada nó de uma lista duplamente encadeada?",
)

PYTHON_PRINTS_2 = "pilha = [1, 2, 3]\npilha.pop()\nprint(pilha[-1])"
C_PRINTS_2 = (
    "#include <stdio.h>\n"
    "\n"
    "int main(void) {\n"
    "    int v[] = {1, 2, 3};\n"
    "    int *p = v;\n"
    '    printf("%d\\n", *(p + 1));\n'
    "    return 0;\n"
    "}"
)
SQL_PRINTS_2 = (
    "CREATE TABLE aluno (id INTEGER PRIMARY KEY, nota REAL);\n"
    "INSERT INTO aluno VALUES (1, 8.5), (2, 6.0), (3, NULL);\n"
    "SELECT COUNT(nota) FROM aluno;"
)


def question(  # noqa: PLR0913  one keyword per thing a test varies
    number: int = 1,
    *,
    subject: str = "estruturas-de-dados",
    topic: str = "pilhas",
    stem: str | None = None,
    code: str | None = None,
    code_language: str | None = None,
    code_check: str | None = None,
    options: Sequence[str] | None = None,
    correct_key: str = "b",
    difficulty: int = 1,
    verified: bool = False,
) -> dict[str, Any]:
    """A valid question, as the data of its line: the spec's sample with
    the given changes. `stem`, `code` and `options` (the four texts, a to
    d) go into both languages. Without `verified`, nothing of the
    pipeline is recorded.
    """
    data: dict[str, Any] = json.loads(SPEC_SAMPLE_LINE)
    data["id"] = f"{subject}.{topic}.{number:04d}"
    data["subject"] = subject
    data["topic"] = topic
    data["difficulty_prior"] = difficulty
    data["correct_key"] = correct_key
    data["code_language"] = code_language
    data["code_check"] = code_check
    for text in data["locales"].values():
        text["stem"] = stem or STEMS[number - 1]
        text["code"] = code
        if options is not None:
            for option, option_text in zip(
                text["options"], options, strict=True
            ):
                option["text"] = option_text
    runs = code_check in ("output", "runs")
    data["verification"] = {
        "blind_key": correct_key if verified else None,
        "blind_agrees": True if verified else None,
        "code_ran": True if verified and runs else None,
        "human_checked": False,
    }
    return data


def output_question(
    number: int, code: str, code_language: str, **changes: Any
) -> dict[str, Any]:
    """A question about what its code prints: the code prints 2, and the
    options are 1, 2, 3 and 4 with b correct.
    """
    return question(
        number,
        code=code,
        code_language=code_language,
        code_check="output",
        options=["1", "2", "3", "4"],
        **changes,
    )


def doc(data: dict[str, Any] | None = None) -> QuestionDoc:
    return QuestionDoc.model_validate(data or question())


def write_lines(path: Path, questions: Iterable[dict[str, Any]]) -> Path:
    """Write the questions to a file, one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(
        json.dumps(data, ensure_ascii=False) + "\n" for data in questions
    )
    path.write_text(text, encoding="utf-8")
    return path


def read_lines(path: Path) -> list[dict[str, Any]]:
    """The data of each line of a JSON-lines file."""
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def the_catalog() -> Catalog:
    """The repository's content/catalog.yaml."""
    return load_catalog(Settings().content_dir / CATALOG_FILE_NAME)
