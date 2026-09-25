# Orchestrator skill — design decisions

Running log of the grilling session with Hernán (started 2026-09-25).
The old `~/.claude/skills/orquestador` is not the base; this is a rewrite.
Skill, files and names in English; conversation in Spanish.

## Decisions

1. **Autonomy.** The orchestrator chains every task in the plan without stopping. It comes back to Hernán only when the whole plan is done, or earlier if a task fails or needs a decision from him.
2. **Plan changes while running.** It may adjust the plan (reorder tasks, split a task that turned out too big, add a small task to fix something a previous task broke). It may not add new scope: new-scope tasks are proposed at the end.
3. **Blocked task.** It keeps going with whatever does not depend on the blocked task, and sends Hernán a Telegram message saying which session needs him and what answer it needs.
4. **Answering from Telegram.** Hernán can reply on Telegram and the reply reaches the orchestrator session. Mechanism: our own script on the existing bot (a background process waits for his reply and wakes the session). Not the official Channels plugin (needs `--channels` from the CLI, preview).
5. **How a task runs.** Always as a background agent, so it never spends orchestrator context: only its final summary comes back. Where it works is decided by the orchestrator at launch (the agent cannot change it later): in the main checkout when the task runs alone (fast, has everything git ignores); in its own worktree only when it runs in parallel with another task. *Changed by 22.*
6. **Parallelism.** At most 2 tasks at a time. When we build the plan together we mark which tasks depend on which; the orchestrator only runs in parallel what the plan marks as independent.
7. **Integration.** The orchestrator merges each worktree branch into main, one at a time, and removes the worktree. On a conflict it launches a small agent that resolves it in the main checkout and runs the tests; if that agent cannot, Hernán is notified. *Amended by 35.*
8. **Verification.** Every task in the plan carries its own "done when" with concrete commands. The agent runs them and reports the results; after integrating, the orchestrator runs the test suite again. No independent reviewer by default.
9. **Memory.** One plan file in the repo (e.g. `plans/<name>.md`) with the task list, each task's status and the decisions. The orchestrator updates and commits it after every task. A new orchestrator resumes by reading that file.
10. **Planning.** Hernán builds the plan together with the orchestrator: the orchestrator interviews him grill-me style (one question at a time, with a recommendation) until there is a solid plan for about the next 10 tasks. Nothing runs until he approves it.
11. **Interview tool.** The orchestrator uses `/grill-me`, which calls `grilling` (both from mattpocock/skills). `grilling` was missing and was installed on 2026-09-25 into `.agents/skills/grilling`, linked from `.claude/skills/grilling`. *Corrected by 19.*
12. **Location and install.** The source lives in this folder (`homemadeSkills`) under git, with no remote for now; a private GitHub remote is added later only if Hernán asks. The skill is `skills/orchestrator/`, linked from `~/.claude/skills/orchestrator`. `grill-me` and `grilling` are installed globally with `npx skills` (on 2026-09-25 it copied them straight into `~/.claude/skills`).
13. **Name and invocation.** The skill is named `orchestrator`. It starts only when Hernán types `/orchestrator` (`disable-model-invocation: true`). If it finds a plan with pending tasks, it offers to resume it; otherwise it starts the planning interview.
14. **Task fields.** Each task in the plan has an id and a title, plus these fields: Status (pending | running | done | blocked | failed), Depends on, Goal, Context (what the agent must read first), Scope (what it may and may not touch), Done when (concrete commands and expected result) and Outcome (filled in by the orchestrator: one line and the commit). The agent's prompt is that block plus a fixed preamble from the skill; no separate prompt is written.
15. **Agent hand-back.** The agent commits its own work as `T03: <title>` and never pushes. It ends with a fixed-format final message of about 20 lines at most:
    - STATUS: done, failed or blocked
    - COMMITS
    - DONE WHEN: the result of each command
    - DECISIONS: the ones it made alone
    - QUESTION: only if blocked
    - OUT OF SCOPE: things it noticed but did not do

    There is no report file: the plan keeps the summary and Claude Code keeps the agent's transcript.
16. **Who decides.** The orchestrator (or the agent) decides anything reversible within the plan's scope and records it in the plan. Hernán decides three kinds of things:
    - new scope;
    - user-visible behavior the plan does not define (copy, flows, design);
    - anything irreversible or outward-facing: push, deploy, migrations on real data, deleting data, sending emails, spending money, creating accounts, tokens and secrets.

    A task that fails its "done when" gets one retry with a fresh agent that receives the first failure. If it fails again, it is marked `failed` and Hernán is notified.
17. **When Telegram fires.** Always and at once, in three cases: a decision from Hernán is needed, a task failed, or the plan finished. It does not fire for each finished task. The first answer to arrive wins, on screen or on Telegram; an answer on screen cancels the wait for Telegram.
18. **End-of-plan delivery.** In the session:
    - one line per task (status and commit);
    - the final test-suite result;
    - decisions the orchestrator made alone (for review);
    - what stayed blocked and why;
    - new-scope proposals;
    - what to try by hand;
    - the next step: push or deploy if Hernán wants, then plan the next batch.

    On Telegram, a 3-line summary. The plan file is updated and committed.
19. **Interview tool (corrects 11).** `grill-me` has `disable-model-invocation: true`, so the model cannot invoke it. The orchestrator invokes `grilling` directly, and `/grill-me` stays as Hernán's manual shortcut.
20. **Language inside projects.** Plan files, agent prompts and commit messages are written in English. Everything addressed to Hernán (the interview, messages in the session, Telegram) is in Spanish.
21. **Old-method projects.** The skill has no migration logic. Once the new skill is finished, Hernán stops the old-method work and tries the new skill in kinelab, yazmina-people and andrevallenails himself. The old `~/.claude/skills/orquestador` is his to handle.
22. **Every task runs in a worktree (changes 5).** Every task works in its own worktree, even when it runs alone; the main checkout belongs to the orchestrator (plan updates, merges, post-merge tests). A blocked task waits in its worktree without leaving half-done work in main. The cost is preparing each worktree's environment.
23. **Worktree base (local).** By default Claude Code branches subagent worktrees from the remote's default branch (`worktree.baseRef: "fresh"`). The orchestrator commits but never pushes, so later tasks would miss earlier ones. On its first run in a project, the orchestrator adds `"worktree": {"baseRef": "head"}` to that project's `.claude/settings.json`, after Hernán's OK. Worktrees then branch from the local main.
24. **Worktree environment.** The project's `.worktreeinclude` lists the git-ignored env and secret files; Claude Code copies them into each new worktree. The plan header has a `Worktree setup` command (for example `npm ci` or `uv sync`) that the agent runs first. Heavy data and models are read from the main checkout by absolute path, never symlinked. The old method saw a symlinked `.venv` get committed, and `git worktree remove` then emptied the real one.
25. **Plan files.** Each batch has its own `plans/NNN-slug.md`, and only one is active; finished plans stay as history. The header holds Status, Goal, Test command and Worktree setup, followed by a Decisions section and a Tasks section. Task ids continue across batches (T01–T10, then T11–T20), so a Txx in a commit is unique.
26. **Resuming a blocked task.** The orchestrator sends Hernán's answer to the same agent (SendMessage), which continues in its worktree with its context. If that is not possible (for example, after the session restarted), a fresh agent continues the blocked task's worktree or branch. It receives the task, the previous agent's summary and the answer.
27. **Scope: local first.** v1 runs only on Hernán's Mac. Running in the cloud (orchestrator and agents in a Claude Code cloud session) is v2, to try once v1 works in his projects. v1 keeps the door open: scripts ship inside the skill, and configuration comes from environment variables. Facts gathered on 2026-09-25 for v2:
    - A cloud session clones from GitHub and can push only to `claude/*` branches. It would end with a branch and a PR, not local commits.
    - Cloud sessions do not see `~/.claude/skills`. The skills would have to be synced from claude.ai or committed in each repo.
    - `api.telegram.org` must be added to the environment's allowed domains, and the bot token goes into the environment's variables.
    - Git-ignored files are not there, so each environment needs a setup script.
    - It is undocumented whether a cloud session can wait hours for a reply, and whether a background command can wake it.
    - Hernán can open and answer a cloud session from the Claude app on his phone, which might replace reading replies from Telegram.
28. **Agent preamble.** Every agent gets this fixed preamble with its task block:
    ```
    You are running task T04 of plans/002-billing.md.
    - Work only inside this worktree. Run "Worktree setup" first.
    - Stay within Scope; anything else goes under OUT OF SCOPE.
    - Make reversible choices yourself; list them under DECISIONS.
    - Stop with STATUS: blocked + QUESTION (options + your recommendation) if you need
      new scope, user-visible behavior the task does not define, anything irreversible
      or outward-facing, or a permission that was denied.
    - Judge each Done-when command by exit code and counts, never by the word "passed".
    - Before finishing: commit everything as "T04: <title>"; git status must be clean.
    - Never push. Never rename the session.
    - End with the fixed-format message.
    ```
29. **Integration.** Each task lands on main as a single squash commit `T04: <title>`. If the Test command fails on main after the merge, the orchestrator reverts that commit, so main stays green and new worktrees do not inherit the breakage. The task then gets its retry (16) with the failure output.
30. **Startup checks.** Before launching the first task, while Hernán is still there for the interview, the orchestrator checks:
    - main is checked out and clean;
    - `.claude/worktrees/` is in `.gitignore`;
    - `baseRef` is `head` (23);
    - `.worktreeinclude` exists, and if not, it proposes what to copy;
    - the Test command passes on main. If it fails, it tells Hernán before he approves the plan; otherwise it could not tell later which task broke what.
31. **Routing Telegram replies.** Every notice starts with `[project]` (see 38), and Hernán answers with Telegram's Reply on that message. Sessions that are waiting take turns reading the bot through a lock. Each reply goes to the session that owns the message it replies to. A loose message (not a Reply) goes to the only pending question; if several are pending, the bot asks him to use Reply. There is no permanent process.
32. **Telegram credentials.** They are read from `/Users/heralc/Desktop/HDDev/H-VOICE-CREEATOR/config.json` (section `telegram`: `bot_token`, `chat_id`), and `TELEGRAM_CONFIG` can override the path. The token is never printed or copied elsewhere.
33. **Permission mode.** The orchestrator session runs in `bypassPermissions`, and its agents inherit it. Claude Code's worktree isolation still stops agents from touching the main checkout; that check cannot be turned off.
34. **Orphans on resume.** When `/orchestrator` resumes a plan with tasks still marked `running`, it inspects each one's worktree:
    - committed and clean: it verifies the Done-when commands and integrates the task;
    - half-done: a fresh agent continues there;
    - empty: the task is relaunched from scratch.

    It shows Hernán what it found before continuing.
35. **Merge conflicts (amends 7).** Conflicts are resolved in the task's worktree, not in main. An agent merges main into the task branch there, resolves the conflict, reruns the Done-when commands and commits; the squash then lands cleanly. Main is never left mid-merge. If the agent cannot resolve it, Hernán is notified.
36. **Task size.** A task is a whole feature, a complex change or a sector of the app, not a small step. The orchestrator splits a task (2) only when it turns out bigger than that.
37. **Safety net.** A hook that is active only while the orchestrator runs rejects `git push`, deploys (`vercel`, `supabase db push`…), `git reset --hard`, `git clean` and `rm -rf` outside the worktree. Hernán's normal sessions are unaffected.
38. **Telegram message content.** A message carries:
    - the project tag `[project]`;
    - the question;
    - the answer options, with the recommended one marked and a one-line reason;
    - the link (39).

    It does not name the task or say what continues meanwhile. The reply is routed by Telegram's Reply (31), not by the tag. A failure message states what failed and offers retry, skip or a free instruction, with a recommendation. The end-of-plan message is the 3-line summary (18).
39. **Session link.** At startup the orchestrator turns on Remote Control for its own session, so the session appears on claude.ai/code and in the Claude mobile app. Every message carries the session's title and a link to `https://claude.ai/code`, where the session sits at the top. Hernán can answer on Telegram or in the app, and the first answer wins (17). A session can only get a `claude://` link to itself, which Telegram cannot tap and phones cannot open. The Remote Control tool never returns the direct https address.
40. **Agents' own subagents.** An agent may launch read-only subagents to explore and research without filling its context. Only the agent itself edits, in its worktree.
41. **Project context for the interview.** Before interviewing, the orchestrator launches a read-only explorer agent that summarizes the project: stack, structure, test and setup commands, git state and previous plans. The interview starts from that summary, so the orchestrator does not spend its context reading the repo.
42. **Watchdog.** If an agent has been running for more than 3 hours, the orchestrator notifies Hernán on Telegram and does not kill it. If a question has gone 4 hours without an answer and everything else is stalled, it reminds him once.
43. **Testing the skill.** Before Hernán uses it in his projects, the skill runs end to end on a throwaway repo in the scratchpad. The plan has 3 or 4 small tasks:
    - two that run in parallel;
    - one that fails and is retried;
    - one that blocks and asks on Telegram. Claude warns Hernán before sending, and he answers from his phone.

    What breaks gets fixed, and then Hernán tries it himself.
44. **Local copies of the interview skills.** Once `grill-me` and `grilling` are installed globally (12), the copies in this folder are deleted: `.agents/skills/`, their links in `.claude/skills/` and `skills-lock.json`. That way they do not show up twice when working here.
45. **Safeguards carried over from the old method's measured pitfalls.** Hernán asked for Claude's recommendation, and Claude recommended all four:
    - The agent preamble tells agents that Context may be stale and must be checked against the code.
    - Tests assert against the source that changes, not against hand-written counts or dates.
    - In Python projects with an editable install, `PYTHONPATH` points at the worktree.
    - At startup, a probe agent in a fresh worktree runs the Worktree setup and the test command before the plan is approved.
46. **Attachments on Telegram.** A blocked agent can save a picture or file in its worktree and list it as `ATTACH: <path>` in QUESTION. The orchestrator sends it after the question, as a reply to it: images as photos, anything else as documents. Replying to an attachment also answers the question.
47. **Mechanics added while building.** None of these changes a decision:
    - the hand-back also carries `BRANCH` and `WORKTREE`;
    - an unfinished agent commits `T04: WIP`, so a continuation agent can pick it up;
    - a `skipped` status covers "saltear";
    - a `Log` section in the plan keeps agent ids and branches for resuming;
    - interview rounds use AskUserQuestion popups;
    - the guard hook lives in the skill's frontmatter, so it is active only in the orchestrator's session and its agents.
48. **Agents fast-forward first (fixes 23 in practice).** In the end-to-end test on 2026-09-26, `baseRef: head` did not take effect: `.claude/settings.json` was created with the session already open, so worktrees came from `origin/main`.
    - Every agent's first step is `git merge --ff-only <base branch>`. It is a no-op when `baseRef` works and a fix when it does not.
    - The startup probe agent also reports its HEAD after the fast-forward, and it must equal main's HEAD.
49. **Attachments live outside the repo (amends 46).** In the test, the agent committed the attached file to its branch, outside its Scope, because the preamble says to commit everything. Attachments now go to `/tmp/orchestrator-attach/<repo>-<task>/`, and `ATTACH:` lines carry absolute paths. Agents never edit `plans/`.
50. **Global: start from any folder.** Hernán wants to use `/orchestrator` from any project or folder. The target repo is the one he names, or else the session folder's repo.
    - If the target differs from the session folder, the orchestrator moves the session with the app's `change_directory` tool. The move takes effect when the turn ends, so no agent launches in that turn.
    - Without that tool (CLI), it asks Hernán to reopen the session in the target repo.
    - A folder without git gets an offer of `git init`.
51. **Fewer plan commits (amends 9).** The test left 15 plan commits for 4 tasks. The plan is still saved to disk on every change, but it is committed only at approval, when a task ends (`done`, `failed` after its retry, `skipped`) and at the end. `integrate.py --ignore` lets the modified plan file sit unstaged while squash-merging.
