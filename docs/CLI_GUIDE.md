# Manuel CLI — cloud-soc

Ce document présente l'ensemble des commandes disponibles dans l'outil `cloud-soc`, leurs options principales, des exemples d'utilisation et des conseils de dépannage.

**Public visé** : opérateurs d'infrastructure, ingénieurs sécurité et développeurs utilisant le projet Cloud SOC.

---

## Vue d'ensemble

- Point d'entrée : `cloud-soc` (script Typer défini dans `pyproject.toml`).
- Obtenir l'aide générale :

```bash
cloud-soc --help
cloud-soc <commande> --help
```

---

## Commandes principales

### apply

But : provisionner l'infrastructure via Terraform (init → import → validate → plan → apply).

Options :
- `--auto-approve` : appliquer automatiquement sans confirmation.
- `--var-file <file>` : fichier de variables Terraform (peut être appelé plusieurs fois).

Exemple :

```bash
cloud-soc apply --auto-approve --var-file infra/prod.tfvars
```

Remarque : `apply` se limite à Terraform — ne lance pas les tâches de déploiement/SSM.

---

### build

But : déclencher les workflows GitHub Actions pour builder les images conteneurs (ex. images victim).

Usage :

```bash
cloud-soc build [targets]
```

Options :
- `--wait` : attendre la fin du workflow GitHub (utilise `gh run watch`).
- `--ref <git-ref>` : référence Git (branche, tag, SHA) à passer au workflow.

Targets valides :
- `victim` (image du serveur victim)
- `all` (construit tous les targets supportés)

Exemple :

```bash
cloud-soc build victim --wait --ref main
```

Détails : la commande exécute `gh workflow run <workflow_file>` puis, si `--wait` est fourni, `gh run watch <id> --exit-status`.

---

### up

But : provision complète, déploiement et validation en une commande.

Options :
- `--build` : builder les images requises avant déploiement (équivalent à lancer `cloud-soc build --wait`).
- `--auto-approve` : approuver automatiquement l'application Terraform.
- `--skip-validation` : sauter la validation post-déploiement.

Exemple :

```bash
cloud-soc up --build --auto-approve
```

Flux : init → import → validate → plan → apply → (optionnel) build → attendre SSM → déployer playbooks → valider.

---

### deploy

But : déployer uniquement les services (SSM + playbooks) sur les instances déjà provisionnées.

Usage :

```bash
cloud-soc deploy [targets]
```

Options :
- `--skip-validation` : ignorer la validation du déploiement.

Targets :
- `wazuh` ou `wazuh_manager`
- `victim` ou `victim_server`
- Aucun target : déploie tout

Exemple :

```bash
cloud-soc deploy wazuh victim
```

Remarque : `deploy` NE construit PAS d'images — si une image attendue est absente dans ECR, la commande échouera et indiquera d'utiliser `cloud-soc build <target> --wait`.

---

### dashboard

But : ouvrir un tunnel SSM vers le tableau de bord Wazuh et consulter l'état du tunnel.

Commandes :
- `cloud-soc dashboard` : ouvre le tunnel (port-forward via SSM).
- `cloud-soc dashboard status` : affiche le statut du tunnel actif.

Options :
- `--local-port <port>` (par défaut 8443)
- `--remote-port <port>` (par défaut 443)
- `--expose` : afficher des conseils d'exposition si le tunnel est dans un conteneur

Exemple :

```bash
cloud-soc dashboard --local-port 9443 --remote-port 443
cloud-soc dashboard status
```

---

### deployment status

But : afficher l'historique et le statut des derniers déploiements.

Exemple :

```bash
cloud-soc deployment status
```

---

### ssm sessions

But : lister les sessions SSM actives et la santé des agents.

Exemple :

```bash
cloud-soc ssm sessions
```

---

### import

But : importer une ressource AWS existante dans l'état Terraform.

Usage :

```bash
cloud-soc import <resource_address> <resource_id>
```

Exemple :

```bash
cloud-soc import aws_vpc.wazuh_vpc vpc-0123456789abcdef0
```

---

### destroy

But : détruire l'infrastructure via Terraform.

Options :
- `--auto-approve` : ne pas demander d'approbation
- `--force` : forcer sans confirmation interactive (attention)

Exemple :

```bash
cloud-soc destroy --auto-approve
```

---

### status

But : afficher l'état actuel des ressources (VPC, subnets, instances) repérées par le tag du projet.

Exemple :

```bash
cloud-soc status
```

---

### validate

But : lancer `terraform validate` localement pour valider la configuration.

Exemple :

```bash
cloud-soc validate
```

---

### version

But : afficher la version de l'outil.

Exemple :

```bash
cloud-soc version
```

---

## Comportements importants et bonnes pratiques

- Séparation claire : `build` (images) est séparé de `deploy` (playbooks). Utilisez `cloud-soc up --build` pour enchaîner build + infra + déploiement.
- ECR check : le déploiement vérifie l'existence des images en ECR et échoue tôt si l'image est manquante.
- Contexte GitHub CLI : la commande `build` utilise l'outil `gh`. Assurez-vous d'être dans la racine du dépôt et d'être authentifié avec `gh auth login`.
- Execution non destructive : `apply` et `up` respectent les phases Terraform ; `destroy` requiert confirmation sauf `--force`.

---

## Dépannage rapide

- Erreur "No Terraform outputs found" → Exécuter d'abord `cloud-soc apply`.
- Erreur "No image found in ECR repository" → Exécuter `cloud-soc build <target> --wait` ou `cloud-soc up --build`.
- Problème `gh workflow run` → vérifier que `gh` est installé et configuré, et que vous êtes dans la racine du dépôt.

---

## Exemples d'opérations fréquentes

- Provisionner + builder + déployer :

```bash
cloud-soc up --build --auto-approve
```

- Construire uniquement l'image victim et attendre la fin :

```bash
cloud-soc build victim --wait
```

- Appliquer l'infrastructure sans déployer :

```bash
cloud-soc apply --var-file env/dev.tfvars
```

- Déployer seulement Wazuh :

```bash
cloud-soc deploy wazuh
```

- Ouvrir localement le dashboard via tunnel SSM :

```bash
cloud-soc dashboard --local-port 9443 --remote-port 443
```

---

## Authentification GitHub CLI (`gh`) et scopes recommandés

La commande `cloud-soc build` utilise l'outil `gh` (GitHub CLI) pour déclencher des workflows GitHub Actions. Avant d'exécuter `cloud-soc build`, assurez-vous que :

- `gh` est installé dans l'environnement (le Dockerfile fourni installe `gh`).
- Vous êtes authentifié avec `gh` ou qu'une variable d'environnement contenant un token GitHub est exposée au conteneur.

Authentification non-interactive (recommandé pour conteneurs/Codespaces) :

```bash
# Exemple : exporter le token dans l'environnement puis lancer la commande
export GITHUB_TOKEN="ghp_xxx..."
echo "$GITHUB_TOKEN" | gh auth login --with-token
cloud-soc build victim --wait
```

Notes pour Codespaces / devcontainers :
- Idéalement, ajoutez le token comme secret Codespaces (Repository → Settings → Codespaces → Secrets) et injectez-le dans le conteneur via `devcontainer.json` ou `containerEnv`.
- Si vous lancez le conteneur localement, passez le token au `docker run` :

```bash
docker run --rm -it -v "$PWD":/workspace -w /workspace -e GITHUB_TOKEN="$GITHUB_TOKEN" cloud-soc-dev bash
```

Scopes recommandés pour le Personal Access Token (PAT) :
- `workflow` : permet de déclencher et lire les workflows (nécessaire pour `gh workflow run` et `gh run watch`).
- `repo` : requis pour les dépôts privés (contrôle/accès aux workflows dans un repo privé). Pour les dépôts publics, `public_repo` peut suffire selon votre flux.

Bonnes pratiques de sécurité :
- N'ajoutez jamais un token en clair dans le dépôt. Utilisez des secrets injectés au runtime.
- Donnez le moins de privilèges possible (scopes minimaux) et définissez une durée d'expiration courte si possible.
- Révoquez et renouvelez régulièrement les tokens.

Note sur `entrypoint.sh` : le conteneur embarqué exécute automatiquement `echo "$GITHUB_TOKEN" | gh auth login --with-token` si `GITHUB_TOKEN` ou `GH_TOKEN` est présent, permettant un démarrage non interactif sécurisé.

---

## Tests et vérifications

- Les tests unitaires liés à l'orchestration se trouvent dans `cloudsoc/tests/`.
- Pour exécuter les tests localement :

```bash
python -m pip install -e '.[dev]'
pytest cloudsoc/tests -q
```

---

## Amendements et contribution

Si vous souhaitez ajouter une commande ou étendre une commande existante :
- Mettre à jour `cloudsoc/main.py` pour ajouter/modifier la commande Typer.
- Ajouter les orchestrateurs/services correspondants dans `cloudsoc/orchestrator.py` ou sous-répertoires.
- Ajouter/mettre à jour les tests dans `cloudsoc/tests/`.

---

Fichier créé automatiquement : `docs/CLI_GUIDE.md`
