# Nettoyage du dépôt

But: retirer des fichiers d'état et secrets du dépôt public et centraliser la configuration dans Docker.

Étapes recommandées :

1. Mettre à jour `.gitignore` (déjà fait).
2. Supprimer du suivi Git les fichiers d'état et artefacts :

   - `terraform/terraform.tfstate`
   - `terraform/terraform.tfstate.backup`
   - `tfplan`, `terraform/tfplan`
   - `cloud_soc.egg-info/`
   - `.venv/`, `__pycache__/`

   Exemple rapide (exécuter localement) :

```sh
sh scripts/cleanup_repo.sh
# puis
git add .gitignore
git commit -m "chore: remove sensitive/artifact files and update .gitignore"
```

3. Déplacer secrets et certificats hors du dépôt : utiliser Docker secrets / variables d'environnement / gestionnaire secret cloud.

4. Si des secrets ont déjà été poussés, purger l'historique avec `git-filter-repo` ou `bfg` (attention, cela réécrit l'historique).

5. Documenter pour les contributeurs comment fournir les variables d'environnement ou secrets locaux (ex: `.env.example`).

Si vous voulez, j'applique les suppressions suivies (git rm --cached) et je prépare la PR. Sinon je fournis les commandes à lancer localement.
