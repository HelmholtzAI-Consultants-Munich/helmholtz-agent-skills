# biochatter

## What it does

Connects biomedical LLM chat to knowledge graphs, APIs and document RAG. Query graphs and
structured backends in natural language.

## When to use / when not

Use when you have a knowledge graph, API or document collection and want conversational access.

Does not build graphs — that is [biocypher](./biocypher.md) or the biotope pipeline via
[biotope-croissant](./biotope-croissant.md).

## Install

```bash
npx skills add biocypher/biotope@biochatter
```

## Install in Claude Science

Import `HelmholtzAI-Consultants-Munich/helmholtz-agent-skills` under
**Skills → Add skill → Import from GitHub**.
ZIP fallback: `biochatter.zip` from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest),
**without extracting it first**.
[Walkthrough](../claude-science.md).

## Source

- [biotope/skills/biochatter](https://github.com/biocypher/biotope/tree/main/skills/biochatter)
- [biocypher/biotope](https://github.com/biocypher/biotope)
