# claude-code-orchestrator

A [Claude Code](https://claude.com/claude-code) skill I wrote to split long pieces of work
across agents without watching every step. You plan a batch of about ten tasks with it, approve
the plan, and it runs the batch on its own: one background agent per task, each in its own git
worktree, merged into the base branch one at a time with the tests in between. It only comes
back to you when the plan ends, a task fails twice or a decision of yours is needed, on Telegram,
where you can answer from your phone.

Start or resume it with `/orchestrator`.

## How it works

1. **Survey and checks.** An `Explore` agent maps the repository (stack, test command, git
   state, ignored files a fresh checkout needs). Then the skill checks that the tests pass on
   the base branch and that a fresh worktree can install and test, before anything runs.
2. **Interview and plan.** A grilling interview, one question at a time, settles about ten
   tasks. Each task has a goal, context, scope (what it may and must not touch), "done when"
   commands with expected results, and its dependencies. The plan is a Markdown file in the
   repo: `plans/NNN-slug.md` ([template](skills/orchestrator/references/plan-template.md)).
   Nothing runs until you approve it.
3. **Run loop.** At most two agents at a time, and only tasks with no dependency path between
   them. The orchestrator never does a task's work itself and only reads each agent's short
   final message, so its own context stays small over a long batch.
4. **Integration.** [`integrate.py`](skills/orchestrator/scripts/integrate.py) squash-merges
   one branch at a time, runs the tests and reverts the merge if they fail, so the base branch
   stays green. Conflicts go back to the agent that wrote the code.
5. **Failures and decisions.** A failed task is retried once with a continuation agent that
   gets the failure. Scope changes, user-visible behaviour the plan does not define and anything
   irreversible or outward-facing are yours to decide; the rest is decided and logged in the
   plan.
6. **Resume.** The plan file is the memory. After a restart, tasks left running are found by
   their worktrees and either integrated, continued or relaunched.

## Guardrails

- [`guard.py`](skills/orchestrator/scripts/guard.py) is a `PreToolUse` hook for the whole
  session, agents included. It blocks `git push`, deploys and publishes, `git reset --hard`,
  `git clean` and recursive `rm` outside the current checkout. Pushing and deploying stay with
  the human.
- Full test output never enters the model's context: the scripts log it and return a short
  JSON line or the tail of a failure.
- [`tg.py`](skills/orchestrator/scripts/tg.py) reads the bot token from a local config file
  outside the repo and never prints it. It only answers messages from the configured chat.

## Design log

[`docs/orchestrator-design.md`](docs/orchestrator-design.md) records the numbered decisions
behind the skill and why each one was taken.
[`docs/prompt-nueva-sesion.md`](docs/prompt-nueva-sesion.md) is the prompt (in Spanish) that
started the design session.

## Status

I use it on my own projects since late September 2026. It is personal: it talks to me in
Spanish and reads my Telegram config from a path on my Mac (or from `$TELEGRAM_CONFIG`). Its
effectiveness is not measured yet, for example how many tasks pass their "done when" checks on
the first attempt.

## Install

```bash
ln -s <path to this repo>/skills/orchestrator ~/.claude/skills/orchestrator
npx skills add mattpocock/skills -g -a claude-code -s grill-me -s grilling -y
```

It needs a Telegram config with `telegram.bot_token` and `telegram.chat_id` (path in
`$TELEGRAM_CONFIG`). Check it with
`python3 ~/.claude/skills/orchestrator/scripts/tg.py check`.
