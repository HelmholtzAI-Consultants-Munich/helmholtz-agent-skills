# Advanced Agentic Skills for Science

Agent skills for scientific work across Helmholtz, started at the Institute of
Computational Biology, Helmholtz Munich. Work in Claude Code,
Cursor, Codex, Copilot, Gemini CLI, and anything else that reads `SKILL.md`

## Skills
---

### Data handling

Tools for finding, understanding and querying biomedical data.

- **[dataset-scouting](./docs/data-handling/dataset-scouting.md)** — Screen public datasets to check the availability of data and metadata, fit to your criteria, and URL correctness before downloading them.
- **[biotope-croissant](./docs/data-handling/biotope-croissant.md)** — Map a messy data folder into a standardized Croissant catalog of files, types and fields.
- **[biocypher](./docs/data-handling/biocypher.md)** — Build biomedical knowledge graphs with BioCypher adapters, schema config and multi-backend export.
- **[biochatter](./docs/data-handling/biochatter.md)** — Query knowledge graphs, APIs and documents in natural language.

### Foundational AI models for biology

Helmholtz Munich foundation models for microscopy, proteins, peptides and molecules.

- **[model-search](./docs/models/model-search.md)** — Find the right biological foundation model for a task. (🔒 Restricted Access: beta version, request access)
- **[model-embed](./docs/models/model-embed.md)** — Run those models: embeddings, Conda and Apptainer runtimes. (🔒 Restricted Access: beta version, request access)

### Biological workflows

Domain-specific analysis workflows.

- **[pureclip-optimization](./docs/biological-workflows/pureclip-optimization.md)** — Choose optimal PureCLIP parameters for protein-RNA binding sites extraction from eCLIP data.

### HPC cluster use

Institute compute environments.

- **[hmgu-hpc](./docs/hpc/hmgu-hpc.md)** — The HMGU SLURM cluster: access, storage, partitions, GPU etiquette, job debugging. (🔒 Restricted Access: Helmholtz Munich SSO)

### Recommended third-party skills

Now our skills, but highly recommended.

- **[grilling](./docs/third-party/grilling.md)** — Interview the user relentlessly about a plan until every branch of the design tree is resolved.
- **[scanpy-scrna-seq](./docs/third-party/scanpy-scrna-seq.md)** — Single-cell RNA-seq analysis with Scanpy.
- **[nextflow-workflow-engine](./docs/third-party/nextflow-workflow-engine.md)** — Scalable bioinformatics workflows with Nextflow and nf-core.

## Install
---

We suggest using `npx skills` [(see official docs)](https://github.com/vercel-labs/skills).

Each skill lives in its own repository. The installer asks which skills to take and which agents
to install them into, writes them to `.agents/skills/`, and symlinks them into every harness it
detects. Add `-g` to install for your user rather than the current project, and run
`npx skills update` to refresh them later.

Open any skill above for its exact install command.

### Coding harnesses: Claude Code, Cursor, Codex, etc.

```bash
npx skills add <source>@<skill>
```

Examples:

```bash
npx skills add HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
npx skills add biocypher/biotope
```

### Claude Science and Claude Web App

Claude Science cannot install from git. Download the ZIPs from the
[latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest),
then in **Customize → Skills** add each one **without extracting it first**. One ZIP is one skill.

Full walkthrough: [docs/claude-science.md](./docs/claude-science.md).

### Access-controlled skills

Same command, against the repository that holds them. `npx skills` authenticates through your
existing git credential helper, `gh`, or SSH key; without access, the clone fails.

## Contributing
---
[CONTRIBUTING.md](./CONTRIBUTING.md) covers writing a skill, the format limits, and how to add a
source to the index.

## License
---
[Apache-2.0](./LICENSE); only applies to not access-restricted skills.
