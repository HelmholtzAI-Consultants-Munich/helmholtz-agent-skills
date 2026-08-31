# Contributing

## Deciding where your skill goes

Answer one question first: what does this skill describe?

- **A tool** — it belongs in that tool's repository, not here. Open a PR there, then add the
  source to [`sources.json`](./sources.json) so it appears in the index.
- **A method that no single tool owns** — it belongs in `skills/` here.
- **A site**, such as a cluster or an institute service, whose details are internal — it belongs
  behind that site's access boundary. Add it to `sources.json` with `"tier": "gated"` so people
  can see it exists without being able to read it.

Never copy another repository's skill into `skills/`. Add it to `sources.json` instead: this
repository holds no second copy of a skill that lives elsewhere. A skill with no home yet may
sit here in the meantime, with the destination recorded in `sources.json`; delete the copy once
it lands. If you are unsure where something belongs, open an issue rather than guessing.

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
it. Everything a skill references must live inside its own directory, since it ships as a
self-contained ZIP.

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
python3 scripts/build_zips.py            # the release build, end to end
```

The build refuses to package anything the linter rejects.

Then test the skill by using it: install it locally with `scripts/link-skills.sh`, start a fresh
session, and give it a task it should fire on without naming the skill. If it does not trigger,
fix the `description`.

## Adding a source to the index

Add an entry to [`sources.json`](./sources.json) with its repository, tier, and the skills it
contains, then add a row to the README table.

| Tier | Meaning |
|---|---|
| `public` | Anyone can clone it. Built into the release. |
| `embargoed` | Private while its tool is in early development; goes public with the tool. |
| `gated` | Permanently access-controlled. Never appears in a public artifact. |

The declared skill list must match what the source actually holds; the build fails if they
disagree. For a repository that does not exist yet, set `"pending"` with the reason: it shows in
the index and is skipped by the build.

`build_zips.py` builds `public` sources only, and refuses to package one containing gated
markers (`scidom.de`, `hpc-submit`, `ascgitlab`, `digit-hpc@`, `/lustre/groups`). If that check
fires, remove the content or move the skill to the gated tier. Do not disable the check.

## Install instructions

Install commands live in `README.md` and nowhere else. Link to it from other documents rather
than repeating the commands, so there is only ever one copy to keep correct.
