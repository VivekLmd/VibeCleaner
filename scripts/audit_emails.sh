#!/usr/bin/env bash
set -euo pipefail

echo "Unique author/committer emails in history:"
git log --all --pretty='%ae%n%ce' | sort -u

