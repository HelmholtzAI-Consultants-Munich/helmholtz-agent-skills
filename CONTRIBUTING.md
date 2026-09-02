# Contributing

## Deciding where your skill goes

Answer one question first: what does this skill describe?

- **A tool** — it belongs in that tool's repository, not here. Open a PR there, then add the
  source to [`sources.json`](./sources.json) and, if it should be installable from this
  marketplace, to [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json).
- **A method that no single tool owns** — it belongs under
  `plugins/method-skills/skills/` here.
- **A site**, such as a cluster or an institute service, whose details are internal — it belongs
  behind that site's access boundary. Add it to `sources.json` with `"tier": "gated"` so people
  can see it exists without being able to read it. Do not list it in the public marketplace.

Never copy another repository's skill into `plugins/`. Add it to `sources.json` and the
marketplace instead: this repository holds no second copy of a skill that lives elsewhere. A
skill with no home yet may sit under `plugins/method-skills/skills/` in the meantime, with the
destination recorded in `sources.json`; delete the copy once it lands. If you are unsure where
something belongs, open an issue rather than guessing.

## Writing the skill

A skill is a directory with a `SKILL.md`, plus whatever it needs:

```
my-skill/
├── SKILL.md          # required: frontmatter + instructions
├── references/       # detail the agent loads only when it needs it
├── scripts/          # code the agent runs; its source never enters context
└── agents/
    └── openai.yaml   # Codex display metadata
```

Frontmatter has two required fields:

```yaml
---
name: my-skill
description: What this does, and when an agent should reach for it.
---
```

The `description` is the only part loaded at startup, and what the model matches a request
against. Say what the skill does *and* when to use it; a bare list of trigger words gives the
model nothing to match intent against.

Put the procedure in `SKILL.md` and the detail in `references/`. `SKILL.md` loads in full
whenever the skill fires, while a reference loads only when the instructions send the agent to
it. Everything a skill references must live inside its own directory.

### Format limits

Enforced by `scripts/lint_skills.py`, from
[Anthropic's Agent Skills spec](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):

- `name` — 64 characters or fewer, lowercase letters, numbers and hyphens only, must not contain
  "claude" or "anthropic", and must match its directory name.
- `description` — 1024 characters or fewer, non-empty, no XML tags. `hmgu-hpc` is at 981.
- Relative links in `SKILL.md` must resolve inside the skill.

### Codex metadata

`agents/openai.yaml` gives Codex a display name and one-line summary for its skill picker:

```yaml
interface:
  display_name: "Dataset Scouting"
  short_description: "Screen public datasets before you download them"
```

Add `policy: {allow_implicit_invocation: false}`, paired with `disable-model-invocation: true`
in the frontmatter, only for a skill that should be reachable solely when a human types its
name. Most skills should stay model-invokable.

## Before you open a PR

```bash
python3 scripts/lint_skills.py           # format limits, link integrity, junk files
python3 scripts/verify_marketplace.py    # marketplace.json and local plugin layout
```

Then test the skill by using it: install it locally with `scripts/link-skills.sh`, start a fresh
session, and give it a task it should fire on without naming the skill. If it does not trigger,
fix the `description`.

## Adding a source to the index

Add an entry to [`sources.json`](./sources.json) with its repository, tier, and the skills it
contains. Public catalog entries also go in
[`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json):

- **GitHub plugin** (has `.claude-plugin/plugin.json`, and may ship MCP servers at the plugin
  root) — `github` or `url` pointing at the **repository root**, never a `skills/` subdirectory.
  MCP config lives beside the plugin manifest; a skill-only subdir drop would omit it.
- **Skill-only tree** with no `plugin.json` — `git-subdir` plus `"strict": false`, and list the
  intended skill paths explicitly.

Embargoed and gated sources stay in `sources.json` only. Then add a human docs page at
`docs/<category>/<skill>.md` (install command, access, source link) and one dense bullet in
[README.md](./README.md). Public skills also get an **Install in Claude Science** section with
the full GitHub URL to import (this marketplace, or the upstream plugin repo).

### Listing fields

Each README bullet and docs page should stay scannable:

- **One-line description** — 120 characters or fewer, user-facing (not the agent trigger list from
  `SKILL.md` frontmatter).
- **Access** — omit when public. Restricted skills: a parenthetical on the README line
  (e.g. `(Restricted Access: …)`), and an **Access** section on the docs page.
  Helmholtz covers both `embargoed` and `gated` tiers in `sources.json`.

Install commands live on the skill's docs page, not in the README listing.

| Tier | Meaning |
|---|---|
| `public` | Anyone can clone it. Listed in the public marketplace. |
| `embargoed` | Private while its tool is in early development; goes public with the tool. |
| `gated` | Permanently access-controlled. Not listed in the public marketplace. |

The declared skill list must match what the source actually holds;
`scripts/verify_marketplace.py` checks local plugins. For a repository that does not exist yet,
set `"pending"` with the reason: it shows in the index and is omitted from the marketplace.

## Landing changes

`main` is protected: land changes through a pull request. Coding harnesses and Claude Science
both install from git, so a merge is enough; there is no ZIP release to tag.

## Install instructions

Global install routes live in [README.md](./README.md) and
[docs/claude-science.md](./docs/claude-science.md). Per-skill `npx` commands and Science notes
live on each skill's docs page.
