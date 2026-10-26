# repoready

## What it does

Check a research codebase, or a paper together with its code and data, for
reproducibility via the RepoReady MCP server. Your agent reads the result and the issues to
fix, with citations to the files and lines concerned, helps you fix them, and can check
again. What the checks cover is described at [repoready.ai](https://repoready.ai).

## When to use / when not

Use when checking, improving, or certifying the reproducibility of research code — before
submitting or publishing, or when you want a cited list of what to fix.

This is a third-party plugin from RepoReady. Analysis runs on their servers and needs an
account at [repoready.ai](https://repoready.ai); see the site for current plans and pricing.
For a local project the workflow zips the code (excluding `.git`, dependency dirs, and `.env`
files) and uploads it for analysis — don't use it on code that must not leave your machine.
Paid checks are priced before they start and run only after your approval.

## Install

Plugin install pulls the skill **and** the remote MCP server:

```bash
claude plugin marketplace add https://github.com/HelmholtzAI-Consultants-Munich/helmholtz-agent-skills
claude plugin install repoready@helmholtz-agent-skills
```

Restart Claude Code, run `/mcp`, and complete the browser sign-in.

Skill-only (workflow instructions, no MCP):

```bash
npx skills add repoready-ai/mcp-plugin@repoready
```

## Install in the Claude web app (claude.ai)

**Customize → Plugins → Add → Add marketplace → Add from a repository**, then paste
`repoready-ai/mcp-plugin` and add the **Repoready** plugin. The plugin bundles the
skill, its commands and the RepoReady MCP connector — open the plugin's **Connectors** tab
and connect it to sign in. No manually added custom connector is needed.

## Install in Claude Science

RepoReady is a remote MCP server. **Connectors → Add connector → Remote**, then:

- name: `repoready`
- URL: `https://api.repoready.ai/api/mcp`
- if Advanced settings ask for a transport, pick **Streamable HTTP** (not SSE)

Sign in when prompted (account at [repoready.ai](https://repoready.ai)).

The workflow skill is optional. **Skills → Add skill → Import from GitHub**, then paste:

```
https://github.com/repoready-ai/mcp-plugin
```

[Walkthrough](../claude-science.md).

## Source

- [repoready-ai/mcp-plugin — skills/repoready](https://github.com/repoready-ai/mcp-plugin/tree/main/skills/repoready)
- [repoready-ai/mcp-plugin](https://github.com/repoready-ai/mcp-plugin)
