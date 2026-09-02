# model-search

## What it does

Finds the right biological foundation model from the Helmholtz Munich model zoo: DinoBloom,
Hyformer, ProtTrans and MolE.

## When to use / when not

Use when choosing a model for a task — listing models, comparing modalities, or deciding which
checkpoint fits your data.

For running embeddings after you have chosen a model, see [model-embed](./model-embed.md).

## Install

```bash
npx skills add git@github.com:HelmholtzAI-Consultants-Munich/virtual_human_chc.git --skill model-search
```

## Access

Helmholtz — requires access to the
[vhmodels](https://github.com/HelmholtzAI-Consultants-Munich/vhmodels)
repository (GitHub login with permission). The clone URL may still be
`virtual_human_chc`.

## Install in Claude Science

**Skills → Add skill → Import from GitHub**, then paste (needs repository access):

```
https://github.com/HelmholtzAI-Consultants-Munich/vhmodels
```

## Source

- [vhmodels](https://github.com/HelmholtzAI-Consultants-Munich/vhmodels)
- Skill path: `skills/model-search/`
