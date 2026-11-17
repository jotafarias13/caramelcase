"""The prompts in content/prompts/ agree with the format and the tools."""

import json
import re
from pathlib import Path

from app.domain.question_doc import QuestionDoc, unverified_reasons
from app.settings import Settings
from content.tools.check_blind import BlindAnswer
from content.tools.run_code import check_code
from tests.support.questions import the_catalog

SETTINGS = Settings()
PROMPTS_DIR = SETTINGS.content_dir / "prompts"
JSON_BLOCK = re.compile(r"```json\n(.*?)```", re.DOTALL)


def _json_blocks(prompt: Path) -> list[str]:
    return JSON_BLOCK.findall(prompt.read_text(encoding="utf-8"))


def test_the_example_question_of_the_generation_prompt_is_valid() -> None:
    [block] = _json_blocks(PROMPTS_DIR / "generate.md")

    example = QuestionDoc.model_validate(json.loads(block))

    subject = the_catalog().subject(example.subject)
    assert subject is not None
    topic = subject.topic(example.topic)
    assert topic is not None
    assert example.code_language == topic.code_language
    # It is as a writer leaves it: nothing of the pipeline recorded yet.
    assert unverified_reasons(example) == [
        "it was not blind-solved",
        "its code was not run",
    ]
    # And its code prints its correct option.
    assert check_code(example, SETTINGS) is None


def test_the_generation_prompt_states_the_limits_of_settings() -> None:
    text = (PROMPTS_DIR / "generate.md").read_text(encoding="utf-8")

    for statement in (
        f"sentence, at most {SETTINGS.question_reason_max_chars} characters",
        f"in at most {SETTINGS.question_explanation_max_chars} characters",
        f"A stem has at most {SETTINGS.question_stem_max_chars} characters",
        f"an option's text at most {SETTINGS.question_option_max_chars}",
        f"At most {SETTINGS.question_code_max_lines} lines of at most "
        f"{SETTINGS.question_code_max_line_chars} characters",
    ):
        assert statement in text


def test_the_example_answers_of_the_blind_solve_prompt_are_answer_lines() -> (
    None
):
    [block] = _json_blocks(PROMPTS_DIR / "blind-solve.md")

    # The block is indented, inside a step of the prompt.
    answers = [
        BlindAnswer.model_validate_json(line)
        for line in block.splitlines()
        if line.strip()
    ]

    assert [answer.key for answer in answers] == ["b", None]
    assert answers[1].note is not None


def test_both_prompts_carry_the_writing_rule_of_one_defensible_answer() -> (
    None
):
    for name in ("generate.md", "blind-solve.md"):
        text = (PROMPTS_DIR / name).read_text(encoding="utf-8")
        assert "Exactly one defensible answer" in text
