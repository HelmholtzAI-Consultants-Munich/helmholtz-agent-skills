# biocypher

## What it does

Build biomedical knowledge graphs with BioCypher adapters, schema config and multi-backend export.

## When to use / when not

Use for standalone KG ETL pipelines, schema design, or graph database export.

For cataloging raw files before mapping, start with [biotope-croissant](./biotope-croissant.md).
For natural-language queries over a built graph, see [biochatter](./biochatter.md).

## Install

```bash
npx skills add biocypher/biotope@biocypher
```

## Install in Claude Science

Import `HelmholtzAI-Consultants-Munich/helmholtz-agent-skills` under
**Skills → Add skill → Import from GitHub**.
ZIP fallback: `biocypher.zip` from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest),
**without extracting it first**.
[Walkthrough](../claude-science.md).

## Source

- [biotope/skills/biocypher](https://github.com/biocypher/biotope/tree/main/skills/biocypher)
- [biocypher/biotope](https://github.com/biocypher/biotope)
