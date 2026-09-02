# Getting these skills into Claude Science

Claude Science installs custom skills through **Skills → Add skill**. Its local catalogue under
`~/.claude-science/skills/` is managed by the app and gets rebuilt, so anything you put there
by hand disappears.

The primary route is **Import from GitHub**. ZIP upload remains a fallback when you already
have an archive, or when the source is not on GitHub.

## Import from GitHub

Under **Skills → Add skill → Import from GitHub**, paste `owner/repo`, `owner/repo@ref`, or a
github.com URL. Claude Science accepts a repo that follows the
[plugin-marketplace layout](https://code.claude.com/docs/en/plugin-marketplaces) or any repo
with `skills/` directories.

To take this collection, import:

```
HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
```

Preview the catalog, then install the plugins you want. Marketplace entries that point at a
whole GitHub plugin (for example `biotope`) bring that plugin's skills and any MCP servers
defined at the plugin root. Skill-only third-party entries are the curated subdirectory, not
the entire upstream repo.

To install one upstream plugin on its own, import that repository instead
(for example `biocypher/biotope`).

To confirm one landed, look for its directory under
`~/.claude-science/orgs/<your-org-id>/skills/`.

## ZIP fallback

1. Open the [latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest)
   and download the ZIPs you want. One ZIP is one skill.
2. **Do not extract them.** The uploader expects the archive.
3. **Skills → Add skill → Upload a skill**, and drop the ZIP.
4. Repeat for each skill.

Nothing updates automatically on this route. Every archive contains a `PROVENANCE.json` naming
the source repository and the commit it was built from:

```json
{
  "skill": "dataset-scouting",
  "source": "helmholtz-agent-skills",
  "commit": "a1b2c3d4…",
  "builtAt": "2026-08-29T09:00:00+00:00"
}
```

Compare it against the current release notes. If yours is older and the change matters to you,
download the new ZIP and upload it again.

## Access-controlled skills

`model-search`, `model-embed` and `hmgu-hpc` are not in the public marketplace or release.

`model-search` and `model-embed` ship as the `vhmodels` plugin. With GitHub access, import
`HelmholtzAI-Consultants-Munich/vhmodels` the same way as this hub. To build ZIPs from a clone
you can access:

```bash
git clone <the repository>
python3 scripts/build_zips.py --only virtual-human-chc --source-root /path/to/that/clone
```

Then upload the ZIPs under `dist/` without extracting them.

`hmgu-hpc` is on Helmholtz GitLab, which GitHub import cannot fetch. With Helmholtz GitLab
access, download
[`dist/hmgu-hpc.zip`](https://ascgitlab.helmholtz-munich.de/vladislav.samoilov/hmgu-hpc-skill/-/blob/main/dist/hmgu-hpc.zip)
and upload it as a ZIP.
