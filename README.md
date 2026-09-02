# Advanced Agentic Skills for Science

Agent skills for scientific work across Helmholtz, started at the Institute of
Computational Biology, Helmholtz Munich. Work in Claude Code,
Cursor, Codex, Copilot, Gemini CLI, and anything else that reads `SKILL.md`

## Skills

#### Data handling

**[dataset-scouting](./docs/data-handling/dataset-scouting.md)** — Screen public datasets to check the availability of data and metadata, fit to your criteria, and URL correctness before downloading them.

**[biotope-croissant](./docs/data-handling/biotope-croissant.md)** — Map a messy data folder into a standardized Croissant catalog of files, types and fields. Useful to making the data accessible to agents and building data harmonization loaders.

**[biocypher](./docs/data-handling/biocypher.md)** — Build biomedical knowledge graphs with BioCypher adapters, schema config and multi-backend export.

#### Foundational AI models for biology

**[model-search](./docs/models/model-search.md)** — Find the right biological foundation model from the Helmholtz's Virtual Humans model collection. (🔒 Restricted Access: beta version, request access)

**[model-embed](./docs/models/model-embed.md)** — Have the agent properly load and run those models: Conda env setup, inference, and Apptainer runtimes. (🔒 Restricted Access: beta version, request access)

#### Biological workflows

**[pureclip-optimization](./docs/biological-workflows/pureclip-optimization.md)** — Choose optimal PureCLIP parameters for protein-RNA binding sites extraction from eCLIP data.

#### HPC cluster use

**[hmgu-hpc](./docs/hpc/hmgu-hpc.md)** — Have agent reliably use the HMGU HPC cluster: access, storage, partitions, GPU etiquette, job dispatch and debugging. (🔒 Restricted Access: Helmholtz Munich SSO)

#### Recommended third-party skills

**[grilling](./docs/third-party/grilling.md)** — Interview the user relentlessly about a plan until every branch of the design tree is resolved.

**[scanpy-scrna-seq](./docs/third-party/scanpy-scrna-seq.md)** — Single-cell RNA-seq analysis with Scanpy.

**[nextflow-workflow-engine](./docs/third-party/nextflow-workflow-engine.md)** — Scalable bioinformatics workflows with Nextflow and nf-core.

## Install

### Coding harnesses: Claude Code, Cursor, Codex, etc.

This repository is a plugin marketplace ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)).
Claude Code and Codex can add it and install plugins separately:

```bash
claude plugin marketplace add https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
claude plugin install method-skills@helmholtz-agent-skills
```

Adding the marketplace does not install every plugin. Public GitHub plugins such as `biotope`
are fetched from their upstream repositories; skill-only third-party entries use a subdirectory
of their source repo.

For Cursor and other `SKILL.md` harnesses, use `npx skills` [(see official docs)](https://github.com/vercel-labs/skills).
The installer asks which skills to take and which agents to install them into. Add `-g` to
install globally rather than the current project, and run `npx skills update` to refresh them later.

`npx skills` only resolves local marketplace paths, so it installs this repo's method skills.
Add other sources the same way:

```bash
npx skills add <source>@<skill>
```

Examples:

```bash
npx skills add HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
npx skills add biocypher/biotope
```

Open any skill above for its exact install command.

### Claude Science and Claude Web App

**Skills → Add skill → Import from GitHub**, then paste the repository URL:

```
https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
```

Preview and install the plugins you want. For a single upstream plugin, paste that repo's URL
instead (for example `https://github.com/biocypher/biotope`).

Full walkthrough: [docs/claude-science.md](./docs/claude-science.md).

## Contributing
[CONTRIBUTING.md](./CONTRIBUTING.md) covers writing a skill, the format limits, and how to add a
source to the index.

## License
[Apache-2.0](./LICENSE); only applies to not access-restricted skills.
