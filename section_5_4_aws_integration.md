### 5.4 Intégration AWS (S3, ECR, SSM, IAM)

L'intégration AWS ne constitue pas un simple ajout fonctionnel ; elle structure l'ensemble de la logique de déploiement, de stockage, de contrôle et de réponse automatisée[cite: 2]. Plutôt que de traiter les instances virtuelles comme des serveurs isolés dépendant d'accès SSH traditionnels, le framework d'automatisation (`cloudsoc`) s'interconnecte nativement avec les services managés d'AWS via des API chiffrées et sécurisées[cite: 1, 2].

#### 5.4.1 Amazon S3 : Stockage Immuable des Artefacts de Déploiement

Le stockage des configurations et des descripteurs de la stack repose sur une intégration Terraform détaillée dans `terraform/s3.tf`[cite: 2]. Les ressources S3 créées garantissent un haut niveau de sécurité et de versionnage[cite: 2] :
* `aws_s3_bucket.wazuh_assets` : Bucket dédié à la centralisation des artefacts du projet[cite: 2].
* `aws_s3_bucket_versioning.wazuh_assets` : Activation du versionnage pour assurer la traçabilité des configurations[cite: 2].
* `aws_s3_bucket_server_side_encryption_configuration.wazuh_assets` : Chiffrement automatique au repos (SSE-S3)[cite: 2].
* `aws_s3_bucket_public_access_block.wazuh_assets` : Blocage strict de tout accès public au niveau du bucket[cite: 2].

Les artefacts de déploiement suivants sont automatiquement transférés vers le bucket via des ressources `aws_s3_object`[cite: 2] :
* `wazuh-docker/docker-compose.yml`[cite: 2]
* `wazuh-docker/generate-indexer-certs.yml`[cite: 2]
* `wazuh-docker/config/wazuh_cluster/wazuh_manager.conf`[cite: 2]
* `wazuh-docker/config/wazuh_indexer/wazuh.indexer.yml`[cite: 2]
* `wazuh-docker/config/wazuh_dashboard/opensearch_dashboards.yml`[cite: 2]
* `wazuh-docker/config/wazuh_dashboard/wazuh.yml`[cite: 2]

Cette approche centralise les fichiers sans les exposer publiquement, s'alignant sur les principes DevSecOps pour éviter tout codage en dur d'identifiants ou de paramètres dans les images conteneurisées[cite: 1, 2]. Par ailleurs, cet espace S3 sert également à l'archivage au fil de l'eau des journaux d'alertes historiques (`alerts.json`)[cite: 1].

#### 5.4.2 Amazon ECR : Gestion des Images de Service et de la Victime

Pour garantir la souveraineté des composants et maîtriser le cycle de vie des conteneurs, le fichier `terraform/ecr.tf` provisionne deux registres privés Elastic Container Registry[cite: 1, 2] :
* `aws_ecr_repository.victim_repo` : Dépôt dédié aux images de l'environnement victime[cite: 2].
* `aws_ecr_repository.manager_repo` : Dépôt réservé aux images personnalisées du SOC/Wazuh[cite: 2].

Afin de prévenir une prolifération du stockage et d'optimiser les coûts cloud, chaque registre est associé à une politique de cycle de vie (*Lifecycle Policy*) conservant uniquement les trois dernières images valides[cite: 2].

Dans le playbook Ansible (`playbooks/victim_server.yml`), l'authentification et la récupération des conteneurs s'effectuent sans stocker de clés statiques, en s'appuyant sur des jetons temporaires générés par l'API AWS[cite: 1, 2] :

```yaml
- name: Login to ECR
  type: shell
  cmd: |
    aws ecr get-login-password --region {{ aws_region }} | docker login --username AWS --password-stdin $(echo "{{ ecr_victim_repository_url }}" | cut -d'/' -f1)

- name: Pull victim container image from ECR
  type: shell
  cmd: docker pull {{ ecr_victim_repository_url }}:latest
```[cite: 2]

#### 5.4.3 AWS Systems Manager (SSM) : Canal de Contrôle et D'Exécution Prinicpal

AWS Systems Manager (SSM) constitue l'épine dorsale des communications entre l'orchestrateur Python et l'infrastructure Cloud[cite: 1, 2]. Il renie l'usage traditionnel du protocole SSH et supprime l'ouverture du port 22 sur l'Internet public, réduisant ainsi la surface d'attaque[cite: 1, 2].

Le wrapper Python `cloudsoc/aws/ssm.py` encapsule la gestion de l'API SSM à travers plusieurs fonctions clés[cite: 2] :
* `send_command()` : Envoie un script d'exécution à distance via le document `AWS-RunShellScript`[cite: 2].
* `get_command_invocation()` : Récupère les sorties standards, les erreurs et le code de retour de la commande exécutée[cite: 2].
* `wait_for_command()` : Interroge l'API en boucle jusqu'à la fin d'exécution de la tâche[cite: 2].
* `wait_for_instance()` : Valide que l'agent SSM de l'instance est en ligne et prêt à recevoir des instructions[cite: 2].

**Séquence Opérationnelle du Flux SSM :**
1. Terraform provisionne les instances EC2 dans les sous-réseaux dédiés[cite: 2].
2. Le script de bootstrap (`user_data`) installe et démarre l'agent SSM sur les instances Ubuntu[cite: 2].
3. La CLI `cloud-soc deploy` attend la disponibilité des nœuds via `wait_for_instance()`[cite: 2].
4. Les playbooks de déploiement et les commandes de réponse automatisée (SOAR) sont transmis sous forme de commandes chiffrées sans session SSH directe[cite: 1, 2].

#### 5.4.4 IAM : Modèle de Privilège Minimum pour le SOC

La sécurité du plan de contrôle est garantie par la déclaration stricte des rôles et profils d'instance IAM dans `terraform/iam.tf`[cite: 2].

* **Rôle IAM Wazuh Server :** Bénéficie des autorisations de lecture sur l'environnement EC2, de modification ciblée des Security Groups (pour le blocage d'isolation), d'accès en lecture/écriture au bucket S3 des assets, de lecture sur les dépôts ECR et de la politique managée `AmazonSSMManagedInstanceCore`[cite: 2].
* **Rôle IAM Instance Victime :** Restreint aux droits stricts de récupération de jetons d'authentification ECR (`ecr:GetAuthorizationToken`) et de lecture (`ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`) sur son propre registre[cite: 2].

Cette séparation s'aligne rigoureusement sur le principe du moindre privilège, garantissant qu'une compromission de la machine cible ne permette pas d'impacter le plan de contrôle de l'infrastructure Cloud[cite: 2].