# repoready

## What it does

Score a research codebase for reproducibility (0–100) and act on findings with file:line
citations via the RepoReady MCP server.

## When to use / when not

Use when checking, improving, or certifying the reproducibility of research code — before
submitting or publishing, or when you want a cited list of what to fix.

This is a third-party plugin from RepoReady. Analysis runs on their servers and needs an
account at [repoready.ai](https://repoready.ai) (institutional email joins an org plan;
otherwise a free trial). For a local project the workflow zips the code (excluding `.git`,
dependency dirs, and `.env` files) and uploads it for analysis — don't use it on code that
must not leave your machine. Runs are metered: trial runs or your organization's plan,
which may enforce a daily cap.

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
