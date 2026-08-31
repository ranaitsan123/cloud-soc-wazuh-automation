### 5.2 Déploiement de la Stack Wazuh

Une fois l'infrastructure cloud AWS provisionnée par Terraform via l'orchestrateur `cloudsoc`, l'étape suivante consiste à instancier la plateforme de supervision centrale (SIEM). Fidèle à une approche modulaire en microservices, la stack Wazuh est entièrement conteneurisée et déployée à l'aide de Docker et Docker Compose (version 3.9) sur l'instance EC2 `wazuh_server`. Cette section détaille la configuration réelle du fichier d'orchestration, le flux automatisé d'intégration (Terraform, S3, SSM), la sécurisation TLS du cluster et la résolution des verrous techniques d'ingénierie.

#### 5.2.1 Configuration et Architecture Réelle du Docker Compose

**Localisation :** `/wazuh-docker/docker-compose.yml`

La pile de supervision a été implémentée selon une architecture microservices stricte, garantissant l'isolation applicative, le redémarrage indépendant des services et une gestion granulaire des ressources. Les conteneurs communiquent à travers un réseau virtuel dédié utilisant le driver bridge (`wazuh-net`).

Le fichier de déploiement définit trois services principaux s'appuyant sur les images officielles Wazuh v4.14.4 :

* **`wazuh.manager` :** Cœur d'analyse et d'ingestion. Il expose les ports d'enrôlement et de collecte des agents (`1514`, `1515`), la réception Syslog UDP (`514/udp`) et l'API REST (`55000`). Il monte des volumes partagés nommés (`wazuh_api_configuration`, `wazuh_etc`, `wazuh_logs`, `wazuh_queue`) ainsi que les configurations locales via des bind mounts. C'est ce service qui alimente en continu le fichier d'alertes `/var/ossec/logs/alerts/alerts.json` (point d'entrée de notre SOAR).
* **`wazuh.indexer` :** Moteur de stockage et d'indexation fondé sur OpenSearch. Il expose le port `9200` et alloue 1 Go de mémoire à la JVM (`OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g`) pour optimiser les performances sur l'instance EC2. Les données d'indexation sont pérennisées grâce au volume Docker nommé `wazuh-indexer-data` monté sur `/var/lib/wazuh-indexer`.
* **`wazuh.dashboard` :** Interface utilisateur web. Elle expose le port externe `443` (mappé sur le port interne `5601`) et s'interconnecte à l'indexer et au manager grâce aux variables d'environnement `INDEXER_URL=https://wazuh.indexer:9200` et `WAZUH_API_URL=https://wazuh.manager`.

La configuration du dépôt inclut le montage dynamique des certificats TLS dans des répertoires d'autorités de certification et de clés pour chaque conteneur :
* `/etc/ssl/root-ca.pem`
* `/etc/ssl/filebeat.pem`
* `/etc/ssl/filebeat.key`
* `/usr/share/wazuh-indexer/config/certs/`
* `/usr/share/wazuh-dashboard/certs/`

#### 5.2.2 Génération des Certificats et Sécurisation du Cluster Wazuh

Wazuh impose une communication strictement chiffrée par certificats TLS (X.509) entre tous les composants du cluster.

* **Génération Automatisée et Conditionnelle :** Dans notre pipeline, la génération des certificats est ordonnée par le playbook Ansible/YAML (`playbooks/wazuh_manager.yml`) qui invoque un conteneur éphémère via `generate-indexer-certs.yml` lorsque les certificats ne sont pas détectés localement :

```yaml
- name: Generate certificates if needed
  type: shell
  cmd: |
    if [ ! -d /opt/wazuh/config/wazuh_indexer_ssl_certs ] || [ -z "$(ls -A /opt/wazuh/config/wazuh_indexer_ssl_certs 2>/dev/null)" ]; then
      cd /opt/wazuh
      docker compose -f generate-indexer-certs.yml run --rm generator
    fi
```

* **Distribution par Bind Mounts :** Les artefacts générés (`root-ca.pem`, `wazuh.indexer.pem/key`, `wazuh.manager.pem/key`, `wazuh.dashboard.pem/key`, `admin.pem/key`) sont ensuite injectés dynamiquement dans les conteneurs par des montages de volumes (`./config/wazuh_indexer_ssl_certs/`). Ce mécanisme empêche toute présence de secret codé en dur dans les images poussées sur Amazon ECR tout en garantissant le chiffrement de bout en bout au sein du VPC.

#### 5.2.3 Intégration Réelle de Terraform, S3, SSM et Python dans le Pipeline

Le déploiement n'est pas exécuté manuellement sur la machine distante, mais est entièrement orchestré par notre CLI Python `cloudsoc` via la commande `cloud-soc deploy` :

1. **Upload des Artefacts (Terraform & S3) :** Lors de l'étape d'infrastructure (`cloud-soc apply`), Terraform provisionne les buckets S3 sécurisés (`aws_s3_bucket.wazuh_assets`) et télécharge les fichiers de configuration de la stack (`docker-compose.yml`, règles Wazuh, scripts) au moyen de ressources `aws_s3_object`.

2. **Exécution à distance via AWS SSM :** L'exécuteur Python (`cloudsoc/deployment/executor.py`) récupère les informations de l'instance `wazuh_server` via Boto3 et utilise AWS Systems Manager (SSM) pour piloter le déploiement sans nécessiter d'accès SSH direct.

3. **Séquence du Playbook sur l'Instance Cible :**
   - Création de l'arborescence `/opt/wazuh`.
   - Synchronisation des fichiers de configuration depuis S3.
   - Déclenchement du conteneur générateur de certificats TLS.
   - Lancement de la stack via `docker compose -f /opt/wazuh/docker-compose.yml up -d`.

#### 5.2.4 Déboguage et Résolution des Verrous Techniques

L'instanciation de cette stack dans un environnement d'intégration conteneurisé (Docker-in-Docker via GitHub Codespaces) et sur AWS EC2 a soulevé plusieurs défis d'ingénierie :

**1. Traitement des chaînes de caractères et variables d'environnement (Quoting Issue)**

- **Le Problème :** Lors de l'injection des variables d'environnement complexes (URLs d'API TLS comme `https://wazuh.indexer:9200`) par l'exécuteur Python (`executor.py`), une mauvaise gestion des guillemets entraînait une troncature des paramètres dans les descripteurs de processus Docker Compose, causant le crash du Dashboard.

- **La Résolution :** L'exécuteur Python a été mis à jour pour appliquer une sérialisation stricte des paires clé-valeur et valider la structure des URLs avant leur injection dans les variables d'environnement des sous-processus.

**2. Résolution d'hôtes et isolation réseau inter-conteneurs**

- **Le Problème :** Le Dashboard et le Manager tentaient d'atteindre l'Indexer via `localhost` ou des IPs statiques. Les certificats TLS étant émis pour des noms de domaine logiques (`wazuh.indexer`), l'utilisation d'IPs brutes échouait lors de la vérification du certificat.

- **La Résolution :** La configuration a été alignée sur la résolution DNS interne du réseau bridge Docker (`wazuh-net`), où chaque conteneur est identifié par son `hostname` officiel (`wazuh.indexer`, `wazuh.manager`, `wazuh.dashboard`). Des directives d'alias réseau (`extra_hosts` et `host.docker.internal`) ont également été injectées pour contourner les redirections de loopback liées au proxy de l'IDE de développement.

**3. Validation de service post-démarrage et stabilisation d'OpenSearch**

- **Le Problème :** OpenSearch (`wazuh.indexer`) et l'API Wazuh nécessitent plusieurs secondes pour s'initialiser et créer leurs index de base. Si l'orchestrateur Python considérait le déploiement terminé immédiatement après l'exécution de `docker compose up`, les tests de santé suivants échouaient.

- **La Résolution :** Une tâche de vérification explicite avec pause de stabilisation a été ajoutée à la fin du playbook `wazuh_manager.yml` pour valider l'état réel des conteneurs avant de rendre la main au CLI `cloud-soc` :

```yaml
- name: Verify Wazuh services are running
  type: shell
  cmd: |
    cd /opt/wazuh
    docker compose ps
    echo "Waiting for services to stabilize..."
    sleep 5
    docker compose logs --tail 20 wazuh.manager | tail -10
```
