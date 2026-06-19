#!/bin/sh
set -e

# Script d'aide : supprime du suivi Git les fichiers/artefacts locaux identifiés
# Exécutez localement : sh scripts/cleanup_repo.sh

echo "Removing tracked sensitive/artifact files from git index (dry-run is safer before committing)..."

# Common Terraform files
git rm --cached -f terraform/terraform.tfstate || true
git rm --cached -f terraform/terraform.tfstate.backup || true
git rm --cached -f terraform/tfplan || true
git rm --cached -f tfplan || true

# Egg-info / build artefacts
git rm --cached -r --ignore-unmatch cloud_soc.egg-info || true

# Virtual environments and caches
git rm --cached -r --ignore-unmatch .venv || true
git rm --cached -r --ignore-unmatch .python-version || true
git rm --cached -r --ignore-unmatch __pycache__ || true

# Terraform cache
git rm --cached -r --ignore-unmatch .terraform || true

# Note: ne supprime pas automatiquement les certificats ou clés s'ils ne sont pas suivis.

echo "Finished removing tracked files from index. Please review 'git status', commit and push manually."

echo "Suggested next steps:"
echo "  git status"
echo "  git add .gitignore"
echo "  git commit -m 'chore: remove sensitive/artifact files and update .gitignore'"

echo "Optional: use BFG or git-filter-repo to purge sensitive files from history if needed." 
