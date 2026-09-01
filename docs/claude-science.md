# Getting these skills into Claude Science

Claude Science cannot install from git, and it is not a folder you can drop skills into. Its
built-in catalogue under `~/.claude-science/skills/` is managed by the app and gets rebuilt, so
anything you put there by hand disappears. Custom skills arrive one way: you upload them to your
Claude account and the app syncs them down.

That means one manual upload per skill, and it is the only route until organisation provisioning
is enabled.

## Upload a skill

1. Open the [latest release](https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills/releases/latest)
   and download the ZIPs you want. One ZIP is one skill.
2. **Do not extract them.** The uploader expects the archive.
3. In Claude Science or the Claude Web App, go to **Customize → Skills**, add a skill, and upload the ZIP.
4. Repeat for each skill. They appear within a few moments.

To confirm one landed, look for its directory under
`~/.claude-science/orgs/<your-org-id>/skills/`.

## Keeping them current

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

`model-search`, `model-embed` and `hmgu-hpc` are not in the public release.

`hmgu-hpc` ships its archive in its own repository. With Helmholtz GitLab access, download
[`dist/hmgu-hpc.zip`](https://ascgitlab.helmholtz-munich.de/vladislav.samoilov/hmgu-hpc-skill/-/blob/main/dist/hmgu-hpc.zip)
and upload it the same way.

`model-search` and `model-embed` still have to be built from a clone you can access:

```bash
git clone <the repository>
python3 scripts/build_zips.py --only virtual-human-chc --source-root /path/to/that/clone
```

Then upload the ZIPs under `dist/` the same way.
