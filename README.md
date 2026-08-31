# Advanced Agentic Skills for Science

Agent skills for computational biology, built at the Institute of Computational Biology,
Helmholtz Munich.

They use the open [Agent Skills](https://agentskills.io) format, so they work in Claude Code,
Cursor, Codex, Copilot, Gemini CLI, and anything else that reads `SKILL.md`, as well as in
Claude Science.

## Install

We suggest using `npx skills` [(see official docs)](https://github.com/vercel-labs/skills).

### Coding harnesses: Claude Code, Cursor, Codex, etc.

Each source installs on its own. Take the ones you want:

```bash
npx skills add HelmholtzAI-Consultants-Munich/advanced-science-skills
npx skills add biocypher/biotope
```

The installer asks which skills to take and which agents to install them into, writes them to
`.agents/skills/`, and symlinks them into every harness it detects. Add `-g` to install for your
user rather than the current project, and run `npx skills update` to refresh them later.

### Claude Science and claude.ai

Claude Science cannot install from git. Download the ZIPs from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/advanced-science-skills/releases/latest),
then in **Customize → Skills** add each one **without extracting it first**. One ZIP is one skill.

Full walkthrough: [docs/claude-science.md](./docs/claude-science.md).

### Access-controlled skills

Same command, against the repository that holds them. `npx skills` authenticates through your
existing git credential helper, `gh`, or SSH key; without access, the clone fails.

```bash
npx skills add git@github.com:HelmholtzAI-Consultants-Munich/virtual_human_chc.git
DISABLE_TELEMETRY=1 npx skills add git@ascgitlab.helmholtz-munich.de:vladislav.samoilov/hmgu-hpc-skill.git
```

## The skills

### Data handling

| Skill | What it does | Lives in | Install |
|---|---|---|---|
| `dataset-scouting` | Screen public datasets before you download them: verify what metadata and raw data a study exposes, and record it as a sourced datasheet. | [here](./skills/dataset-scouting/SKILL.md) | `npx skills add HelmholtzAI-Consultants-Munich/advanced-science-skills@dataset-scouting` |
| `biotope-croissant` | Scans you messy data folder, maps all files, types, and fields inside them. Creates a standartized (croissan standard) map of all your data for easy mapping, agent-use, or audit. | [biocypher/biotope](https://github.com/biocypher/biotope) | `npx skills add biocypher/biotope@biotope-croissant` |
| `biocypher` | Build knowledge graphs with BioCypher: adapters, schema config, multi-backend export. | [biocypher/biotope](https://github.com/biocypher/biotope) | `npx skills add biocypher/biotope@biocypher` |
| `biochatter` | Query knowledge graphs, APIs and documents in natural language. | [biocypher/biotope](https://github.com/biocypher/biotope) | `npx skills add biocypher/biotope@biochatter` |

### Foundational AI Models for Biology

| Skill | What it does | Lives in | Install |
|---|---|---|---|
| `model-search` | Pick a model from the Helmholtz Munich zoo: DinoBloom, Hyformer, ProtTrans, MolE. | [virtual_human_chc](https://github.com/HelmholtzAI-Consultants-Munich/virtual_human_chc), *access required* | `npx skills add git@github.com:HelmholtzAI-Consultants-Munich/virtual_human_chc.git --skill model-search` |
| `model-embed` | Run those models: embeddings, Conda/Apptainer runtimes. | [virtual_human_chc](https://github.com/HelmholtzAI-Consultants-Munich/virtual_human_chc), *access required* | `npx skills add git@github.com:HelmholtzAI-Consultants-Munich/virtual_human_chc.git --skill model-embed` |

### Biological workflows

| Skill | What it does | Lives in | Install |
|---|---|---|---|
| `pureclip-optimization` | Choose PureCLIP parameters on evidence, and judge whether the resulting crosslink calls are credible. | [here](./skills/pureclip-optimization/SKILL.md), until the PureCLIP maintainers' repo is settled | `npx skills add HelmholtzAI-Consultants-Munich/advanced-science-skills@pureclip-optimization` |

### HPC cluster use

| Skill | What it does | Lives in | Install |
|---|---|---|---|
| `hmgu-hpc` | The HMGU SLURM cluster: getting access, storage layout, partitions and QoS, GPU etiquette, why your job is stuck. | [HMGU GitLab](https://ascgitlab.helmholtz-muenchen.de/vladislav.samoilov/hmgu-hpc-skill), *Helmholtz login required* | `DISABLE_TELEMETRY=1 npx skills add git@ascgitlab.helmholtz-munich.de:vladislav.samoilov/hmgu-hpc-skill.git` |

## Recommended third-party skills

| Skill | Source | License | Install |
|---|---|---|---|
| `scanpy-scrna-seq` | [SciAgent-Skills](https://github.com/jaechang-hits/SciAgent-Skills/tree/main/skills/genomics-bioinformatics/single-cell) | CC-BY-4.0 | `npx skills add jaechang-hits/SciAgent-Skills@scanpy-scrna-seq` |
| `nextflow-workflow-engine` | [SciAgent-Skills](https://github.com/jaechang-hits/SciAgent-Skills/tree/main/skills/scientific-computing) | Apache-2.0 | `npx skills add jaechang-hits/SciAgent-Skills@nextflow-workflow-engine` |

## Contributing

[CONTRIBUTING.md](./CONTRIBUTING.md) covers writing a skill, the format limits, and how to add a
source to the index.

## License
[Apache-2.0](./LICENSE); only applies to not access-restricted skills.
