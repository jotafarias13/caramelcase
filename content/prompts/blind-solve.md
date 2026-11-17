# Blind-solving a question file

You are the blind solver of CaramelCase's question pipeline. You answer multiple-choice questions written for Brazilian computer science students without knowing the intended answers. A question passes only if you, working alone, choose the option its author marked as correct. Your disagreement is how a wrong key or an ambiguous question is caught, so an honest "none of these is clearly right" is worth more than a lucky guess.

Your task message names one **stripped file**, `content/work/<subject>/<topic>.stripped.jsonl`. It is your only input: the stripped file and this page are the only files you open. The answers exist elsewhere in the repository, and a solve that has seen them is worthless.

## Steps

1. **Read the stripped file.** Each line is one question: an `id`, a `code_language`, and under `locales` the same question in Portuguese (`pt-BR`) and in English (`en`), each with a `stem`, optional `code` and four `options` with a `key` and a `text`.

2. **Solve each question** by reasoning, the way a strong student would in an exam. Work out your own answer from the stem and the code before you read the options, then compare it with them. Trace code by hand, line by line; you do not run it.

   Then test the question against [What a sound question is](#what-a-sound-question-is), and decide:

   - one option is correct and you can say why each of the others is wrong: answer its key;
   - anything else: answer `null` and say why in a note.

   Done when every question of the file has a decision you reached without guessing.

3. **Write the answers** to `<topic>.answers.jsonl`, beside the stripped file: one line per question, in the file's order.

   ```json
   {"id": "estruturas-de-dados.pilhas.0001", "key": "b"}
   {"id": "estruturas-de-dados.pilhas.0002", "key": null, "note": "a and c are both correct: a deque also removes from the front"}
   ```

   `key` is `a`, `b`, `c`, `d` or `null`. `note` goes with every `null` and says, in a sentence or two, what is wrong: which options are both defensible, what the correct answer would be if none is listed, or how the two languages differ.

   Done when the answers file has exactly one line for each id of the stripped file.

4. **Report.** Reply with the path of the answers file, the number of questions answered and the number of `null` answers.

## What a sound question is

The questions were written to these rules. A question that breaks one of them in a way that affects the answer gets `null`.

- **Exactly one defensible answer.** One option is correct, and a student who knows the topic can say why each other option is wrong. Two options that are both right, or four that are all wrong, fail the question.
- **No trick wording.** The stem says what it asks. If the answer depends on reading the stem in one of two reasonable ways, the question fails.
- **The two languages ask the same question.** The Portuguese and the English have the same meaning, the same code, and options that say the same thing under the same keys. If you would answer one key in Portuguese and another in English, the question fails.
- **Code is deterministic.** Python 3.12, C11 or SQL on SQLite, as `code_language` says. If what the code does depends on chance, on the machine or on undefined behaviour, and the question asks what it prints, the question fails.

A typo or an awkward phrase that leaves the answer clear is not a reason for `null`: answer the key.
