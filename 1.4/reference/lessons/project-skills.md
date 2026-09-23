---
description: "Lesson: project-scoped skills — discovery, priority, creation. version: 1.4"
---
# Lesson: project-scoped skills
## How Letta discovers skills
The harness scans four sources in descending priority. On ID collision,
the higher-priority source wins:
| Priority | Source | Path |
|---|---|---|
| 1 (highest) | Project | `<cwd>/.agents/skills/` |
| 2 | Agent | `$MEMORY_DIR/skills/` |
| 3 | Computer | `~/.letta/skills/` |
| 4 (lowest) | Bundled | inside Letta Code |
List available skills — `/skills` command.
## What this means in practice
The same skill can live in multiple places. Project overrides agent,
agent overrides computer, computer overrides bundled.
If a skill exists in `$MEMORY_DIR/skills/` or `~/.letta/skills/` — it is
always available, in any project. Duplicating it into a project is pointless:
it would need to be maintained in two places.
## Creating a project skill
1. **Check for an existing skill with the same name.**
   - `/skills` shows all available skills.
   - If the skill already exists in agent-scoped (`$MEMORY_DIR/skills/`)
     or global-scoped (`~/.letta/skills/`) — it is always available.
     Do not create a duplicate in the project. Report to the user.
   - If the user insists on a project version — warn that there will now
     be two versions: general and project. Project overrides general.
     Suggest deleting the general one if no longer needed.
2. Create folder `<physical_path>\.agents\skills\<name>\`.
3. Create `SKILL.md` with frontmatter (`name`, `description`).
4. Ensure dialogue CWD = project `physical_path` — the skill will be picked
   up on the next turn.
5. In `projects/<name>/skills.md` add a line with the skill name and
   the marker "project-scoped".
## Limitations
- not managed by Letta — manual file creation only;
- not versioned in MemFS — only in the project git, if any;
- not transferred between machines automatically;
- not visible to other agents;
- works only when dialogue CWD = project folder.