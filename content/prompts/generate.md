# Writing questions for one topic

You write multiple-choice questions for CaramelCase, a practice app for Brazilian computer science students. A student answers ten questions in about five minutes, so every question, the hardest included, is solved in under a minute.

Your task message names a **subject**, a **topic**, **how many** questions and the **first id number**. You write them to `content/work/<subject>/<topic>.jsonl`, one question per line. Run every command from the repository root.

If the task message lists failed questions instead, go to [Repairing](#repairing).

## Steps

1. **Read the topic.** In `content/catalog.yaml`, read the topic's entry: `covers` is the syllabus content the questions come from and `code_language` is the language of any code. Read the names of the subject's other topics, so that you stay inside yours. If `content/bank/<subject>/<topic>.jsonl` exists, read its stems: you write new questions, not variations of those.

   Done when you can list the concepts in `covers` and say which neighbouring topic owns each concept you will leave out.

2. **Plan the set.** Write a list with one line per question: the concept it tests, its level and whether it has code. Follow [Difficulty](#difficulty) for the levels.

   Done when the list has the number of questions asked for, every concept in `covers` appears at least once, no two lines test the same fact, and the levels are as near as the number allows to 25% level 1 or 2, 50% level 3 and 25% level 4 or 5.

3. **Write the questions.** For each line of the plan, write the question in Portuguese, then in English, following [The line](#the-line) and [Writing rules](#writing-rules). Number the ids from the first id number, without gaps.

   Build the file with a short script kept outside the repository, in which each question is a dict written out with `json.dumps(question, ensure_ascii=False)`. A line typed by hand goes wrong at the quotes and line breaks of its code.

   Done when the file has one line per planned question.

4. **Check the file.** Run the three checks and fix what they report, until all three pass:

   ```sh
   uv run --project api python -m content.tools validate content/work/<subject>/<topic>.jsonl
   uv run --project api python -m content.tools run-code content/work/<subject>/<topic>.jsonl --dry-run
   uv run --project api python -m content.tools dedupe content/work/<subject>/<topic>.jsonl --against content/bank
   ```

   When `run-code` says the code printed something other than the correct option, the code is the authority: work out again what the right answer is, then fix the key, the options, the reasons and the explanation together.

   Done when each command exits with code 0.

5. **Solve your own questions.** Read each finished question as a student who sees only the stem, the code and the four options. Answer it without looking at the key, and try to defend each wrong option. `uv run --project api python -m content.tools strip-keys <file>` writes that view, without keys, reasons or explanations, to `<topic>.stripped.jsonl` beside the file.

   Done when, for every question, your answer is the key and you could not defend any other option. Rewrite a question that fails, then repeat step 4.

6. **Report.** Reply with the file's path, the number of questions at each level, and the ids of any question you are unsure about, with the doubt in one sentence.

## The line

Each line of the file is one JSON object. This one is spread over several lines to be readable; in the file it is a single line.

```json
{
  "id": "estruturas-de-dados.pilhas.0007",
  "subject": "estruturas-de-dados",
  "topic": "pilhas",
  "type": "mcq",
  "difficulty_prior": 3,
  "correct_key": "c",
  "code_language": "python",
  "code_check": "output",
  "source": "generated",
  "version": 1,
  "locales": {
    "pt-BR": {
      "stem": "O que este programa imprime?",
      "code": "pilha = []\nfor valor in [4, 8, 15]:\n    pilha.append(valor)\npilha.pop()\npilha.append(16)\nprint(pilha.pop() + pilha.pop())",
      "options": [
        {"key": "a", "text": "12", "reason": "Seria a soma de 4 e 8, mas o 16 empilhado por último é o primeiro a sair."},
        {"key": "b", "text": "23", "reason": "O 15 já tinha sido desempilhado antes de o 16 entrar, então não participa da soma."},
        {"key": "c", "text": "24", "reason": "Saem o 16 e depois o 8, os dois elementos mais recentes da pilha."},
        {"key": "d", "text": "31", "reason": "O 15 não está mais na pilha quando a soma é feita."}
      ],
      "explanation": "Depois de empilhar 4, 8 e 15, o programa desempilha o 15 e empilha o 16. A pilha fica [4, 8, 16], e os dois pop devolvem 16 e 8."
    },
    "en": {
      "stem": "What does this program print?",
      "code": "pilha = []\nfor valor in [4, 8, 15]:\n    pilha.append(valor)\npilha.pop()\npilha.append(16)\nprint(pilha.pop() + pilha.pop())",
      "options": [
        {"key": "a", "text": "12", "reason": "That would be 4 plus 8, but the 16 pushed last is the first one out."},
        {"key": "b", "text": "23", "reason": "The 15 was popped before the 16 went in, so it is not part of the sum."},
        {"key": "c", "text": "24", "reason": "The 16 comes out and then the 8, the two most recent elements of the stack."},
        {"key": "d", "text": "31", "reason": "The 15 is no longer on the stack when the sum is computed."}
      ],
      "explanation": "After pushing 4, 8 and 15, the program pops the 15 and pushes 16. The stack is [4, 8, 16], and the two pops return 16 and 8."
    }
  }
}
```

- `id` is `<subject>.<topic>.` and a four-digit number. `source` is `generated`, `type` is `mcq`, `version` is 1.
- `options` has the keys `a`, `b`, `c`, `d`, in that order, in both languages. `correct_key` names the right one. Across the file, each key is the correct one about equally often.
- Every option has a `reason`: one sentence, at most 160 characters, saying why that option is right or wrong. A wrong option's reason names the misconception behind it.
- `explanation` says, in at most 500 characters, how to reach the answer. A stem has at most 400 characters and an option's text at most 140.
- A question without code has `"code": null` in both languages, `"code_language": null` and `"code_check": null`.
- Leave `verification` out. The pipeline fills it in.
- All text is plain text: Markdown is shown to the student as typed.

`validate` checks every limit above and prints the line and the rule for each miss.

## Writing rules

- **Exactly one defensible answer.** A student who knows the topic picks the key and can say why each other option is wrong. Options such as "todas as anteriores" or "nenhuma das anteriores", and trick wording, are out.
- **Distractors come from real misconceptions**: the off-by-one, the confusion between two similar structures, the right idea applied to the wrong case. Each distractor has the length and the form of the correct option, so that neither length nor phrasing gives the answer away.
- **Test understanding over recall** wherever the topic allows it: apply the concept to a concrete case, trace code, compare two choices. Keep recall for level 1.
- **The text stands on its own.** Options are shuffled when shown, so a stem, a reason or an explanation refers to an option by what it says, never by its letter or its position.
- **Portuguese is written natively**, in the words a Brazilian lecturer uses, and the English says the same thing in natural English. The two versions ask the same question, with the same options in the same order and the same key.

## Difficulty

`difficulty_prior` sets the rating a question starts with, from 1 to 5.

| Level | What it asks |
| --- | --- |
| 1 | A definition or a fact from the first lesson on the topic |
| 2 | One concept applied directly |
| 3 | The typical exam question: a concept applied to a concrete case, or short code to trace |
| 4 | Two concepts combined, an edge case, or code that needs careful tracing |
| 5 | A subtle case that needs several steps of reasoning, still fair and still under a minute |

## Code

Use code when the question is about what code does. It goes in `code`, identical in both languages, and the stem refers to it as "este programa" or "este código".

- The language is the topic's `code_language`: `python`, `c` or `sql`.
- At most 15 lines of at most 80 characters, indented with spaces.
- Identifiers are in Portuguese without accents (`pilha`, `tamanho`, `proximo`), and the English text names them as the code does. The code has no comments and prints only values that read the same in both languages (numbers, proper names, codes), because it cannot be translated.
- It is deterministic: it reads no input, no file, no clock and no random number, and prints no address.

`code_check` says how the pipeline checks the code. Prefer `output`, then `runs`.

| `code_check` | Use it when | What the pipeline does |
| --- | --- | --- |
| `output` | The question asks what the program prints | Runs the code. What it prints must be exactly the text of the correct option, in both languages. Make the program print one line |
| `runs` | The code is complete but the question is about something else, such as its complexity | Runs the code, which must finish without an error |
| `skip` | The code must not run: a fragment, or code that fails on purpose (a compile error, undefined behaviour) | Nothing. Only the blind solver checks the question |

A question about code whose behaviour is undefined (an uninitialized or null pointer, a read out of bounds) never asks what the code prints: it asks which statement about the code is correct, with `skip`.

For `output` and `runs`, the code is a complete program:

- **Python** runs as a script on Python 3.12, with the standard library only.
- **C** is a full program with its `#include` lines and `main`. It is compiled as C11 with `-Wall -Werror` and the address and undefined-behaviour sanitizers, so a warning, a read out of bounds, a use after `free` or a signed overflow fails the run.
- **SQL** runs in an empty SQLite database with foreign keys enforced. The code creates its tables and inserts its rows before it queries them, so the student sees the data. Each row of a result is printed on one line, the columns separated by `|`, and NULL as `NULL`; a stem whose answer has more than one column says so, since the student has not seen that format. A query that returns several rows is asked through the number of its rows, with `SELECT COUNT(*)` and a sentence in the stem saying what it counts, or is built to return a single row. A result without rows prints nothing, so it cannot be the answer of an `output` question. Write standard SQL that SQLite accepts; a question about a feature SQLite lacks, such as stored procedures, uses `skip`.

## Repairing

The task message lists failed questions of one file, each with the reason: a validation problem, a failed run, a near-duplicate, or a blind solver who chose another option or none.

1. For each failed question, find the cause in the question itself. A blind solver who disagrees usually found a second defensible option or a wrong key: take the solver's note seriously. A near-duplicate is replaced by a question on another concept of the topic.
2. Rewrite the question under the same `id`, without its `verification`. Leave every other line of the file as it is.
3. Run the three checks of step 4 and solve the rewritten questions as in step 5.

Done when the checks pass and each rewritten question has one defensible answer. Reply with the ids you rewrote and what changed in each, in one sentence.
