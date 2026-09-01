# biotope-croissant

## What it does

Map a messy data folder into a standardized Croissant catalog of files, types and fields. Useful to
making the data accessible to agents and building data harmonization loaders.

## When to use / when not

Use when you need to understand what is in a data directory before building a knowledge graph or
handing data to an agent.

For the full biotope pipeline — init, add, map, build — and Croissant-to-graph conversion, see
[biocypher](./biocypher.md). For querying an existing graph, see [biochatter](./biochatter.md).

## Install

```bash
npx skills add biocypher/biotope@biotope-croissant
```

## Install in Claude Science

Download `biotope-croissant.zip` from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest).
In **Customize → Skills**, add it **without extracting it first**.
[Walkthrough](../claude-science.md).

## Source

- [biotope/skills/biotope-croissant](https://github.com/biocypher/biotope/tree/main/skills/biotope-croissant)
- [biocypher/biotope](https://github.com/biocypher/biotope)
