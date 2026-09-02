# pureclip-optimization

## What it does

Choose optimal PureCLIP parameters for protein-RNA binding sites extraction from eCLIP data.

## When to use / when not

Use for eCLIP, iCLIP or PAR-CLIP data when you need evidence-based parameter tuning and a reviewable
report — not a black-box peak call.

Hosted here temporarily until the PureCLIP maintainers' repository is settled.

## Install

```bash
npx skills add HelmholtzAI-Consultants-Munich/helmholtz-agent-skills@pureclip-optimization
```

## Install in Claude Science

Import `HelmholtzAI-Consultants-Munich/helmholtz-agent-skills` under
**Skills → Add skill → Import from GitHub**.
ZIP fallback: `pureclip-optimization.zip` from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest),
**without extracting it first**.
[Walkthrough](../claude-science.md).

## Source

- [SKILL.md](../../plugins/method-skills/skills/pureclip-optimization/SKILL.md) in this repository
- [helmholtz-agent-skills](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills)
