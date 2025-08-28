#!/usr/bin/env bash
set -euo pipefail

# Rewrite all git history to replace a personal email with GitHub noreply.
# Usage:
#   OLD_EMAIL="vivek@lmdmax.com" NEW_EMAIL="VivekLmd@users.noreply.github.com" ./scripts/rewrite_email.sh

OLD_EMAIL="${OLD_EMAIL:-}"
NEW_EMAIL="${NEW_EMAIL:-}"

if [[ -z "${OLD_EMAIL}" || -z "${NEW_EMAIL}" ]]; then
  echo "Set OLD_EMAIL and NEW_EMAIL env vars. Example:" >&2
  echo "  OLD_EMAIL=you@example.com NEW_EMAIL=User@users.noreply.github.com ./scripts/rewrite_email.sh" >&2
  exit 1
fi

echo "Rewriting history: $OLD_EMAIL -> $NEW_EMAIL"
git filter-branch -f --env-filter "
if [ \"\$GIT_AUTHOR_EMAIL\" = \"$OLD_EMAIL\" ]; then
  GIT_AUTHOR_EMAIL=\"$NEW_EMAIL\";
fi
if [ \"\$GIT_COMMITTER_EMAIL\" = \"$OLD_EMAIL\" ]; then
  GIT_COMMITTER_EMAIL=\"$NEW_EMAIL\";
fi
export GIT_AUTHOR_EMAIL GIT_COMMITTER_EMAIL
" --tag-name-filter cat -- --all

echo "Cleaning backup refs and GC..."
rm -rf .git/refs/original || true
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Force-pushing rewritten history and tags..."
DEFAULT_REMOTE="origin"
git push "$DEFAULT_REMOTE" --force --all
git push "$DEFAULT_REMOTE" --force --tags

echo "Done. If you had GitHub Releases, recreate them to match new SHAs."

