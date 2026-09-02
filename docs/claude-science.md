# Getting these skills into Claude Science

Claude Science installs custom skills through **Skills → Add skill → Import from GitHub**.
Paste a full github.com URL. It accepts a repo that follows the
[plugin-marketplace layout](https://code.claude.com/docs/en/plugin-marketplaces) or any repo
with `skills/` directories.

Its local catalogue under `~/.claude-science/skills/` is managed by the app and gets rebuilt,
so anything you put there by hand disappears.

## This collection

```
https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
```

Preview the catalog, then install the plugins you want. Marketplace entries that point at a
whole GitHub plugin bring that plugin's skills and any MCP servers defined at the plugin root.
Skill-only third-party entries are the curated subdirectory, not the entire upstream repo.

## One upstream plugin

Import that repository's URL instead. Example:

```
https://github.com/biocypher/biotope
```

To confirm one landed, look for its directory under
`~/.claude-science/orgs/<your-org-id>/skills/`.

## Access-controlled skills

`model-search` and `model-embed` ship as the `vhmodels` plugin. With GitHub access, import:

```
https://github.com/HelmholtzAI-Consultants-Munich/vhmodels
```

`hmgu-hpc` lives on Helmholtz GitLab. Claude Science GitHub import cannot fetch it. With GitLab
access, open https://ascgitlab.helmholtz-munich.de/vladislav.samoilov/hmgu-hpc-skill and download
[`dist/hmgu-hpc.zip`](https://ascgitlab.helmholtz-munich.de/vladislav.samoilov/hmgu-hpc-skill/-/blob/main/dist/hmgu-hpc.zip?ref_type=heads),
then **Skills → Add skill → Upload a skill** without extracting it. See [hmgu-hpc](./hpc/hmgu-hpc.md).
