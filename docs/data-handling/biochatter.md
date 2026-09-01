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

Download `biochatter.zip` from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest).
In **Customize → Skills**, add it **without extracting it first**.
[Walkthrough](../claude-science.md).

## Source

- [biotope/skills/biochatter](https://github.com/biocypher/biotope/tree/main/skills/biochatter)
- [biocypher/biotope](https://github.com/biocypher/biotope)
