# hmgu-hpc

## What it does

Helps you work with the Helmholtz Munich HMGU SLURM cluster: getting access, storage layout,
partitions and QoS, GPU etiquette, and debugging stuck jobs.

## When to use / when not

Use when the task involves the HMGU cluster — scidom.de, hpc-submit, `/lustre/groups`, job
submission, notebooks on cluster compute, or onboarding new group members.

Not a substitute for generic SLURM documentation. This skill covers institute-specific conventions
that are invisible from the outside.

## Install

```bash
DISABLE_TELEMETRY=1 npx skills add git@ascgitlab.helmholtz-munich.de:vladislav.samoilov/hmgu-hpc-skill.git
```

## Access

Helmholtz — requires Helmholtz GitLab login with access to the
[hmgu-hpc-skill](https://ascgitlab.helmholtz-munich.de/vladislav.samoilov/hmgu-hpc-skill)
repository.

## Source

- [hmgu-hpc-skill](https://ascgitlab.helmholtz-munich.de/vladislav.samoilov/hmgu-hpc-skill)
- For Claude Science upload: download `dist/hmgu-hpc.zip` from that repository
