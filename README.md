# cloud-soc-wazuh-automation

Ce dépôt contient l'automatisation complète pour déployer un Security Operations Center (SOC) basé sur le cloud en utilisant Wazuh, une plateforme open-source de sécurité. Il intègre des configurations Terraform pour l'infrastructure AWS, des déploiements Docker pour les composants Wazuh, et des scripts d'automatisation pour la gestion et les tests.

## Vue d'ensemble

Le projet vise à automatiser le déploiement d'un environnement SOC cloud-ready, incluant la surveillance, la détection d'intrusions, et la réponse aux incidents. Il utilise Wazuh pour la gestion des logs et des alertes, déployé sur AWS via Terraform, avec des conteneurs Docker pour une portabilité et une scalabilité.

## Structure du dépôt

Voici une description de chaque répertoire et fichier principal :

- **`docker-compose.yml`** : Fichier principal de Docker Compose pour orchestrer le déploiement global de l'environnement SOC, incluant les services Wazuh et autres composants.

- **`LICENSE`** : Fichier de licence du projet (probablement MIT ou similaire).

- **`README.md`** : Ce fichier, guide global du dépôt.

- **`attack-scenarios/`** : Contient des scénarios d'attaques simulés pour tester les capacités de détection et de réponse du SOC. Utile pour valider la configuration Wazuh.

- **`automation/`** : Scripts d'automatisation pour des tâches opérationnelles, telles que l'isolation de machines virtuelles (`isolate_vm.py`) en cas d'incident de sécurité.

- **`docker/`** : Contient le Dockerfile pour construire des images Docker personnalisées utilisées dans le déploiement, par exemple pour des outils supplémentaires ou des personnalisations.

- **`scripts/`** : Scripts utilitaires divers, comme `terraform_cleaner.sh` pour nettoyer les ressources Terraform.

- **`terraform/`** : Terraform IaC configurations for AWS resources (ECR, IAM, EC2, networking, S3, security groups). Includes safe apply scripts and history tracking.

- **`wazuh-docker/`** : Déploiement spécifique des composants Wazuh via Docker :
  - `docker-compose.yml` : Orchestration des services Wazuh (manager, indexer, dashboard).
  - `generate-indexer-certs.yml` : Playbook Ansible pour générer les certificats de l'indexer.
  - `config/` : Configurations pour les clusters Wazuh, le dashboard OpenSearch, et l'indexer.

## Prérequis

- AWS CLI configuré avec des credentials appropriés.
- Terraform installé (version >= 1.0).
- Docker et Docker Compose.
- Ansible pour certains scripts de génération de certificats.

## Utilisation

1. **Déploiement de l'infrastructure** : Naviguez vers `terraform/` et exécutez `terraform_safe_apply.sh` pour déployer les ressources AWS en toute sécurité.

2. **Déploiement Wazuh** : Utilisez `wazuh-docker/docker-compose.yml` pour lancer les services Wazuh.

3. **Tests** : Exécutez des scénarios d'attaques depuis `attack-scenarios/` pour valider le SOC.

4. **Automatisation** : Utilisez les scripts dans `automation/` pour des tâches réactives, comme l'isolation d'VMs.

Pour plus de détails, consultez les README.md spécifiques dans chaque répertoire.

## Contribution

Les contributions sont les bienvenues. Veuillez suivre les bonnes pratiques de commit et tester les changements avant de soumettre une PR.