# dataset-scouting

## What it does

Screen public datasets to check the availability of data and metadata, fit to your criteria, and URL
correctness before downloading them.

## When to use / when not

Use when you need to decide which public datasets are worth acquiring — building a candidate list,
checking download routes, or auditing metadata coverage.

Not for loading, harmonizing or mapping data after you have already chosen a dataset. For graph
construction, see [biocypher](./biocypher.md) or [biotope-croissant](./biotope-croissant.md).

## Install

```bash
npx skills add HelmholtzAI-Consultants-Munich/helmholtz-agent-skills@dataset-scouting
```

## Install in Claude Science

Import `HelmholtzAI-Consultants-Munich/helmholtz-agent-skills` under
**Skills → Add skill → Import from GitHub**.
ZIP fallback: `dataset-scouting.zip` from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest),
**without extracting it first**.
[Walkthrough](../claude-science.md).

## Source

- [SKILL.md](../../plugins/method-skills/skills/dataset-scouting/SKILL.md) in this repository
- [helmholtz-agent-skills](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills)
