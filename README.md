# homemadeSkills

Hernán's own Claude Code skills, under git.

| Skill | What it does |
|---|---|
| `skills/orchestrator` | Plan ~10 large tasks with a grilling interview, then run them unattended as background agents in worktrees; Telegram when something needs Hernán. Start with `/orchestrator`. |

Design log: `docs/orchestrator-design.md` (numbered decisions).

## Install

```bash
ln -s ~/Desktop/HDDev/homemadeSkills/skills/orchestrator ~/.claude/skills/orchestrator
npx skills add mattpocock/skills -g -a claude-code -s grill-me -s grilling -y
```

The orchestrator also needs the Telegram config at
`~/Desktop/HDDev/H-VOICE-CREEATOR/config.json` (or `$TELEGRAM_CONFIG`); check it with
`python3 ~/.claude/skills/orchestrator/scripts/tg.py check`.
