---
description: "Lesson: YAML frontmatter — allowed keys, version in description. version: 1.5"
---
# Lesson: YAML frontmatter
## Allowed keys in memory files
Letta harness accepts only three keys in frontmatter of memory files:
- `description` — required, non-empty string
- `read_only` — optional
- `limit` — optional
Any other key — `version`, `status`, `last_updated`, `author` — is rejected
with an error. This applies to all memory files, not only to `system/`.
## Where to put version
Version goes inside `description`, wrapped in double quotes:
    ---
    description: "Lesson: memory and agents. version: 1.5"
    ---
## Colon in description
If `description` contains a colon followed by a space (`: `), YAML parses it
as a nested key and fails. Wrap the whole value in double quotes.
Check before commit: if description has `: ` — quotes are mandatory.
## Double quotes inside description
If the value is wrapped in double quotes, a straight double quote inside it
(`"нет интернета"`) closes the string and breaks YAML. Use guillemets or
single quotes for inner quotes:
    ---
    description: "Сеть и DNS — диагностика «нет интернета». version: 1.5"
    ---
Before commit — check every new description for inner straight double
quotes; guillemets «» are the safe choice for Russian text.
## Double dot
Make sure there is exactly one dot before ` version:`. Common script bug
produces `.. version: 1.5`.