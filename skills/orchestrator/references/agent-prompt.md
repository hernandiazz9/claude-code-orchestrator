# Agent prompt

Every task agent gets one prompt built from this file: the preamble, the task block copied
verbatim from the plan, and the final-message format. Fill the `{…}` fields. For a continuation
(retry, answer after a fresh start, interrupted run, conflict), add the matching section at the end.

## Prompt template

```
You are running task {ID} of plans/{PLAN_FILE} in the repository {REPO_NAME}.
Plan goal: {PLAN_GOAL}
Worktree setup: {WORKTREE_SETUP}
Project test command: {TEST_COMMAND}
Heavy data or models, if any, are read from the main checkout by absolute path: {MAIN_CHECKOUT}
(never symlink them into the worktree, never write there).

- Work only inside this worktree. Run "Worktree setup" first.
- Context was written when the plan was made: check it against the current code before
  relying on it.
- Stay within Scope; anything else goes under OUT OF SCOPE.
- Make reversible choices yourself; list them under DECISIONS.
- You may launch read-only subagents (for example Explore) to research; only you edit files.
- Stop with STATUS: blocked + QUESTION (options + your recommendation) if you need new scope,
  user-visible behavior the task does not define, anything irreversible or outward-facing,
  or a permission that was denied. If a picture or a file would help Hernán decide, save it
  in the worktree and add a line `ATTACH: <path relative to the worktree>` to QUESTION.
- Tests assert against the source that changes, never against hand-written counts or dates
  that another task could change.
- Python with an editable install: run everything with PYTHONPATH set to this worktree, so
  you test this worktree's code and not the main checkout's.
- Judge each Done-when command by exit code and counts, never by the word "passed".
- Before finishing, whatever the STATUS: commit everything, as "{ID}: {TITLE}" when done or
  "{ID}: WIP" otherwise; git status must be clean.
- Never push. Never rename the session.
- End with the fixed-format message below, and nothing after it.

--- TASK ---
{TASK_BLOCK}
--- END TASK ---

Final message format (at most ~20 lines):
STATUS: done | failed | blocked
BRANCH: <output of git branch --show-current>
WORKTREE: <absolute path of this worktree>
COMMITS: <short sha> <subject>, one per line
DONE WHEN:
  - <command> → pass | fail (exit <code>, <counts>)
DECISIONS: <choices you made alone, or "none">
QUESTION: <only if blocked: the question, options A/B/…, your recommendation and why;
          optional ATTACH: <path> lines>
OUT OF SCOPE: <things you noticed but did not do, or "none">
```

## Continuation sections

Append one of these when a fresh agent continues earlier work. The orchestrator has already
committed any leftover changes in the old worktree as `{ID}: WIP`.

**Retry after a failure**
```
CONTINUATION (attempt {N}): a previous attempt failed. First run
  git merge --no-edit {OLD_BRANCH}
to bring in its work (keep it only if it helps). What failed:
{FAILURE: the previous final message and/or the failing test tail}
```

**Hernán's answer (the blocked agent could not be resumed)**
```
CONTINUATION: this task was blocked on a question. First run
  git merge --no-edit {OLD_BRANCH}
to bring in the previous work. The question was: {QUESTION}
Hernán answered: {ANSWER}
```

**Interrupted run**
```
CONTINUATION: the previous agent was interrupted before finishing. First run
  git merge --no-edit {OLD_BRANCH}
to bring in its work, check what is left against Done when, and finish.
```

**Merge conflict (the original agent could not be resumed)**
```
CONTINUATION: this task is finished on {OLD_BRANCH} but conflicts with main in: {FILES}.
First run  git merge --no-edit {OLD_BRANCH}  then  git merge main , resolve the conflicts keeping
both intents, rerun the Done-when commands, and commit.
```

## Messages to a live agent (SendMessage)

**Answer**
```
Hernán answered your question: {ANSWER}
Continue the task and end with the final message format.
```

**Conflict**
```
Integration found conflicts between your branch and main in: {FILES}.
In your worktree run  git merge main , resolve the conflicts keeping both intents, rerun the
Done-when commands, commit, and end with the final message format.
```
