# Advanced Agentic Skills for Science

Agent skills for scientific work across Helmholtz, started at the Institute of
Computational Biology, Helmholtz Munich. Work in Claude Code,
Cursor, Codex, Copilot, Gemini CLI, and anything else that reads `SKILL.md`

## Skills
---

### Data handling

Tools for finding, understanding and querying biomedical data.

- **[dataset-scouting](./docs/data-handling/dataset-scouting.md)** — Screen public datasets to check the availability of data and metadata, fit to your criteria, and URL correctness before downloading them.
- **[biotope-croissant](./docs/data-handling/biotope-croissant.md)** — Map a messy data folder into a standardized Croissant catalog of files, types and fields. Useful to making the data accessible to agents and building data harmonization loaders.
- **[biocypher](./docs/data-handling/biocypher.md)** — Build biomedical knowledge graphs with BioCypher adapters, schema config and multi-backend export.

### Foundational AI models for biology

Helmholtz Munich foundation models for microscopy, proteins, peptides and molecules.

- **[model-search](./docs/models/model-search.md)** — Find the right biological foundation model from the Helmholtz's Virtual Humans model collection. (🔒 Restricted Access: beta version, request access)
- **[model-embed](./docs/models/model-embed.md)** — Have the agent properly load and run those models: Conda env setup, inference, and Apptainer runtimes. (🔒 Restricted Access: beta version, request access)

### Biological workflows

Domain-specific analysis workflows.

- **[pureclip-optimization](./docs/biological-workflows/pureclip-optimization.md)** — Choose optimal PureCLIP parameters for protein-RNA binding sites extraction from eCLIP data.

### HPC cluster use

Institute compute environments.

- **[hmgu-hpc](./docs/hpc/hmgu-hpc.md)** — Have agent reliably use the HMGU HPC cluster: access, storage, partitions, GPU etiquette, job dispatch and debugging. (🔒 Restricted Access: Helmholtz Munich SSO)

### Recommended third-party skills

Now our skills, but highly recommended.

- **[grilling](./docs/third-party/grilling.md)** — Interview the user relentlessly about a plan until every branch of the design tree is resolved.
- **[scanpy-scrna-seq](./docs/third-party/scanpy-scrna-seq.md)** — Single-cell RNA-seq analysis with Scanpy.
- **[nextflow-workflow-engine](./docs/third-party/nextflow-workflow-engine.md)** — Scalable bioinformatics workflows with Nextflow and nf-core.

## Install
---

### Coding harnesses: Claude Code, Cursor, Codex, etc.

We suggest using `npx skills` [(see official docs)](https://github.com/vercel-labs/skills).

Each skill lives in its own repository. The installer asks which skills to take and which agents
to install them into. Add `-g` to install flobally rather than the current project, and run
`npx skills update` to refresh them later.

Open any skill above for its exact install command.

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

## Contributing
---
[CONTRIBUTING.md](./CONTRIBUTING.md) covers writing a skill, the format limits, and how to add a
source to the index.

## License
---
[Apache-2.0](./LICENSE); only applies to not access-restricted skills.
