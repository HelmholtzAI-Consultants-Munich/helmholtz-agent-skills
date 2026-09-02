#!/usr/bin/env bash
set -euo pipefail

# Maintainer convenience, not an installer. Users install with `npx skills add`.
#
# Symlinks this repo's skills into the local harness skill directories, so a
# `git pull` is all it takes to pick up changes while you are working on them:
#   ~/.claude/skills  — Claude Code
#   ~/.agents/skills  — Codex, and every other Agent Skills harness
#
# Claude Science is absent because its skill directories are server-managed and will
# discard a symlink. Upload a ZIP from dist/ instead; see docs/claude-science.md.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

mapfile -t SKILLS < <(find "$REPO/plugins" -path '*/skills/*/SKILL.md' -print0 |
  xargs -0 -n1 dirname | sort)

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo "no skills found under $REPO/plugins" >&2
  exit 1
fi

for dest in "${DESTS[@]}"; do
  # A $dest that is itself a symlink into this repo would make us write the
  # per-skill links back into our own working tree.
  if [ -L "$dest" ] && [[ "$(readlink "$dest")" == "$REPO"* ]]; then
    echo "error: $dest is a symlink into this repo. Remove it and re-run." >&2
    exit 1
  fi

  mkdir -p "$dest"
  for src in "${SKILLS[@]}"; do
    target="$dest/$(basename "$src")"
    [ -e "$target" ] && [ ! -L "$target" ] && rm -rf "$target"
    ln -sfn "$src" "$target"
    echo "linked $(basename "$src") -> $dest"
  done
done
