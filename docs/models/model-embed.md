# model-embed

## What it does

Runs VH CHC model embeddings via isolated Conda or Apptainer runtimes. Covers DinoBloom,
Hyformer, ProtTrans and MolE.

## When to use / when not

Use when embedding images, proteins, peptides or molecules, or setting up model runtimes.

For choosing which model to use first, see [model-search](./model-search.md).

## Install

```bash
npx skills add git@github.com:HelmholtzAI-Consultants-Munich/virtual_human_chc.git --skill model-embed
```

## Access

Helmholtz — requires access to the
[vhmodels](https://github.com/HelmholtzAI-Consultants-Munich/vhmodels)
repository (GitHub login with permission). The clone URL may still be
`virtual_human_chc`.

## Install in Claude Science

Import `HelmholtzAI-Consultants-Munich/vhmodels` under
**Skills → Add skill → Import from GitHub** (needs repository access).
ZIP fallback: build from a clone you can access, as
[docs/claude-science.md](../claude-science.md) describes.

## Source

- [vhmodels](https://github.com/HelmholtzAI-Consultants-Munich/vhmodels)
- Skill path: `skills/model-embed/`
