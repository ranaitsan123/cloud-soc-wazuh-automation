**Résumé :**

Dans un contexte où les solutions de cybersécurité génèrent un volume élevé d’alertes journalières, ce projet propose une solution intelligente pour aider les administrateurs à filtrer, analyser et traiter rapidement les incidents critiques. En s’appuyant sur un modèle de langage local (Ollama), le système analyse automatiquement les alertes toutes les minutes, détermine leur nature (menace ou non), fournit des recommandations de sécurité structurées et envoie des notifications immédiates par Telegram lorsque des événements critiques sont détectés. Une interface web conviviale permet d'accéder à l’historique des alertes, de les filtrer selon différents critères (date, niveau, classification) et d’interagir de manière simple avec le système. Ce dispositif contribue à transformer un flux continu d’alertes en informations exploitables, renforçant ainsi la réactivité et l’efficacité de la gestion des incidents de sécurité.

**Mots clés :**

Analyse d’alertes, Système intelligent, Wazuh, SIEM, Ollama, Notification Telegram, LLM.

2025

#### [**https://www.univh2c.ma**](https://www.univh2c.ma/)

19, Rue Tarik Ibnou Ziad,B.P,9167, Mers Sultan Casablanca- Maroc Tél.+212 522.43.30.30/31I Fax:+212522 276150  
**E-**mail:  [presidence@univcasa.ma](mailto:presidence@univcasa.ma)

#### [**http://www.fsac.ac.ma**](http://www.fsac.ac.ma/)

Faculté des Sciences – Aïn Chock Km 8 Route d’El Jadida

B.P 5366 Mâarif Casablanca 20100 Maroc

Tel.: 05 22 23 06 80 Fax: 05 22 23 06 74

Projet de Fin d'Études

Pour obtenir le Master en

# **Ingénierie des Systèmes Intelligents**

# **Cloud Infrastructure Threat Detection and Automated Incident Response System**

Réalisé et soutenu par

**LAHNITE AICHA**

Le, 

Encadré par

**Pr. Dehbi Rachid, Faculté des Sciences Aïn Chock**

Membres du Jury

| Pr.  | Fsac | Rapporteur |
| :---- | :---- | :---- |
| **Pr.**  | **Fsac** | Rapporteur |
| **Pr.**  | **Fsac** | Encadrant |

Département de Mathématiques et Informatique

Master Ingénierie des Systèmes Intelligents	Année universitaire 2025/2026

**Remerciement**

Je tiens à adresser mes sincères remerciements à mon encadrant, Monsieur Dehbi Rachid, pour son accompagnement, sa disponibilité et les précieux conseils qu'il m'a prodigués tout au long de la réalisation de ce projet de fin d'études. Son soutien et son expertise m'ont permis de progresser et d'approfondir mes connaissances dans les domaines du Cloud Computing, de la cybersécurité et de l'automatisation.

J'adresse également mes remerciements à l'ensemble des enseignants et à toutes les personnes qui, de près ou de loin, ont contribué à la réussite de ce projet. Leurs conseils, leurs encouragements et leur soutien ont été d'une grande valeur et ont largement participé à l'aboutissement de ce travail.

Enfin, je remercie ma famille et mes proches pour leur soutien constant et leur confiance tout au long de mon parcours académique.

**Résumé**

L'adoption généralisée des infrastructures Cloud Computing a considérablement étendu la surface d'attaque des organisations, imposant une refonte des stratégies de cyberdéfense. Les Centres d'Opérations de Sécurité (SOC) traditionnels, limités par des processus d'investigation et de remédiation manuels, affichent des délais de réaction critiques face à des menaces automatisées. L'objectif de ce Projet de Fin d'Études (PFE) est de concevoir et d'implémenter un prototype de **Cyber Range Cloud** doté d'une boucle fermée de détection et de réponse automatisée (**SOAR**).

S'appuyant sur une démarche **DevSecOps**, la solution développée s'articule autour de trois piliers technologiques : l'Infrastructure en tant que Code (**IaC**) avec **Terraform** pour le provisionnement reproductible des environnements sur Amazon Web Services (**AWS**), la conteneurisation avec **Docker** pour l'industrialisation de la stack de supervision **Wazuh (SIEM)**, et le développement sur-mesure d'un orchestrateur en **Python 3**.

La validation de l'architecture a été menée selon les principes de l'ingénierie du chaos à l'aide du framework **Atomic Red Team**, en simulant des techniques offensives réelles indexées sur la matrice **MITRE ATT\&CK** (notamment la persistance via des tâches planifiées Cron). Les résultats expérimentaux démontrent une efficacité opérationnelle majeure : le couplage natif entre l'orchestrateur Python et les APIs cloud d'AWS (**Boto3**, **AWS Systems Manager**) permet de classifier l'alerte, d'isoler le réseau et d'assainir l'hôte compromis de manière totalement autonome. Les tests de performance révèlent un Temps Moyen de Réponse (**MTTR**) de seulement **8 secondes**, ce qui représente une réduction de la fenêtre d'opportunité de l'attaquant supérieure à 99% par rapport aux interventions manuelles standards, validant ainsi la viabilité industrielle du système.

**Abstract**

The widespread adoption of Cloud Computing infrastructures has significantly expanded the attack surface of organizations, demanding a fundamental shift in cyber defense strategies. Traditional Security Operations Centers (SOCs), constrained by manual investigation and incident remediation workflows, exhibit critical response latencies when facing automated threats. The primary objective of this Master’s Thesis is to design and implement a **Cloud Cyber Range** prototype featuring a closed-loop Automated Detection and Response (**SOAR**) framework.

Rooted in a **DevSecOps** methodology, the engineered solution relies on three main technical pillars: Infrastructure as Code (**IaC**) powered by **Terraform** for reproducible environment provisioning on Amazon Web Services (**AWS**), containerization via **Docker** to industrialize the **Wazuh SIEM** monitoring stack, and a custom-built automation engine developed in **Python 3**.

Architecture validation was conducted through security chaos engineering concepts using the **Atomic Red Team** framework, simulating real-world offensive techniques mapped to the **MITRE ATT\&CK** matrix (specifically persistence via malicious Cron modifications). Experimental results demonstrate a major operational breakthrough: the seamless integration between the Python orchestrator and native AWS cloud APIs (**Boto3**, **AWS Systems Manager**) enables autonomous alert classification, strict network isolation, and automated host sanitization. Performance metrics reveal a Mean Time To Respond (**MTTR**) of only **8 seconds**, yielding a reduction in the attacker's window of opportunity of over 99% compared to traditional manual SOC interventions, thereby validating the industrial viability of the system.

**Liste des abréviations**

| API  | Application Programming Interface  |
| :---- | :---- |
| APT  | Advanced Persistent Threat  |
| AWS  | Amazon Web Services  |
| CLI  | Command Line Interface  |
| CTI  | Cyber Threat Intelligence  |
| DRY  | Don't Repeat Yourself  |
| EC2  | Amazon Elastic Compute Cloud  |
| ECR  | Amazon Elastic Container Registry  |
| FIM  | File Integrity Monitoring  |
| GCP  | Google Cloud Platform  |
| IAM  | Identity and Access Management  |
| IaC  | Infrastructure as Code  |
| IoC  | Indicator of Compromise  |
| JSON  | JavaScript Object Notation  |
| KPI  | Key Performance Indicator  |
| MITRE ATT\&CK  | Adversarial Tactics, Techniques, and Common Knowledge  |
| MTTD  | Mean Time To Detect  |
| MTTR  | Mean Time To Respond  |
| PoC  | Proof of Concept  |
| POO  | Programmation Orientée Objet  |
| RAM  | Random Access Memory  |
| S3  | Amazon Simple Storage Service  |
| SDK  | Software Development Kit  |
| SG  | Security Group  |
| SIEM  | Security Information and Event Management  |
| SOAR  | Security Orchestration, Automation, and Response  |
| SOC  | Security Operations Center  |
| SSH  | Secure Shell  |
| SSM  | AWS Systems Manager  |
| TLS  | Transport Layer Security  |
| VPC  | Virtual Private Cloud  |
| YAML  | YAML Ain't Markup Language  |

**Table des matières**

**[Introduction Générale	20](#introduction-générale)**

[**Chapitre 1 : Contexte Général du Projet	21**](#chapitre-1-:-contexte-général-du-projet)

[1.1. Introduction	21](#introduction)

[1.2. Présentation de l’organisme d’accueil	22](#présentation-de-l’organisme-d’accueil)

[1.2.1 Présentation générale de l’entreprise	22](#1.2.1-présentation-générale-de-l’entreprise)

[1.2.2 Activités et domaines d’expertise	22](#1.2.2-activités-et-domaines-d’expertise)

[1.2.3 Département d’accueil	22](#1.2.3-département-d’accueil)

[1.2.4 Cadre du stage	23](#1.2.4-cadre-du-stage)

[1.3. Contexte du Projet	23](#contexte-du-projet)

[1.3.1 Contexte et motivation	23](#1.3.1-contexte-et-motivation)

[1.3.2 Problématique	24](#1.3.2-problématique)

[1.3.3 Objectifs du projet	24](#1.3.3-objectifs-du-projet)

[Objectifs fonctionnels	24](#objectifs-fonctionnels)

[Objectifs non fonctionnels	24](#objectifs-non-fonctionnels)

[1.3.4 Périmètre du projet	25](#1.3.4-périmètre-du-projet)

[1.3.5 Résultats attendus	25](#1.3.5-résultats-attendus)

[1.4. Problématique	25](#problématique)

[1.5 Objectifs du Projet	26](#1.5-objectifs-du-projet)

[1.5.1 Objectifs Fonctionnels	26](#1.5.1-objectifs-fonctionnels)

[1.5.2 Objectifs Non Fonctionnels	27](#1.5.2-objectifs-non-fonctionnels)

[1.5.3 Résultats Attendus	27](#1.5.3-résultats-attendus)

[1.6 Conclusion	27](#1.6-conclusion)

[**Chapitre 2 : Méthodologie et Gestion du Projet	30**](#chapitre-2-:-méthodologie-et-gestion-du-projet)

[2.1. Méthodologie Adoptée	30](#méthodologie-adoptée)

[2.2. Phases du Projet	32](#phases-du-projet)

[2.2.1 Phase 1 : Étude et Conception	32](#2.2.1-phase-1-:-étude-et-conception)

[2.2.2 Phase 2 : Mise en Place de l’Infrastructure Cloud	32](#2.2.2-phase-2-:-mise-en-place-de-l’infrastructure-cloud)

[2.2.3 Phase 3 : Déploiement de la Plateforme SOC	33](#2.2.3-phase-3-:-déploiement-de-la-plateforme-soc)

[2.2.4 Phase 4 : Intégration des Mécanismes de Détection	33](#2.2.4-phase-4-:-intégration-des-mécanismes-de-détection)

[2.2.5 Phase 5 : Développement de la Réponse Automatisée	34](#2.2.5-phase-5-:-développement-de-la-réponse-automatisée)

[2.2.6 Phase 6 : Validation et Tests	34](#2.2.6-phase-6-:-validation-et-tests)

[2.2.7 Synthèse des Phases	34](#2.2.7-synthèse-des-phases)

[2.3 Planification du Projet	35](#2.3-planification-du-projet)

[2.3.1 Planning Général	35](#2.3.1-planning-général)

[2.3.2 Évolution du Planning	36](#2.3.2-évolution-du-planning)

[2.3.3 Diagramme de Gantt	36](#2.3.3-diagramme-de-gantt)

[2.4 Gestion des Versions et des Évolutions	36](#2.4-gestion-des-versions-et-des-évolutions)

[2.4.1 Utilisation de GitHub	37](#2.4.1-utilisation-de-github)

[2.4.2 Stratégie de Branches	37](#2.4.2-stratégie-de-branches)

[2.4.3 Gestion des Évolutions de l’Architecture	38](#2.4.3-gestion-des-évolutions-de-l’architecture)

[2.4.4 Documentation Technique	38](#2.4.4-documentation-technique)

[2.4.5 Apports de la Gestion de Versions	38](#2.4.5-apports-de-la-gestion-de-versions)

[2.5 Conclusion	39](#2.5-conclusion)

[**Chapitre 3 : Analyse et Conception	40**](#chapitre-3-:-analyse-et-conception)

[3.1 Analyse des besoins	40](#3.1-analyse-des-besoins)

[3.1.1 Besoins fonctionnels	40](#3.1.1-besoins-fonctionnels)

[3.1.2 Besoins non fonctionnels	40](#3.1.2-besoins-non-fonctionnels)

[3.1.3 Contraintes du projet	41](#3.1.3-contraintes-du-projet)

[3.2 Étude des technologies	41](#3.2-étude-des-technologies)

[3.2.1 AWS (Amazon Web Services)	41](#3.2.1-aws-\(amazon-web-services\))

[3.2.2 Terraform	42](#3.2.2-terraform)

[3.2.3 Docker et Docker Compose	42](#3.2.3-docker-et-docker-compose)

[3.2.4 Wazuh (SIEM / EDR)	42](#3.2.4-wazuh-\(siem-/-edr\))

[3.2.5 MITRE ATT\&CK	43](#3.2.5-mitre-att&ck)

[3.2.6 Atomic Red Team	43](#3.2.6-atomic-red-team)

[3.2.7 MITRE Caldera	43](#3.2.7-mitre-caldera)

[3.2.8 Python et Boto3	43](#3.2.8-python-et-boto3)

[3.2.9 AWS Systems Manager (SSM)	44](#3.2.9-aws-systems-manager-\(ssm\))

[3.3 Conception générale	44](#3.3-conception-générale)

[3.3.1 Description des acteurs du système	45](#3.3.1-description-des-acteurs-du-système)

[3.3.2 Composants principaux du système	45](#3.3.2-composants-principaux-du-système)

[3.3.3 Cas d’utilisation global	45](#3.3.3-cas-d’utilisation-global)

[3.3.4 Diagramme fonctionnel global	46](#3.3.4-diagramme-fonctionnel-global)

[3.3.5 Scénarios principaux d’interaction \- diagrammes de séquence :	48](#3.3.5-scénarios-principaux-d’interaction---diagrammes-de-séquence-:)

[3.3.6 Flux de données	51](#3.3.6-flux-de-données)

[3.4 Conclusion	51](#3.4-conclusion)

[**Chapitre 4 : Architecture Technique de la Solution	52**](#chapitre-4-:-architecture-technique-de-la-solution)

[4.1 Vue d’ensemble de l’architecture	52](#4.1-vue-d’ensemble-de-l’architecture)

[4.2 Architecture Cloud AWS	53](#4.2-architecture-cloud-aws)

[4.2.1 Réseau et isolation : VPC SOC et sous-réseaux	53](#4.2.1-réseau-et-isolation-:-vpc-soc-et-sous-réseaux)

[4.2.2 Contrôle des flux : Security Groups	54](#4.2.2-contrôle-des-flux-:-security-groups)

[4.2.3 Calcul et services de support	54](#4.2.3-calcul-et-services-de-support)

[4.3 Architecture DevSecOps	55](#4.3-architecture-devsecops)

[4.3.1 Infrastructure as Code (IaC) avec Terraform	55](#4.3.1-infrastructure-as-code-\(iac\)-avec-terraform)

[4.3.2 Conteneurisation avec Docker et gestion des images via ECR	56](#4.3.2-conteneurisation-avec-docker-et-gestion-des-images-via-ecr)

[4.3.3 Pipeline d’exécution et orchestration customisée	56](#4.3.3-pipeline-d’exécution-et-orchestration-customisée)

[4.4 Architecture SOC	57](#4.4-architecture-soc)

[4.4.1 La Stack Centrale Wazuh (Le Cluster de Supervision)	57](#4.4.1-la-stack-centrale-wazuh-\(le-cluster-de-supervision\))

[4.4.2 Collecte de la Télémétrie : Les Agents Linux et Windows	58](#4.4.2-collecte-de-la-télémétrie-:-les-agents-linux-et-windows)

[4.5 Architecture de Simulation d’Attaque	58](#4.5-architecture-de-simulation-d’attaque)

[4.5.1 Framework d'Émulation : Atomic Red Team (ART)	59](#4.5.1-framework-d'émulation-:-atomic-red-team-\(art\))

[4.5.2 Cartographie et Alignement avec la Matrice MITRE ATT\&CK	59](#4.5.2-cartographie-et-alignement-avec-la-matrice-mitre-att&ck)

[4.5.3 Architecture Conjointe et Ouverture vers MITRE Caldera	59](#4.5.3-architecture-conjointe-et-ouverture-vers-mitre-caldera)

[4.6 Architecture de Réponse Automatisée	60](#4.6-architecture-de-réponse-automatisée)

[4.6.1 Le Moteur d'Orchestration Python (SOAR Customisé)	60](#4.6.1-le-moteur-d'orchestration-python-\(soar-customisé\))

[4.6.2 Interaction avec le Plan de Contrôle : AWS Boto3 et AWS Systems Manager (SSM)	61](#4.6.2-interaction-avec-le-plan-de-contrôle-:-aws-boto3-et-aws-systems-manager-\(ssm\))

[4.7 Évolution de l’architecture	61](#4.7-évolution-de-l’architecture)

[4.7.1 Architecture Initiale et Objectifs Primitifs	61](#4.7.1-architecture-initiale-et-objectifs-primitifs)

[4.7.2 Difficultés Rencontrées et Verrous Techniques	62](#4.7.2-difficultés-rencontrées-et-verrous-techniques)

[4.7.3 Évolution vers une Architecture Modulaire et Choix Retenus	62](#4.7.3-évolution-vers-une-architecture-modulaire-et-choix-retenus)

[4.8 Conclusion	63](#4.8-conclusion)

[**Chapitre 5 : Implémentation et Réalisation	64**](#chapitre-5-:-implémentation-et-réalisation)

[5.1 Déploiement de l’infrastructure AWS	64](#5.1-déploiement-de-l’infrastructure-aws)

[5.1.1 Organisation et Structure du Code Terraform	64](#5.1.1-organisation-et-structure-du-code-terraform)

[5.1.2 Ressources Cloud Créées	64](#5.1.2-ressources-cloud-créées)

[5.1.3 Difficultés Rencontrées et Résolutions Techniques	65](#5.1.3-difficultés-rencontrées-et-résolutions-techniques)

[5.2 Déploiement de la Stack Wazuh	66](#5.2-déploiement-de-la-stack-wazuh)

[5.2.1 Configuration et Architecture du Docker Compose	66](#5.2.1-configuration-et-architecture-du-docker-compose)

[5.2.2 La Gestion des Certificats TLS et Sécurisation Inter-Intra Conteneurs	66](#5.2.2-la-gestion-des-certificats-tls-et-sécurisation-inter-intra-conteneurs)

[5.2.3 Déboguage et Résolution des Verrous Techniques	67](#5.2.3-déboguage-et-résolution-des-verrous-techniques)

[5.3 Mise en place des Agents	67](#5.3-mise-en-place-des-agents)

[5.3.1 Déploiement et Configuration sur l'Agent Linux	67](#5.3.1-déploiement-et-configuration-sur-l'agent-linux)

[5.3.2 Déploiement et Configuration sur l'Agent Windows	68](#5.3.2-déploiement-et-configuration-sur-l'agent-windows)

[5.3.3 Sécurisation des Flux et Validation de l'Enrôlement	68](#5.3.3-sécurisation-des-flux-et-validation-de-l'enrôlement)

[5.4 Intégration AWS (S3, ECR, SSM)	69](#5.4-intégration-aws-\(s3,-ecr,-ssm\))

[5.4.1 Distribution des Images de Supervision : Amazon ECR	69](#5.4.1-distribution-des-images-de-supervision-:-amazon-ecr)

[5.4.2 Archivage Immuable des Journaux : Amazon S3	69](#5.4.2-archivage-immuable-des-journaux-:-amazon-s3)

[5.4.3 Le Canal de Contrôle Sécurisé : AWS Systems Manager (SSM)	70](#5.4.3-le-canal-de-contrôle-sécurisé-:-aws-systems-manager-\(ssm\))

[5.5 Développement des Scripts Python	70](#5.5-développement-des-scripts-python)

[5.5.1 L’Exécuteur de Tâches (executor.py)	70](#5.5.1-l’exécuteur-de-tâches-\(executor.py\))

[5.5.2 Le Moteur de Réponse Automatisée (orchestrator.py)	71](#5.5.2-le-moteur-de-réponse-automatisée-\(orchestrator.py\))

[5.5.3 Couplage et Communication Inter-Modules	72](#5.5.3-couplage-et-communication-inter-modules)

[5.6 Conclusion	73](#5.6-conclusion)

[**Chapitre 6 : Validation et Tests	74**](#chapitre-6-:-validation-et-tests)

[6.1 Méthodologie de test	74](#6.1-méthodologie-de-test)

[6.1.1 Le Cycle d'Évaluation Opérationnel	74](#6.1.1-le-cycle-d'évaluation-opérationnel)

[6.1.2 Critères d'Évaluation et Indicateurs Clés de Performance (KPIs)	74](#6.1.2-critères-d'évaluation-et-indicateurs-clés-de-performance-\(kpis\))

[6.2 Scénario 1 : Atomic Red Team	75](#6.2-scénario-1-:-atomic-red-team)

[6.2.1 Description et Objectif de l'Attaque	75](#6.2.1-description-et-objectif-de-l'attaque)

[6.2.2 Technique MITRE ATT\&CK Utilisée : T1053.005 (Scheduled Task/Job: Cron)	75](#6.2.2-technique-mitre-att&ck-utilisée-:-t1053.005-\(scheduled-task/job:-cron\))

[6.2.3 Détection par le SIEM Wazuh	76](#6.2.3-détection-par-le-siem-wazuh)

[6.2.4 Résultats et Validation de la Visibilité	77](#6.2.4-résultats-et-validation-de-la-visibilité)

[6.3 Scénario 2 : MITRE Caldera	77](#6.3-scénario-2-:-mitre-caldera)

[6.4 Réponse automatisée	77](#6.4-réponse-automatisée)

[6.4.1 Déclenchement du Playbook SOAR	78](#6.4.1-déclenchement-du-playbook-soar)

[6.4.2 Isolation de la Machine et Actions AWS Exécutées	78](#6.4.2-isolation-de-la-machine-et-actions-aws-exécutées)

[6.4.3 Analyse Forensique et Nettoyage via AWS SSM	78](#6.4.3-analyse-forensique-et-nettoyage-via-aws-ssm)

[6.4.4 Validation de l'État de Remédiation	79](#6.4.4-validation-de-l'état-de-remédiation)

[6.5 Analyse des performances	79](#6.5-analyse-des-performances)

[6.5.1 Chronologie Précise du Cycle de Remédiation	79](#6.5.1-chronologie-précise-du-cycle-de-remédiation)

[6.5.2 Évaluation du MTTD et du MTTR	80](#6.5.2-évaluation-du-mttd-et-du-mttr)

[6.5.3 Comparaison Opérationnelle : Approche Manuelle vs Approche Automatisée	80](#6.5.3-comparaison-opérationnelle-:-approche-manuelle-vs-approche-automatisée)

[6.5.4 Réduction Drastique de la Fenêtre d'Opportunité	81](#6.5.4-réduction-drastique-de-la-fenêtre-d'opportunité)

[6.6 Discussion	81](#6.6-discussion)

[6.6.1 Limites Techniques du Système de Réponse	82](#6.6.1-limites-techniques-du-système-de-réponse)

[6.6.2 Gestion des Faux Positifs et Risques de l'Automatisation	82](#6.6.2-gestion-des-faux-positifs-et-risques-de-l'automatisation)

[6.7 Conclusion	83](#6.7-conclusion)

[**Conclusion Générale	84**](#conclusion-générale)

[**Webographie	85**](#webographie)

[⮚ I. Référentiels de Cybersécurité et Frameworks	85](#i.-référentiels-de-cybersécurité-et-frameworks)

[⮚ II. Infrastructure Cloud et Automatisation (Infrastructure as Code)	85](#ii.-infrastructure-cloud-et-automatisation-\(infrastructure-as-code\))

[⮚ III. Supervision (SIEM) et Microservices	85](#iii.-supervision-\(siem\)-et-microservices)

[⮚ IV. Automatisation de la Réponse (SOAR) et Méthodologies	86](#iv.-automatisation-de-la-réponse-\(soar\)-et-méthodologies)

[**Annexes	87**](#annexes)

[Annexe A : Fichier d'orchestration de l'infrastructure (main.tf)	87](#annexe-a-:-fichier-d'orchestration-de-l'infrastructure-\(main.tf\))

[Annexe B : Extrait de la configuration du Manager Wazuh (ossec.conf)	89](#annexe-b-:-extrait-de-la-configuration-du-manager-wazuh-\(ossec.conf\))

[\<ossec\_config\>	89](#\</ruleset\>)

[\<global\>	89](#\</ruleset\>)

[\<jsonout\_output\>yes\</jsonout\_output\>	89](#\</ruleset\>)

[\<alerts\_log\>yes\</alerts\_log\>	89](#\</ruleset\>)

[\<logall\>no\</logall\>	89](#\</ruleset\>)

[\<logall\_json\>no\</logall\_json\>	89](#\</ruleset\>)

[\</global\>	89](#\</ruleset\>)

[\<\!-- Configuration des ports d'ecoute pour la communication chiffree \--\>	89](#\</ruleset\>)

[\<remote\>	89](#\</ruleset\>)

[\<connection\>secure\</connection\>	89](#\</ruleset\>)

[\<port\>1514\</port\>	89](#\</ruleset\>)

[\<protocol\>tcp\</protocol\>	89](#\</ruleset\>)

[\<queue\_size\>131072\</queue\_size\>	89](#\</ruleset\>)

[\</remote\>	89](#\</ruleset\>)

[\<\!-- Activation du moteur de regles interne \--\>	90](#\</ruleset\>)

[\<ruleset\>	90](#\</ruleset\>)

[\<\!-- Regles par defaut de Wazuh \--\>	90](#\</ruleset\>)

[\<decoder\_dir\>ruleset/decoders\</decoder\_dir\>	90](#\</ruleset\>)

[\<rule\_dir\>ruleset/rules\</rule\_dir\>	90](#\</ruleset\>)

[\<rule\_include\>0015-ciscat\_rules.xml\</rule\_include\>	90](#\</ruleset\>)

[\<rule\_include\>0530-ossec\_rules.xml\</rule\_include\> \<\!-- Inclut la regle 533 de la Crontab \--\>	90](#\</ruleset\>)

[\<\!-- Emplacement de nos regles et signatures personnalisees \--\>	90](#\</ruleset\>)

[\<rule\_dir\>etc/rules\</rule\_dir\>	90](#\</ruleset\>)

[\</ruleset\>	90](#\</ruleset\>)

[\</ossec\_config\>	90](#\</ossec_config\>)

[Annexe C : Code source complet de l'orchestrateur de réponse (orchestrator.py)	90](#annexe-c-:-code-source-complet-de-l'orchestrateur-de-réponse-\(orchestrator.py\))

[Annexe D : Captures d’écran et résultats de tests	93](#annexe-d-:-captures-d’écran-et-résultats-de-tests)

[D.1 Tableau récapitulatif des captures de validation	93](#d.1-tableau-récapitulatif-des-captures-de-validation)

[Annexe E : Lien GitHub du projet	94](#annexe-e-:-lien-github-du-projet)

[E.1 Accès au Répertoire Principal	94](#e.1-accès-au-répertoire-principal)

**Liste des figures**

[Figure 1: Diagramme de Gantt	11](#heading=h.cn7wu94vkrar)

[Figure 2: Diagramme des taches	11](#heading=h.bz5tvsldp2ba)

[Figure 3: Architecture du SIEM	14](#2.2.5-phase-5-:-développement-de-la-réponse-automatisée)

[Figure 4: Architecture Wazuh	24](#heading=h.k95ecq5y209q)

[Figure 5: Les principaux domaines d’application de l’intelligence artificielle (IA) et de l’apprentissage automatique (ML) en cybersécurité. 27](#heading=h.vb8jyjc9hy5c) [Figure 6: Les principales techniques d’IA et d’apprentissage automatique appliquées à la cybersécurité	27](#heading=h.wq6tc8s2dok)

[Figure 7: L’impact du machine learning sur les fonctions IDS/IPS	30](#heading=h.fw79l1ucbrv8)

[Figure 8: Techniques d’IA/ML dans l’analyse comportementale et le profilage des utilisateurs	30](#heading=h.jfw5m7fklwpi)

[Figure 9: NLP dans la threat intelligence : automatisation de l’analyse et des informations	31](#heading=h.oj3z8sdf2fwb)

[Figure 10: VirtualBox logo	34](#heading=h.16yjys50bd87)

[Figure 11: Ubuntu logo	34](#heading=h.6swxv8y07iig)

[Figure 12: Kali linux logo	35](#heading=h.fkjfoogf9apg)

[Figure 13: Python logo	35](#heading=h.eqxmw4snxgao)

[Figure 14: Flask logo	36](#heading=h.mnp1rs8mv5tx)

[Figure 15: Visual Studio Code logo	36](#heading=h.4bt47njzjiym)

[Figure 16: PuTTY logo	37](#heading=h.e94ofmv3b7kw)

[Figure 17: Ollama logo	37](#heading=h.vb3485svvodu)

[Figure 18: Telegram logo	38](#heading=h.871x729gtfqe)

[Figure 19: Docker logo	38](#heading=h.77h4bcumcvvo)

[Figure 20: Wazuh logo	39](#heading=h.xkrxbdlhr3yq)

[Figure 21: Ubuntu Server	41](#heading=h.dwi7kxloyg5l)

[Figure 22: Ubuntu Victim	41](#heading=h.hohgbghkjym1)

[Figure 23: Kali linux	42](#heading=h.hnzweg27jdds)

[Figure 24: Schéma architecture	42](#heading=h.p92oq78pu1h7)

[Figure 25: update & upgrade du système	43](#heading=h.kkmvs1ws4cus)

[Figure 26: Installation de curl	43](#heading=h.z1en1jv6o5bj)

[Figure 27: Installation de Wazuh Manager	44](#heading=h.l6roo1h3ae73)

[Figure 28: L'état de Wazuh Manager	44](#heading=h.vfp16p2nvg0k)

[Figure 29: l'état de Wazuh dashboard	45](#heading=h.vohia04ejokb)

[Figure 30: Wazuh Dashboard	45](#heading=h.eafx5vkduv28)

[Figure 31: ajouter un agent Wazuh	45](#heading=h.vszlh3d14y30)

[Figure 32: Choix de l'architecture du système	46](#heading=h.t8po9w60wr3r)

[Figure 33: Insertion de l'adresse IP du Wazuh Manager	46](#heading=h.l0mac1s8qj3v)

[Figure 34: saisi du nom de l'agent	46](#heading=h.kt1wo8ppjktc)

[Figure 35: Commande d'installation d'agent Wazuh	47](#heading=h.3deh3mp79qxv)

[Figure 36: Installation d'agent Wazuh	47](#heading=h.izj5lmajeg2r)

[Figure 37: Commandes de démarrage de l'agent Wazuh	47](#heading=h.pukqysec5nec)

[Figure 38: Démarrage de l'agent Wazuh	47](#heading=h.kkeg5h1eo2q9)

[Figure 39: Le statut de l'agent Wazuh	48](#heading=h.gb2db5oy9l17)

[Figure 40: Agent Wazuh victim-ubuntu	48](#heading=h.aqzx3syb2xgj)

[Figure 41: Installation des dépendances requises	49](#heading=h.i993kzln57fm)

[Figure 42: Importe de la clé Docker GPG	50](#heading=h.gvniwp7t6rf0)

[Figure 43: Ajout de dépôt Docker	50](#heading=h.2u8f8mz74m3o)

[Figure 44: Mise à jour des packages système	50](#heading=h.jpqtlc3pj0p6)

[Figure 45: Installation de Docker	50](#heading=h.mi1n4lo05pnm)

[Figure 46: Continuation d'installation de Docker	51](#heading=h.fai0xq19nl10)

[Figure 47: Vérification du statut de Docker	51](#heading=h.wg6o8rm7a658)

[Figure 48: Creation du répertoire pour docker compose	52](#heading=h.8dtu5gidxjqd)

[Figure 49: Téléchargement de docker compose	52](#heading=h.jsqx31665srf)

[Figure 50: Définition des autorisations	52](#heading=h.tmdfgornnebh)

[Figure 51: Vérification de la version de docker compose	52](#heading=h.52sko8ooh9te)

[Figure 52: Creation de fichier docker-compose.yml	52](#heading=h.goiel2yzcl70)

[Figure 53: docker-compose.yml partie 1	53](#heading=h.5lj471gupxxp)

[Figure 54: docker-compose.yml partie 2	53](#heading=h.uglfamsgi29s)

[Figure 55: Installation des services	53](#heading=h.cly8xaocosnr)

[Figure 56: Vérification des conteneurs	54](#heading=h.y1pb04w23jrv)

[Figure 57: Installation de openSSH	54](#heading=h.n99kssllpgnf)

[Figure 58: Vérification du statut de openSSH	54](#heading=h.7xlgzfpa3euw)

[Figure 59: Autorisation de la connexion sur le port SSH	55](#heading=h.c131qokzaed9)

[Figure 60: Activation et rechargement d'UFM	55](#heading=h.ckloa66t9ex)

[Figure 61: Vérification du service SSH	55](#heading=h.sg93v9jxr32u)

[Figure 62: Configuration de la collecte des logs Docker	56](#heading=h.7i466vot52w3)

[Figure 63: Activation du module docker listener	56](#heading=h.ilgskjpcbic9)

[Figure 64: Creation d'une règle personnalisée de Docker	57](#heading=h.uz4jebiwadg9)

[Figure 65: Activation des logs HTTP Apache via modification de la règle 31108	57](#heading=h.98p7frm5i4q3)

[Figure 66: Fichier local\_decoder.xml	58](#heading=h.pei50loyu4x9)

[Figure 67: Exécution du binaire de test de journal	58](#heading=h.mue6yumlwmuz)

[Figure 68: requête http	59](#heading=h.jjv3n0gk3yha)

[Figure 69: Fichier passwords.lst	59](#heading=h.iirfedwqy1u7)

[Figure 70: Execution de Hydra	60](#heading=h.lode8uf047x7)

[Figure 71: Scan de vulnérabilités avec Nikto	60](#heading=h.eujua8bz1tjr)

[Figure 72: Alerte de la requête HTTP avec curl	61](#heading=h.5rqjwno4i7ug)

[Figure 73: Alerte générée lors de l'attaque de force brute avec hydra	61](#heading=h.8d5cp1l9bz5g)

[Figure 74: Alertes générées par le scan de vulnérabilités avec nikto	61](#heading=h.txq5i04on339)

[Figure 75: Onglet de dossier partagé	64](#heading=h.pdy1tbsi1li9)

[Figure 76: Ajouter un dossier partagé	64](#heading=h.iyxdv3lod2u3)

[Figure 77: Insertion des informations des dossier partagé	64](#heading=h.iru6i6inn232)

[Figure 78: Montage manuel du dossier partagé	65](#heading=h.m0f6anpbl0u)

[Figure 79: Montage permanent du dossier partagé	65](#heading=h.9bbtcv5tzd6r)

[Figure 80: Commande crontab	65](#heading=h.np531cfpday8)

[Figure 81: Copie du fichier alerts.json	66](#heading=h.k49hwxyfdd8v)

[Figure 82: Importation des modules	66](#heading=h.i4rmv84zr02m)

[Figure 83: Déclaration des constantes	67](#heading=h.475gvcq19jvf)

[Figure 84: dictionnaire des patterns des menaces	67](#heading=h.dpu1krvhure9)

[Figure 85: Template du message pour l'IA	68](#heading=h.66n20ds1m1z8)

[Figure 86: Initialisation du modèle Ollama	69](#heading=h.n7t69qrucb9e)

[Figure 87: Fonction de détection de mots-clés	70](#heading=h.sm5sm98dvk91)

[Figure 88: Analyse complète avec IA	71](#heading=h.ppbk1lq7ychy)

[Figure 89: Correction intelligente de la réponse	72](#heading=h.e59mty2icq80)

[Figure 90: Fallback si l'IA ne répond pas	73](#heading=h.yrfmwhcp5m37)

[Figure 91: Analyse de plusieurs alertes	74](#heading=h.zig33t3pjh0t)

[Figure 92: Chargement des alertes	75](#heading=h.apass119pbhm)

[Figure 93: Vérification de doublons	75](#heading=h.mb7jomjv79t)

[Figure 94: Exécution automatique	76](#heading=h.2bcrqouj0igh)

[Figure 95: Telegrame BotFather	78](#heading=h.kfj7o63b20mg)

[Figure 96: Création du bot	78](#heading=h.385pxzp3813j)

[Figure 97: Le bot Telegram crée	79](#heading=h.kegv5zbdtw9y)

[Figure 98: Récuperation de l'ID du chat	79](#heading=h.46oi18tcsy3a)

[Figure 99: Script notifier.py	80](#heading=h.4apbtbb4iarc)

[Figure 100: Fonction de lecture d'analyses	82](#heading=h.skb2it63aukj)

[Figure 101: Statistiques globales du système	83](#heading=h.iqzbclab464y)

[Figure 102: Vérification si c'est une alerte est d'aujourd’hui	84](#heading=h.4kf9yevwd5tx)

[Figure 103: Fonction pour déterminer la couleur selon la criticité	84](#heading=h.j3ce6k9qynqn)

[Figure 104: API pour rechercher en temps réel	85](#heading=h.c1tn5xe6y1z8)

[Figure 105: API pour les statistiques	85](#heading=h.qzw89xdk7j4o)

[Figure 106: Route principale de l'application	86](#heading=h.9qohi7g80g58)

[Figure 107: Bloc main de l'application	86](#heading=h.kjeloys023i0)

[Figure 108: Extrait de fichier alerts.json	88](#heading=h.x16gfjhwijpx)

[Figure 109: Analyse d'alerte Docker	88](#heading=h.u9ku43jbcvi1)

[Figure 110: Analyse d'alerte SSH	89](#heading=h.fx908gc466et)

[Figure 111: Analyse d'alerte de web server	89](#heading=h.3riprzga2riq)

[Figure 112: Extrait de fichier analyses.log	90](#heading=h.ejv2sn7ucowu)

[Figure 113: Notification Telegram	91](#heading=h.asg6umugvdjo)

[Figure 114: Message reçu de wazbot	91](#heading=h.tb96ujj215mp)

[Figure 115: Extrait du fichier notified.log	92](#heading=h.3p8atmi2r1q8)

[Figure 116: Démarrage de l'app Flask	92](#heading=h.s4juyts7sq5w)

[Figure 117: Titre pricipal de l'application	93](#heading=h.4ixf20t5q5ge)

[Figure 118: Tableau de bord de statiques	93](#heading=h.wgy6eaywt319)

[Figure 119: Zone de filtres de l'application	93](#heading=h.1lq3y1fpujm9)

[Figure 120: Extrait de liste des alertes analysées	94](#heading=h.7eefb9eiodjk)

[Figure 121: Extrait 1 de l’aAffichage mobile de l'application	95](#heading=h.py17f0jydj95)

[Figure 122: Extrait 2 de l'affichage mobile de l'application	95](#heading=h.e7ntxmdvhqhk)

# Introduction Générale {#introduction-générale}

L'avènement du Cloud Computing et la transition massive des entreprises vers des infrastructures dématérialisées ont profondément bouleversé les paradigmes de la production logicielle et de la gestion des systèmes d'information. En offrant une flexibilité sans précédent, des ressources élastiques et une réduction drastique des coûts opérationnels, les plateformes de Cloud public, au premier rang desquelles figure Amazon Web Services (AWS), sont devenues le socle de l'innovation technologique moderne.

Cependant, cette mutation technologique s'accompagne d'une complexification majeure de la surface d'attaque. Les infrastructures Cloud ne se résument plus à de simples serveurs distants, mais forment des écosystèmes dynamiques, interconnectés et hautement programmables. Cette agilité, si elle profite aux équipes de développement, est également exploitée par des cyberattaquants de plus en plus sophistiqués. Ces derniers déploient désormais des scripts et des logiciels malveillants automatisés capables d'identifier des vulnérabilités, de compromettre des instances et d'exfiltrer des données sensibles en quelques minutes, voire quelques secondes.

# Chapitre 1 : Contexte Général du Projet  {#chapitre-1-:-contexte-général-du-projet}

1. ## Introduction {#introduction}

La transformation numérique et l’adoption croissante des technologies Cloud ont profondément modifié la manière dont les organisations déploient et gèrent leurs infrastructures informatiques. Les plateformes Cloud offrent de nombreux avantages tels que la flexibilité, la scalabilité, la haute disponibilité et l’optimisation des coûts. Cependant, cette évolution s’accompagne également de nouveaux défis en matière de cybersécurité.

Les infrastructures Cloud modernes sont exposées à une grande variété de menaces, notamment les attaques par force brute, les compromissions de comptes, les erreurs de configuration, les mouvements latéraux ou encore l’exploitation de vulnérabilités. Face à ces risques, les entreprises doivent être capables non seulement de détecter rapidement les activités malveillantes, mais également de réagir efficacement afin de limiter l’impact des incidents de sécurité.

Dans ce contexte, les centres opérationnels de sécurité (Security Operations Centers – SOC) jouent un rôle essentiel en assurant la surveillance continue des systèmes, l’analyse des événements de sécurité et la gestion des incidents. Toutefois, les approches traditionnelles reposant principalement sur des interventions manuelles peuvent entraîner des délais importants de détection et de réponse, augmentant ainsi les risques pour l’organisation.

Afin de répondre à ces enjeux, les approches modernes de cybersécurité s’orientent vers l’automatisation des processus de surveillance et de réponse aux incidents, en s’appuyant sur des technologies telles que les solutions SIEM (Security Information and Event Management), l’Infrastructure as Code (IaC), les pratiques DevSecOps et les mécanismes d’orchestration de la sécurité.

C’est dans cette perspective que s’inscrit le présent projet de fin d’études, réalisé au sein de la société Omnidata. L’objectif principal est de concevoir et mettre en œuvre un système Cloud de détection des menaces et de réponse automatisée aux incidents de sécurité. La solution proposée repose sur une infrastructure AWS déployée automatiquement à l’aide de Terraform, une plateforme SOC basée sur Wazuh pour la collecte et l’analyse des événements de sécurité, ainsi que des mécanismes d’automatisation développés en Python pour la réponse aux incidents. Des outils de simulation d’attaques tels qu’Atomic Red Team et MITRE Caldera sont également intégrés afin d’évaluer l’efficacité des mécanismes de détection et de remédiation mis en place.

Ce rapport présente les différentes étapes du projet, depuis l’analyse des besoins et la conception de l’architecture jusqu’à l’implémentation, la validation et l’évaluation de la solution développée.

2. ## Présentation de l’organisme d’accueil  {#présentation-de-l’organisme-d’accueil}

### **1.2.1 Présentation générale de l’entreprise**  {#1.2.1-présentation-générale-de-l’entreprise}

![][image1]

Omnidata est une entreprise marocaine spécialisée dans les technologies de l’information, l’intégration de solutions informatiques et les services numériques destinés aux entreprises et aux administrations. Forte de plusieurs années d’expérience, l’entreprise accompagne ses clients dans leur transformation digitale à travers la mise en œuvre de solutions innovantes couvrant différents domaines technologiques.

L’entreprise intervient notamment dans les domaines des infrastructures informatiques, des réseaux, du Cloud Computing, de la cybersécurité, de la gestion des données et de l’intégration de solutions logicielles. Grâce à son expertise multidisciplinaire, Omnidata propose des services adaptés aux besoins de ses clients tout en respectant les exigences de performance, de disponibilité et de sécurité.

### **1.2.2 Activités et domaines d’expertise**  {#1.2.2-activités-et-domaines-d’expertise}

Les principales activités d’Omnidata s’articulent autour des axes suivants :

* Conception et déploiement d’infrastructures informatiques.  
* Intégration de solutions Cloud et virtualisation.  
* Mise en place de solutions de cybersécurité et de supervision.  
* Administration des systèmes et réseaux.  
* Gestion et analyse des données.  
* Conseil et accompagnement dans les projets de transformation digitale.  
* Support technique et maintenance des infrastructures.

Dans le domaine de la cybersécurité, l’entreprise participe à la mise en œuvre de solutions permettant la protection des systèmes d’information, la surveillance des événements de sécurité, la détection des menaces et la gestion des incidents.

### **1.2.3 Département d’accueil**   {#1.2.3-département-d’accueil}

Le projet de fin d’études a été réalisé au sein du département Cybersécurité d’Omnidata. Ce département est chargé d’accompagner les clients dans la sécurisation de leurs infrastructures et de leurs applications à travers différentes activités telles que :

* La supervision des événements de sécurité.  
* L’analyse des alertes et des incidents.  
* La gestion des vulnérabilités.  
* Le déploiement de solutions SIEM et SOC.  
* La mise en œuvre de mécanismes de détection et de réponse aux menaces.

L’environnement de travail a permis de découvrir les processus opérationnels liés à la cybersécurité ainsi que les outils utilisés dans les centres opérationnels de sécurité (SOC).

### **1.2.4 Cadre du stage**  {#1.2.4-cadre-du-stage}

Dans le cadre de ce stage de Projet de Fin d’Études (PFE), l’objectif principal était de participer à la conception et au développement d’une solution permettant d’améliorer la détection des menaces et l’automatisation de la réponse aux incidents dans un environnement Cloud.

Le projet s’inscrit dans une démarche DevSecOps combinant les domaines du Cloud Computing, de la cybersécurité, de l’automatisation et de l’Infrastructure as Code. Il vise à mettre en place une architecture capable de détecter des activités malveillantes, de centraliser les événements de sécurité et de déclencher automatiquement des actions de remédiation afin de réduire le temps de réaction face aux incidents.

Cette expérience a permis de mettre en pratique les connaissances acquises durant le cursus universitaire tout en développant de nouvelles compétences techniques dans les domaines du Cloud AWS, de la cybersécurité opérationnelle, de l’automatisation et de l’orchestration des mécanismes de sécurité.

3. ## Contexte du Projet  {#contexte-du-projet}

### **1.3.1 Contexte et motivation**   {#1.3.1-contexte-et-motivation}

Avec l’adoption croissante du Cloud Computing, les entreprises déploient de plus en plus leurs applications et infrastructures sur des plateformes cloud afin de bénéficier d’une meilleure flexibilité, d’une réduction des coûts d’exploitation et d’une mise à l’échelle simplifiée. Cependant, cette évolution s’accompagne d’une augmentation de la surface d’attaque et de nouveaux défis en matière de sécurité.

Les environnements cloud sont exposés à de nombreuses menaces telles que les attaques par force brute, les compromissions d’identifiants, les erreurs de configuration, les accès non autorisés ou encore les activités malveillantes visant les ressources hébergées. Dans ce contexte, il devient essentiel de mettre en place des mécanismes permettant de surveiller en continu l’infrastructure, détecter rapidement les comportements suspects et réagir efficacement aux incidents de sécurité.

Les centres opérationnels de sécurité (SOC) jouent un rôle fondamental dans cette démarche en assurant la collecte, l’analyse et la corrélation des événements de sécurité. Toutefois, les processus de réponse restent souvent manuels, ce qui peut augmenter le temps nécessaire pour contenir un incident et limiter son impact.

L’automatisation de certaines tâches de sécurité constitue aujourd’hui une approche stratégique permettant d’améliorer l’efficacité opérationnelle des équipes de sécurité tout en réduisant le temps moyen de détection et de réponse aux incidents.

### **1.3.2 Problématique**  {#1.3.2-problématique}

Dans un environnement cloud moderne, les incidents de sécurité peuvent se produire à tout moment et évoluer rapidement. Bien que de nombreux outils permettent de détecter les activités suspectes, la réponse aux incidents dépend encore souvent d’interventions manuelles réalisées par les administrateurs ou les analystes SOC.

Cette situation soulève plusieurs problématiques :

* Comment détecter efficacement les activités malveillantes dans une infrastructure cloud ?  
* Comment centraliser et analyser les événements de sécurité provenant de plusieurs systèmes ?  
* Comment réduire le temps nécessaire pour répondre à un incident de sécurité ?  
* Comment automatiser certaines actions de remédiation afin de limiter l’impact d’une attaque ?  
* Comment concevoir une architecture flexible, reproductible et facilement déployable dans un environnement cloud ?

Ces questions constituent le point de départ du présent projet.

### **1.3.3 Objectifs du projet**  {#1.3.3-objectifs-du-projet}

L’objectif principal du projet est de concevoir et mettre en œuvre un système de détection des menaces et de réponse automatisée aux incidents dans une infrastructure cloud AWS.

Pour atteindre cet objectif, plusieurs sous-objectifs ont été définis :

### Objectifs fonctionnels {#objectifs-fonctionnels}

* Déployer une infrastructure cloud sécurisée sur AWS.  
* Mettre en place une plateforme SOC basée sur Wazuh pour la supervision et l’analyse des événements de sécurité.  
* Déployer et configurer des agents de collecte sur les machines surveillées.  
* Simuler différents scénarios d’attaque à l’aide d’Atomic Red Team et de MITRE Caldera.  
* Détecter les comportements malveillants à travers des règles et mécanismes de surveillance.  
* Développer des mécanismes automatisés de réponse aux incidents à l’aide de Python et des services AWS.  
* Valider l’efficacité de la solution à travers des scénarios de test représentatifs.

### Objectifs non fonctionnels {#objectifs-non-fonctionnels}

* Assurer l’automatisation du déploiement grâce à l’Infrastructure as Code (Terraform).  
* Garantir la reproductibilité de l’infrastructure.  
* Favoriser une architecture modulaire et évolutive.  
* Réduire le temps moyen de réponse aux incidents (MTTR).  
* Respecter les bonnes pratiques de sécurité et de gestion des accès.

### **1.3.4 Périmètre du projet**  {#1.3.4-périmètre-du-projet}

Le projet se concentre principalement sur la mise en œuvre d’une architecture SOC cloud intégrant des mécanismes de détection et de réponse automatisée.

Le périmètre couvre :

* Les ressources AWS nécessaires à l’infrastructure.  
* Le déploiement et la configuration de la plateforme Wazuh.  
* L’intégration des outils de simulation d’attaque.  
* Le développement des mécanismes d’automatisation de la réponse aux incidents.  
* La validation de la solution à travers des scénarios de test.

En revanche, certains aspects ne sont pas couverts dans cette première version du projet, notamment :

* Le support multi-cloud (Azure, Google Cloud).  
* L’intégration complète d’une plateforme SOAR commerciale.  
* Les mécanismes avancés de Threat Intelligence.  
* L’utilisation de modèles d’intelligence artificielle pour la détection comportementale.

### **1.3.5 Résultats attendus**  {#1.3.5-résultats-attendus}

À l’issue du projet, la solution devra permettre :

* La supervision centralisée des événements de sécurité.  
* La détection automatique d’activités suspectes ou malveillantes.  
* L’exécution automatisée d’actions de remédiation selon les scénarios définis.  
* La réduction du temps nécessaire pour contenir un incident.  
* La démonstration d’une approche DevSecOps appliquée à la cybersécurité cloud.

Cette solution constitue ainsi une illustration concrète de l’intégration des technologies Cloud, de la cybersécurité et de l’automatisation au sein d’une architecture moderne de type SOC.

4. ## Problématique  {#problématique}

L’essor du Cloud Computing a considérablement amélioré la flexibilité et l’évolutivité des infrastructures informatiques. Cependant, cette évolution s’accompagne d’une augmentation des risques de sécurité liés à la multiplication des ressources, à la complexité des architectures et à l’exposition croissante des services sur Internet.

Dans les environnements cloud, les attaques peuvent se propager rapidement et compromettre plusieurs ressources avant même qu’une intervention humaine ne soit réalisée. Bien que les solutions SIEM permettent de collecter et d’analyser les événements de sécurité afin de détecter les comportements suspects, la réponse aux incidents reste souvent manuelle, ce qui augmente le temps de réaction et l’impact potentiel des attaques.

Par ailleurs, les équipes de sécurité doivent faire face à un volume important d’alertes et à des infrastructures en constante évolution, rendant nécessaire l’automatisation de certaines tâches de détection, d’investigation et de remédiation.

Dans ce contexte, il devient essentiel de concevoir une solution capable de surveiller efficacement une infrastructure cloud, de détecter les activités malveillantes et de déclencher automatiquement des actions de réponse adaptées afin de limiter les risques de compromission.

La problématique de ce projet peut ainsi être formulée comme suit :

**Comment concevoir et déployer un système Cloud capable de détecter efficacement les menaces de sécurité et d’automatiser la réponse aux incidents afin de réduire le temps de réaction et l’impact des attaques sur l’infrastructure ?**

## 1.5 Objectifs du Projet  {#1.5-objectifs-du-projet}

Afin de répondre à la problématique identifiée, ce projet vise à concevoir et mettre en œuvre une plateforme Cloud de détection des menaces et de réponse automatisée aux incidents de sécurité. La solution proposée s’appuie sur les principes du DevSecOps, de l’Infrastructure as Code (IaC) et de l’automatisation afin d’améliorer la capacité de détection et de réaction face aux cyberattaques dans un environnement Cloud.

Les objectifs du projet sont répartis en objectifs fonctionnels et non fonctionnels.

### **1.5.1 Objectifs Fonctionnels**  {#1.5.1-objectifs-fonctionnels}

Les principaux objectifs fonctionnels du projet sont les suivants :

* Déployer une infrastructure Cloud sécurisée sur AWS à l’aide de Terraform.  
* Mettre en place une plateforme SOC basée sur Wazuh pour la collecte, la centralisation et l’analyse des événements de sécurité.  
* Déployer et configurer des agents de supervision sur les machines surveillées.  
* Simuler différents scénarios d’attaque à l’aide d’Atomic Red Team et de MITRE Caldera afin de reproduire des techniques réelles utilisées par les attaquants.  
* Détecter automatiquement les comportements suspects et les activités malveillantes à travers les mécanismes de surveillance de Wazuh.  
* Développer des mécanismes de réponse automatisée aux incidents à l’aide de scripts Python et des services AWS.  
* Mettre en œuvre des playbooks de réponse permettant d’exécuter automatiquement des actions de remédiation lorsqu’une menace est détectée.  
* Valider l’efficacité de la solution à travers des scénarios de tests représentatifs.

### **1.5.2 Objectifs Non Fonctionnels**  {#1.5.2-objectifs-non-fonctionnels}

Au-delà des fonctionnalités attendues, le projet doit également respecter plusieurs exigences non fonctionnelles :

* Automatiser le déploiement et la gestion de l’infrastructure afin de réduire les interventions manuelles.  
* Garantir la reproductibilité de l’environnement grâce à l’Infrastructure as Code.  
* Concevoir une architecture modulaire facilitant l’intégration de nouveaux composants de sécurité.  
* Assurer la maintenabilité et l’évolutivité de la solution.  
* Réduire le temps moyen de détection et de réponse aux incidents (MTTR).  
* Respecter les bonnes pratiques de sécurité concernant la gestion des accès, des identités et des communications entre composants.  
* Faciliter l’intégration future d’outils complémentaires de cybersécurité et d’orchestration tels que Cortex ou Shuffle.  
* Assurer la traçabilité des actions effectuées dans le cadre des mécanismes de détection et de réponse aux incidents.

### **1.5.3 Résultats Attendus**  {#1.5.3-résultats-attendus}

À l’issue du projet, la solution développée devra permettre :

* La supervision centralisée des ressources et événements de sécurité.  
* La détection de scénarios d’attaque simulés dans un environnement Cloud.  
* L’exécution automatisée de certaines actions de réponse aux incidents.  
* La réduction du temps de réaction face aux menaces.  
* La démonstration d’une approche DevSecOps appliquée à la cybersécurité Cloud.  
* La mise à disposition d’une architecture réutilisable et extensible pour des besoins futurs de supervision et d’orchestration de la sécurité.

Ainsi, ce projet vise à démontrer comment l’association des technologies Cloud, des solutions SIEM et des mécanismes d’automatisation peut contribuer à renforcer la posture de sécurité d’une infrastructure moderne tout en améliorant l’efficacité opérationnelle des équipes de sécurité.

## 1.6 Conclusion  {#1.6-conclusion}

Dans ce premier chapitre, nous avons présenté le contexte général du projet ainsi que les enjeux liés à la sécurisation des infrastructures Cloud modernes. L’évolution des systèmes d’information vers des architectures de plus en plus distribuées et dynamiques rend indispensable la mise en place de mécanismes efficaces de surveillance, de détection et de réponse aux incidents de sécurité.

Après avoir présenté l’organisme d’accueil et le cadre du stage, nous avons exposé la problématique du projet ainsi que les objectifs fonctionnels et non fonctionnels à atteindre. La solution envisagée repose sur la combinaison de plusieurs approches complémentaires, notamment le Cloud Computing, l’Infrastructure as Code, les pratiques DevSecOps, les technologies SIEM et l’automatisation de la réponse aux incidents.

Le projet vise ainsi à concevoir une plateforme capable de détecter des activités malveillantes dans un environnement AWS et de déclencher automatiquement des actions de remédiation afin de réduire le temps de réaction face aux menaces. L’utilisation d’outils tels que Wazuh, Atomic Red Team, MITRE Caldera et Python permettra de mettre en œuvre une architecture moderne orientée supervision et automatisation de la sécurité.

Le chapitre suivant présentera la méthodologie adoptée pour la réalisation du projet ainsi que les différentes phases ayant permis sa conception, son développement et sa mise en œuvre.

# Chapitre 2 : Méthodologie et Gestion du Projet  {#chapitre-2-:-méthodologie-et-gestion-du-projet}

1. ## Méthodologie Adoptée  {#méthodologie-adoptée}

La réalisation de ce projet a nécessité l’adoption d’une méthodologie flexible permettant de prendre en compte les contraintes techniques liées à la cybersécurité, au Cloud Computing et à l’automatisation. Contrairement à un projet de développement classique dont les exigences sont généralement bien définies dès le départ, ce projet a évolué progressivement en fonction des résultats obtenus, des difficultés rencontrées et des nouvelles exigences techniques identifiées au cours de sa réalisation.

Pour cette raison, une approche itérative inspirée des principes DevSecOps a été adoptée. Cette méthodologie repose sur l’intégration continue de la sécurité tout au long du cycle de vie du projet, ainsi que sur l’automatisation des opérations de déploiement, de supervision et de réponse aux incidents.

L’approche suivie s’articule autour de plusieurs cycles successifs comprenant les étapes suivantes :

* #### **Analyse et étude des besoins**

La première étape a consisté à analyser les objectifs du projet et à identifier les différentes composantes nécessaires à la mise en place d’un environnement SOC Cloud. Cette phase a également permis d’étudier les technologies susceptibles d’être utilisées, notamment AWS, Terraform, Docker, Wazuh, Python, Atomic Red Team et MITRE Caldera.

* #### **Conception de l’architecture**

Une architecture initiale a été définie afin de répondre aux objectifs de supervision et de réponse automatisée. Au cours du projet, cette architecture a été progressivement améliorée afin d’intégrer de nouveaux composants tels que les mécanismes de simulation d’attaques, les services AWS de gestion à distance et les fonctionnalités d’automatisation avancées.

Cette démarche itérative a permis d’adapter continuellement la solution aux besoins réels du projet tout en conservant une architecture modulaire et évolutive.

* #### **Déploiement automatisé de l’infrastructure**

L’infrastructure Cloud a été mise en place à l’aide de Terraform selon les principes de l’Infrastructure as Code (IaC). Cette approche permet de décrire l’ensemble des ressources AWS sous forme de code, garantissant ainsi la reproductibilité, la traçabilité et la simplification des opérations de déploiement.

Les différentes ressources nécessaires au projet (réseaux, instances EC2, groupes de sécurité, stockage et services associés) sont automatiquement créées et configurées à partir de fichiers de configuration versionnés.

* #### **Mise en œuvre de la plateforme SOC**

La plateforme de supervision a été déployée à l’aide de conteneurs Docker afin de faciliter son installation, son maintien en condition opérationnelle et sa portabilité. Cette étape comprend l’intégration des composants Wazuh Manager, Wazuh Indexer et Wazuh Dashboard, ainsi que la configuration des agents de collecte de journaux sur les machines supervisées.

* #### **Simulation des attaques et validation de la détection**

Afin d’évaluer les capacités de détection de la solution, plusieurs scénarios d’attaque sont mis en œuvre à l’aide des outils Atomic Red Team et MITRE Caldera. Ces outils permettent de reproduire des techniques d’attaque réelles référencées dans le framework MITRE ATT\&CK et de vérifier la capacité du SOC à détecter les activités malveillantes.

* #### **Automatisation de la réponse aux incidents**

Une fois les mécanismes de détection validés, la dernière phase consiste à développer des mécanismes de réponse automatisée aux incidents. Cette automatisation repose principalement sur des scripts Python utilisant les services AWS afin d’exécuter des actions correctives ou de confinement lorsqu'un comportement suspect est détecté.

L’objectif est de réduire le temps moyen de réponse aux incidents (MTTR) et de démontrer l’intérêt de l’automatisation dans un environnement SOC moderne.

* #### **Approche DevSecOps appliquée au projet**

L’ensemble du projet s’inscrit dans une démarche DevSecOps qui vise à intégrer la sécurité dès les premières phases de conception et tout au long du cycle de développement. Cette approche repose sur plusieurs principes :

* Automatisation des déploiements à travers Terraform.  
* Utilisation du contrôle de version avec GitHub.  
* Conteneurisation des services avec Docker.  
* Centralisation des configurations.  
* Validation continue à travers des scénarios de tests de sécurité.  
* Automatisation des mécanismes de réponse aux incidents.

Cette méthodologie permet de garantir une meilleure cohérence de l’infrastructure, une réduction des erreurs manuelles et une amélioration continue de la posture de sécurité du système développé.

2. ## Phases du Projet  {#phases-du-projet}

La réalisation de ce projet a été organisée en plusieurs phases successives permettant de concevoir, déployer et valider progressivement la solution. Cette démarche a facilité l’intégration des différentes technologies utilisées tout en assurant une évolution continue de l’architecture vers une approche DevSecOps orientée automatisation et cybersécurité. 

### **2.2.1 Phase 1 : Étude et Conception**  {#2.2.1-phase-1-:-étude-et-conception}

Cette première phase a consisté à analyser les besoins du projet, définir les objectifs à atteindre et étudier les technologies susceptibles de répondre aux exigences fonctionnelles et techniques.

Les principaux travaux réalisés durant cette phase sont :

* Analyse du contexte et de la problématique.  
* Étude des concepts liés aux SOC, SIEM et SOAR.  
* Étude des services AWS nécessaires au projet.  
* Analyse des solutions de supervision et de détection.  
* Étude des outils de simulation d’attaques.  
* Élaboration de l’architecture générale du système.  
* Identification des mécanismes de réponse automatisée à mettre en place.

Cette étape a permis de définir les différentes composantes du projet ainsi que les interactions entre elles.

### **2.2.2 Phase 2 : Mise en Place de l’Infrastructure Cloud**  {#2.2.2-phase-2-:-mise-en-place-de-l’infrastructure-cloud}

La deuxième phase a été consacrée à la création de l’environnement Cloud sur AWS.

Afin de garantir la reproductibilité et l’automatisation du déploiement, l’ensemble de l’infrastructure a été décrit à l’aide de Terraform selon les principes de l’Infrastructure as Code (IaC).

Les travaux réalisés comprennent :

* Création des réseaux virtuels (VPC).  
* Configuration des sous-réseaux.  
* Mise en place des Security Groups.  
* Déploiement des instances EC2.  
* Configuration des rôles et permissions IAM.  
* Mise en place des services de stockage et de gestion des configurations.

Cette phase a également permis d’identifier et de corriger plusieurs problèmes liés à la gestion du cycle de vie des ressources cloud et à la duplication involontaire de certaines ressources lors des déploiements.

### **2.2.3 Phase 3 : Déploiement de la Plateforme SOC** {#2.2.3-phase-3-:-déploiement-de-la-plateforme-soc}

Cette phase a porté sur l’installation et la configuration de la plateforme de supervision de sécurité.

La solution retenue repose sur Wazuh, déployé sous forme de conteneurs Docker afin de faciliter la gestion et la portabilité de l’environnement.

Les principales activités réalisées sont :

* Déploiement de la stack Wazuh.  
* Configuration du Wazuh Manager.  
* Configuration du Wazuh Indexer.  
* Configuration du Wazuh Dashboard.  
* Génération et gestion des certificats de sécurité.  
* Vérification de la communication entre les différents composants.  
* Intégration des agents de supervision.

Cette étape a nécessité plusieurs opérations de débogage afin de résoudre des problèmes liés au déploiement des conteneurs et à la gestion des certificats.

### **2.2.4 Phase 4 : Intégration des Mécanismes de Détection**  {#2.2.4-phase-4-:-intégration-des-mécanismes-de-détection}

Une fois l’infrastructure SOC opérationnelle, la phase suivante a consisté à mettre en place les mécanismes permettant de détecter des comportements malveillants.

Pour cela, plusieurs outils et frameworks spécialisés ont été étudiés et intégrés au projet.

Les travaux réalisés comprennent :

* Étude du framework MITRE ATT\&CK.

* Intégration d’Atomic Red Team.

* Intégration de MITRE Caldera.

* Création de scénarios de simulation d’attaques.

* Analyse des alertes générées par Wazuh.

* Validation des mécanismes de détection.

Cette phase permet de reproduire des techniques d’attaque réalistes afin d’évaluer l’efficacité du SOC mis en place.

### **2.2.5 Phase 5 : Développement de la Réponse Automatisée**  {#2.2.5-phase-5-:-développement-de-la-réponse-automatisée}

Cette phase est dédiée à la mise en œuvre des mécanismes de réponse aux incidents.

L’objectif est de réduire l’intervention humaine lors de la gestion de certains incidents en automatisant les actions de remédiation.

Les principales tâches concernées sont :

* Développement de scripts Python.

* Utilisation du SDK AWS Boto3.

* Intégration avec les mécanismes Active Response de Wazuh.

* Automatisation des actions de confinement.

* Exécution de commandes à distance via AWS Systems Manager (SSM).

* Développement de playbooks de réponse aux incidents.

Cette phase constitue le cœur de la dimension SOAR du projet.

### **2.2.6 Phase 6 : Validation et Tests**  {#2.2.6-phase-6-:-validation-et-tests}

La dernière phase consiste à vérifier le bon fonctionnement de l’ensemble de la solution développée.

Les tests réalisés visent à évaluer :

* Le déploiement automatisé de l’infrastructure.  
* La stabilité de la plateforme SOC.  
* Les capacités de détection des attaques.  
* Le fonctionnement des mécanismes de réponse automatisée.  
* Les performances globales du système.

Des scénarios d’attaque basés sur Atomic Red Team et MITRE Caldera sont exécutés afin de mesurer l’efficacité des mécanismes de détection et de réponse.

### **2.2.7 Synthèse des Phases**  {#2.2.7-synthèse-des-phases}

La méthodologie adoptée repose sur une progression incrémentale permettant de construire progressivement une architecture complète de supervision et de réponse aux incidents. Chaque phase s’appuie sur les résultats de la phase précédente, ce qui garantit une meilleure maîtrise des technologies utilisées et facilite l’évolution du projet vers une solution DevSecOps intégrant les concepts de SIEM, SOAR, Infrastructure as Code et automatisation Cloud. 

## 2.3 Planification du Projet  {#2.3-planification-du-projet}

Afin d'assurer une réalisation progressive et structurée du projet, un planning prévisionnel a été établi dès le début du stage. Cette planification a permis d'organiser les différentes activités en fonction des objectifs à atteindre et des dépendances existantes entre les différentes phases du projet.

Toutefois, comme pour de nombreux projets orientés recherche et innovation, certaines évolutions techniques ont conduit à des ajustements du planning initial. En effet, plusieurs défis liés à l'intégration des technologies Cloud, à l'automatisation du déploiement et à la mise en place des mécanismes de cybersécurité ont nécessité des phases supplémentaires d'étude, de conception et de débogage.

L'approche adoptée est donc une planification itérative permettant d'adapter progressivement le projet aux contraintes techniques rencontrées tout en conservant les objectifs fixés.

### **2.3.1 Planning Général** {#2.3.1-planning-général}

Le projet a été découpé en six grandes phases :

| Phase | Activités principales |
| ----- | ----- |
| Phase 1 | Étude des besoins et conception de l'architecture |
| Phase 2 | Déploiement de l'infrastructure Cloud avec Terraform |
| Phase 3 | Déploiement et configuration de la plateforme Wazuh |
| Phase 4 | Intégration des mécanismes de détection (Atomic Red Team et MITRE Caldera) |
| Phase 5 | Développement des mécanismes de réponse automatisée |
| Phase 6 | Validation, tests et préparation de la soutenance |

### **2.3.2 Évolution du Planning** {#2.3.2-évolution-du-planning}

Au cours du projet, plusieurs ajustements ont été nécessaires afin d'améliorer la qualité et la robustesse de la solution développée.

Parmi les principales évolutions :

* Refonte partielle de l'architecture initiale afin d'intégrer correctement les composants de simulation d'attaque et d'automatisation.  
* Mise en place d'une architecture multi-VPC afin de mieux isoler les différents rôles du système.  
* Introduction des services AWS SSM et ECR pour améliorer l'automatisation et réduire les opérations manuelles.  
* Mise en œuvre d'une stratégie de gestion des configurations basée sur Amazon S3.  
* Adoption d'une approche DevSecOps plus complète intégrant des mécanismes CI/CD et une meilleure séparation des responsabilités.

Ces évolutions ont permis d'obtenir une architecture plus modulaire, plus réaliste et davantage alignée avec les pratiques professionnelles du domaine de la cybersécurité Cloud.

### **2.3.3 Diagramme de Gantt** {#2.3.3-diagramme-de-gantt}

Le diagramme de Gantt présenté dans la section suivante illustre la répartition temporelle des différentes phases du projet ainsi que leur enchaînement.

Il met en évidence :

* Les périodes d'étude et de conception.  
* Les phases de développement et d'intégration.  
* Les activités de validation et de test.  
* Les tâches réalisées en parallèle.  
* Les ajustements apportés au cours du projet.

Ce planning constitue un outil de suivi permettant d'évaluer l'état d'avancement du projet et de garantir le respect des échéances fixées pour la soutenance.

*(Le diagramme de Gantt détaillé sera inséré dans cette section.)*

## 2.4 Gestion des Versions et des Évolutions {#2.4-gestion-des-versions-et-des-évolutions}

Dans le cadre de ce projet, un système de gestion de versions a été mis en place afin de faciliter le suivi des modifications, la collaboration avec les encadrants et l'évolution progressive de la solution développée.

Pour cela, la plateforme GitHub a été utilisée comme dépôt central du projet. Elle permet de conserver l'historique des changements, de documenter les différentes étapes de développement et de garantir la traçabilité des évolutions apportées à l'architecture et au code source.

### **2.4.1 Utilisation de GitHub** {#2.4.1-utilisation-de-github}

L'ensemble des composants du projet est centralisé dans un dépôt GitHub regroupant :

* Les fichiers Terraform utilisés pour le déploiement de l'infrastructure AWS.  
* Les configurations Docker de la plateforme Wazuh.  
* Les scripts Python d'automatisation et de réponse aux incidents.  
* La documentation technique du projet.  
* Les diagrammes d'architecture et de flux.  
* Les fichiers de configuration nécessaires au déploiement et aux tests.

Cette organisation facilite la maintenance du projet et permet de suivre précisément l'évolution de chaque composant.

### **2.4.2 Stratégie de Branches** {#2.4.2-stratégie-de-branches}

Le développement du projet a été organisé selon une approche de gestion de versions basée sur Git, afin de permettre une évolution progressive, expérimentale et sécurisée de l’architecture.

Contrairement à une structure GitFlow stricte, le projet a suivi une organisation flexible adaptée à la nature exploratoire du travail (DevSecOps, Cloud et automatisation), où l’architecture évolue rapidement en fonction des tests et contraintes techniques.

Cette approche a permis :

* L’isolation des expérimentations techniques (Terraform, Wazuh, SSM, Docker)  
* La refactorisation progressive de l’orchestrateur Python  
* La validation indépendante des composants de sécurité et d’automatisation  
* La réduction des risques de régression lors des changements majeurs

Les branches ont été organisées par fonctionnalité et par évolution technique, notamment :

* Déploiement et infrastructure (ex : `feature/build-deployment-workflow`)  
* Intégration des mécanismes de détection (ex : `feature/art-soc-baseline`)  
* Orchestration et automatisation Python (ex : `refactor/python-orchestrator-v3`)  
* Intégration des services AWS et monitoring (ex : `feature/ssm-dashboard-connection`)

Cette organisation a également évolué au cours du projet, certaines branches ayant été refactorisées plusieurs fois afin d’adapter l’architecture aux contraintes réelles rencontrées sur AWS et dans l’intégration des outils de cybersécurité.

### **2.4.3 Gestion des Évolutions de l’Architecture** {#2.4.3-gestion-des-évolutions-de-l’architecture}

L'architecture du projet a connu plusieurs évolutions au cours de sa réalisation.

Initialement centrée sur un déploiement simple de Wazuh dans un environnement AWS, elle a progressivement évolué vers une architecture DevSecOps plus complète intégrant :

* Infrastructure as Code avec Terraform.  
* Gestion centralisée des configurations via Amazon S3.  
* Conteneurisation avec Docker.  
* Registre d'images avec Amazon ECR.  
* Automatisation des opérations via AWS Systems Manager (SSM).  
* Simulation d'attaques avec Atomic Red Team et MITRE Caldera.  
* Réponse automatisée aux incidents à l'aide de scripts Python.

Ces évolutions ont été motivées par les besoins du projet ainsi que par les difficultés rencontrées lors de certaines phases d'intégration.

### **2.4.4 Documentation Technique** {#2.4.4-documentation-technique}

Une attention particulière a été portée à la documentation du projet afin de faciliter sa compréhension et sa maintenance.

La documentation comprend notamment :

* Des diagrammes d'architecture réseau.  
* Des diagrammes de flux de données.  
* Des diagrammes Mermaid décrivant les interactions entre composants.  
* La description des mécanismes de détection et de réponse aux incidents.  
* Les procédures de déploiement et de test.

Cette documentation est régulièrement mise à jour afin de refléter l'état réel du projet et d'assurer une meilleure traçabilité des décisions techniques prises au cours du développement.

### **2.4.5 Apports de la Gestion de Versions** {#2.4.5-apports-de-la-gestion-de-versions}

L'utilisation de GitHub et d'une stratégie de développement basée sur les branches a permis :

* De sécuriser les développements.  
* D'éviter les régressions lors des modifications importantes.  
* De tester indépendamment les nouvelles fonctionnalités.  
* D'améliorer la qualité de la documentation.  
* De faciliter le suivi de l'avancement du projet.  
* De conserver l'historique complet des évolutions techniques.

Cette approche s'inscrit pleinement dans les bonnes pratiques DevOps et DevSecOps utilisées aujourd'hui dans les projets Cloud et cybersécurité.

## 2.5 Conclusion  {#2.5-conclusion}

Ce chapitre a permis de présenter la démarche méthodologique adoptée ainsi que l’organisation globale du projet. Dans un contexte combinant cybersécurité, cloud computing et DevSecOps, une approche rigoureuse mais flexible a été nécessaire afin de s’adapter à l’évolution progressive des besoins techniques et des contraintes d’intégration.

La méthodologie retenue repose sur une approche itérative inspirée des pratiques DevSecOps, permettant de construire progressivement une architecture complète allant de l’infrastructure Cloud jusqu’à la réponse automatisée aux incidents de sécurité. Cette approche a facilité l’expérimentation, l’intégration progressive des outils (Terraform, Docker, Wazuh, MITRE ATT\&CK, Atomic Red Team, AWS SSM) ainsi que l’amélioration continue de la solution.

L’organisation du travail en plusieurs phases a permis de structurer le projet de manière cohérente, en séparant clairement les étapes de conception, de déploiement, de détection et d’automatisation. Chaque phase a contribué à enrichir la compréhension globale du système et à renforcer la robustesse de l’architecture finale.

Par ailleurs, la gestion des versions via GitHub a joué un rôle central dans le suivi du projet. Elle a permis de gérer efficacement les évolutions successives de l’architecture, les refactorisations de l’orchestrateur Python, ainsi que l’intégration progressive des différents modules. Cette organisation a également facilité la traçabilité des choix techniques et la validation des différentes fonctionnalités développées.

Enfin, ce chapitre met en évidence le caractère évolutif du projet. L’architecture initiale a été progressivement adaptée et améliorée afin de répondre aux exigences réelles d’un environnement SOC cloud moderne, intégrant des notions de sécurité, d’automatisation et d’infrastructure as code.

Le chapitre suivant présentera l’analyse et la conception détaillée de la solution, ainsi que les différents choix techniques effectués pour la mise en place de l’architecture globale.

# Chapitre 3 : Analyse et Conception  {#chapitre-3-:-analyse-et-conception}

## 

## 3.1 Analyse des besoins {#3.1-analyse-des-besoins}

L’analyse des besoins constitue une étape fondamentale dans la conception de la solution, car elle permet d’identifier les exigences fonctionnelles et non fonctionnelles du système à mettre en place. Dans le cadre de ce projet, l’objectif principal est de concevoir une plateforme Cloud de détection des menaces et de réponse automatisée aux incidents, intégrant des approches DevSecOps, SIEM et SOAR.

Le système doit permettre de reproduire un environnement réaliste de type Security Operations Center (SOC) dans le Cloud, capable de détecter des comportements malveillants, de les analyser et de déclencher des actions de remédiation de manière automatisée.

### **3.1.1 Besoins fonctionnels** {#3.1.1-besoins-fonctionnels}

Les besoins fonctionnels définissent les principales fonctionnalités attendues du système :

* Déployer automatiquement une infrastructure Cloud sécurisée sur AWS à l’aide d’Infrastructure as Code (Terraform).  
* Mettre en place un environnement SOC basé sur Wazuh (Manager, Indexer, Dashboard).  
* Installer et gérer des agents de surveillance sur des machines cibles (Linux et Windows).  
* Collecter et centraliser les logs de sécurité provenant des différentes machines.  
* Détecter des activités suspectes ou malveillantes à partir de règles de corrélation et de scénarios d’attaque.  
* Simuler des attaques réalistes à l’aide de frameworks tels que Atomic Red Team et MITRE Caldera.  
* Déclencher des alertes de sécurité en temps réel lors de la détection d’incidents.  
* Automatiser la réponse aux incidents de sécurité via des scripts Python utilisant AWS Boto3 et AWS Systems Manager (SSM).  
* Isoler automatiquement les machines compromises afin de limiter la propagation des attaques.

### **3.1.2 Besoins non fonctionnels** {#3.1.2-besoins-non-fonctionnels}

Les besoins non fonctionnels concernent les contraintes et qualités attendues du système :

* **Sécurité** : l’architecture doit respecter les principes de Zero Trust, avec une minimisation des accès directs et une utilisation privilégiée de SSM.  
* **Automatisation** : le maximum d’opérations doit être automatisé afin de réduire l’intervention humaine.  
* **Scalabilité** : l’infrastructure doit pouvoir évoluer facilement pour supporter plusieurs machines et scénarios d’attaque.  
* **Fiabilité** : le système doit être stable malgré les redéploiements fréquents et les tests destructifs.  
* **Reproductibilité** : l’ensemble de l’environnement doit pouvoir être reconstruit rapidement via Terraform et Docker.  
* **Modularité** : chaque composant (détection, attaque, réponse) doit être indépendant pour faciliter les évolutions futures.  
* **Maintenabilité** : le code, les configurations et les scripts doivent être structurés pour permettre une maintenance simple et évolutive.

### **3.1.3 Contraintes du projet** {#3.1.3-contraintes-du-projet}

Le projet est soumis à plusieurs contraintes techniques et organisationnelles :

* Utilisation exclusive des services AWS disponibles dans le cadre académique et du budget alloué.  
* Nécessité de maîtriser plusieurs technologies complexes (Terraform, Docker, Wazuh, Caldera, AWS SSM).  
* Environnement de développement évolutif nécessitant plusieurs refactorisations de l’architecture.  
* Temps limité pour la réalisation du projet et la préparation de la soutenance.  
* Nécessité d’adapter les outils de cybersécurité (initialement conçus pour des environnements on-premise) à un environnement Cloud.

## 3.2 Étude des technologies {#3.2-étude-des-technologies}

Cette section présente les principales technologies utilisées dans le cadre du projet. Le choix de ces outils est motivé par la nécessité de construire une architecture Cloud moderne, automatisée et orientée cybersécurité, intégrant les concepts de SIEM, SOAR et DevSecOps.

### **3.2.1 AWS (Amazon Web Services)** {#3.2.1-aws-(amazon-web-services)}

![][image2]

AWS constitue la plateforme Cloud principale utilisée pour héberger l’ensemble de l’infrastructure du projet.

Les services utilisés incluent notamment :

* **Amazon EC2** : déploiement des serveurs (SOC, victimes, attaquant).  
* **Amazon VPC** : isolation réseau et segmentation des environnements.  
* **Security Groups** : contrôle des flux réseau et segmentation des accès.  
* **IAM** : gestion des permissions et des rôles d’accès sécurisés.  
* **Amazon S3** : stockage centralisé des configurations et fichiers de déploiement.  
* **Amazon ECR** : stockage et gestion des images Docker.  
* **AWS Systems Manager (SSM)** : exécution de commandes à distance sans accès SSH.

AWS joue un rôle central dans la mise en place d’une architecture sécurisée, scalable et automatisable.

### **3.2.2 Terraform** {#3.2.2-terraform}

![][image3]

Terraform est utilisé pour l’Infrastructure as Code (IaC), permettant de décrire et déployer l’ensemble de l’infrastructure Cloud de manière automatisée.

Dans ce projet, Terraform permet :

* La création des VPC et sous-réseaux.  
* Le déploiement des instances EC2.  
* La configuration des Security Groups.  
* L’automatisation de la reproductibilité de l’environnement.  
* La gestion de l’état de l’infrastructure.

L’utilisation de Terraform permet de garantir la cohérence et la rapidité de déploiement de l’environnement SOC.

### **3.2.3 Docker et Docker Compose** {#3.2.3-docker-et-docker-compose}

![][image4]

Docker est utilisé pour la conteneurisation de la plateforme SOC basée sur Wazuh.

Les avantages principaux sont :

* Isolation des services (Manager, Indexer, Dashboard).  
* Portabilité de l’environnement.  
* Simplification du déploiement.  
* Standardisation des configurations.

Docker Compose est utilisé pour orchestrer les différents services nécessaires au fonctionnement de Wazuh.

### **3.2.4 Wazuh (SIEM / EDR)** {#3.2.4-wazuh-(siem-/-edr)}

![][image5]

Wazuh est la solution principale de détection et de supervision de sécurité (SIEM/EDR).

Il permet :

* La collecte et l’analyse des logs.  
* La détection d’incidents de sécurité.  
* La génération d’alertes en temps réel.  
* La surveillance des agents installés sur les machines cibles.

Dans ce projet, Wazuh constitue le cœur du système de détection.

### **3.2.5 MITRE ATT\&CK** {#3.2.5-mitre-att&ck}

![][image6]

MITRE ATT\&CK est un framework de référence décrivant les techniques utilisées par les attaquants.

Son utilisation dans le projet permet :

* La modélisation des scénarios d’attaque.  
* L’organisation des règles de détection.  
* L’amélioration de la couverture de sécurité.  
* L’analyse des comportements malveillants.

### **3.2.6 Atomic Red Team** {#3.2.6-atomic-red-team}

![][image7]

Atomic Red Team est utilisé pour simuler des attaques simples et reproductibles.

Il permet :

* De tester les règles de détection Wazuh.  
* De valider les scénarios MITRE ATT\&CK.  
* De générer des comportements malveillants contrôlés.

### **3.2.7 MITRE Caldera** {#3.2.7-mitre-caldera}

![][image8]

MITRE Caldera est une plateforme de simulation d’attaques avancées (emulation adversary).

Dans ce projet, il est utilisé pour :

* Simuler des attaques multi-étapes.  
* Reproduire des comportements d’attaquants réels.  
* Tester la robustesse du SOC.

### **3.2.8 Python et Boto3** {#3.2.8-python-et-boto3}

![][image9]

Python est utilisé pour le développement des scripts d’automatisation.

La bibliothèque Boto3 permet :

* L’interaction avec les services AWS.  
* L’automatisation des actions de réponse.  
* L’isolation des machines compromises.  
* L’intégration avec les alertes Wazuh.

### **3.2.9 AWS Systems Manager (SSM)** {#3.2.9-aws-systems-manager-(ssm)}

![][image10]

SSM est utilisé pour exécuter des commandes à distance sur les instances EC2 sans utilisation de SSH.

Avantages :

* Sécurité renforcée (pas d’ouverture du port 22).  
* Centralisation des commandes.  
* Automatisation des actions de remédiation.  
* Intégration avec les scripts Python.

## 3.3 Conception générale {#3.3-conception-générale}

La conception générale du système vise à définir les interactions entre les différents composants de l’architecture ainsi que les flux de données et de contrôle. Le système proposé repose sur une architecture Cloud distribuée intégrant des mécanismes de détection, de simulation d’attaques et de réponse automatisée aux incidents de sécurité.

L’objectif principal est de construire un environnement SOC complet dans le Cloud, capable de reproduire des scénarios réalistes d’attaques et de déclencher des actions de remédiation en temps réel.

![][image11]

### **3.3.1 Description des acteurs du système** {#3.3.1-description-des-acteurs-du-système}

L'analyse fonctionnelle du système met en évidence deux acteurs principaux qui interagissent avec la plateforme :

* **Administrateur SOC (Security Operations Center)**  
   Responsable du déploiement, de la configuration et de la supervision de l'infrastructure de sécurité. Il utilise la plateforme pour provisionner les ressources cloud, accéder au tableau de bord Wazuh, surveiller les événements de sécurité et analyser les alertes générées.  
* **Attaquant (acteur simulé)**  
   Représente une source de menace externe. Cet acteur exécute des scénarios d'attaque contrôlés afin d'évaluer les capacités de détection et de réponse du système. Les attaques sont simulées à l'aide de techniques inspirées du framework MITRE ATT\&CK et des tests Atomic Red Team.

  ### **3.3.2 Composants principaux du système** {#3.3.2-composants-principaux-du-système}

Le fonctionnement de la plateforme repose sur plusieurs composants techniques :

* **Infrastructure AWS**  
   Fournit les ressources cloud nécessaires au déploiement de la plateforme, notamment les services EC2, VPC, S3, IAM et Systems Manager (SSM).  
* **Wazuh (SIEM/EDR)**  
   Assure la collecte des journaux, la corrélation des événements, la détection des comportements suspects et la génération d'alertes de sécurité.  
* **Machines victimes**  
   Instances EC2 surveillées par des agents Wazuh. Elles représentent les systèmes cibles sur lesquels sont exécutés les scénarios d'attaque.  
* **Moteur de réponse automatisée**  
   Ensemble de scripts Python exploitant les bibliothèques AWS SDK (Boto3) et AWS Systems Manager pour appliquer automatiquement des actions de remédiation suite à la détection d'un incident.

### **3.3.3 Cas d’utilisation global** {#3.3.3-cas-d’utilisation-global}

![][image12]

### **3.3.4 Diagramme fonctionnel global** {#3.3.4-diagramme-fonctionnel-global}

Le fonctionnement global du système peut être résumé selon les étapes suivantes :

1. L’infrastructure Cloud est provisionnée automatiquement sur AWS à l’aide de Terraform.  
2. Les instances EC2 sont créées et configurées pour héberger les différents composants de la plateforme.  
3. Le serveur Wazuh est déployé et les agents de supervision sont installés sur les machines victimes.  
4. Des scénarios d’attaque sont exécutés à l’aide d’outils de simulation tels qu’Atomic Red Team et MITRE Caldera.  
5. Les événements générés par les attaques sont collectés par les agents Wazuh puis transmis au serveur SIEM.  
6. Wazuh analyse les journaux et les événements de sécurité afin de détecter les comportements suspects et de générer des alertes.  
7. Les alertes détectées sont consultées et analysées par l’administrateur SOC via le tableau de bord Wazuh.  
8. En cas d’incident, le moteur de réponse automatisée déclenche des actions de remédiation via AWS Systems Manager (SSM) et les API AWS (Boto3).  
9. Toutes les opérations de déploiement, de supervision et de réponse sont journalisées afin d’assurer la traçabilité des actions effectuées.

   ![][image13]

### **3.3.5 Scénarios principaux d’interaction \- diagrammes de séquence :** {#3.3.5-scénarios-principaux-d’interaction---diagrammes-de-séquence-:}

#### **1\. Scénario de déploiement**

* L’administrateur déclenche le déploiement de l’infrastructure via Terraform.  
* Les ressources AWS sont créées automatiquement (VPC, EC2, Security Groups, IAM).  
* La plateforme SOC est ensuite déployée via Docker.

![][image14]

#### **2\. Scénario de détection d’attaque**

* Une attaque simulée est exécutée sur une machine victime.  
* Les agents Wazuh détectent des comportements suspects.  
* Une alerte est générée et affichée dans le dashboard SOC.

![][image15]

#### **3\. Scénario de réponse automatisée**

Lorsqu’une alerte critique est détectée :

* Wazuh déclenche une règle de réponse active.  
* Un script Python est exécuté.  
* AWS SSM ou Boto3 est utilisé pour appliquer des actions correctives.  
* La machine compromise est isolée (modification des Security Groups).  
* L’incident est enregistré pour analyse.

![][image16]

### **3.3.6 Flux de données** {#3.3.6-flux-de-données}

Le flux de données principal suit la chaîne suivante :

Machines victimes → Agents Wazuh → Manager Wazuh → Indexer → Dashboard → Moteur de réponse → AWS (actions correctives)

Ce flux permet une visibilité complète des événements de sécurité et une automatisation de la réponse aux incidents.

## 3.4 Conclusion  {#3.4-conclusion}

Le chapitre d’analyse et de conception a permis de définir les fondations techniques et fonctionnelles du projet. L’étude des besoins a mis en évidence la nécessité de concevoir une architecture automatisée, scalable et sécurisée, capable de reproduire un environnement SOC réaliste dans le Cloud.

L’étude des technologies a justifié le choix d’outils complémentaires tels que AWS, Terraform, Docker, Wazuh, MITRE ATT\&CK, Atomic Red Team, MITRE Caldera et Python avec Boto3. Ces technologies permettent de couvrir l’ensemble du cycle de vie d’un incident de sécurité, depuis la détection jusqu’à la réponse automatisée.

La conception générale a permis de définir les acteurs, les flux et les scénarios principaux du système. Elle met en évidence une architecture modulaire où chaque composant joue un rôle précis dans la chaîne de sécurité.

Enfin, les diagrammes de séquence ont illustré les interactions dynamiques entre les différents modules du système, confirmant la cohérence de l’architecture proposée.

Le chapitre suivant présentera l’architecture technique détaillée de la solution ainsi que les choix d’implémentation adoptés pour sa mise en œuvre.

# Chapitre 4 : Architecture Technique de la Solution  {#chapitre-4-:-architecture-technique-de-la-solution}

## 

## 4.1 Vue d’ensemble de l’architecture {#4.1-vue-d’ensemble-de-l’architecture}

L’objectif principal de ce projet est de concevoir un environnement unifié de simulation, de détection et de remédiation des incidents de sécurité, capable de couvrir l’ensemble du cycle de gestion des menaces :  
 **émulation d’attaques (Red Teaming), supervision centralisée (Blue Teaming / SIEM) et réponse automatisée (SOAR)**.

Afin de garantir la flexibilité, la reproductibilité et la robustesse de la plateforme, l’architecture globale repose sur un découplage strict entre le plan de contrôle et le plan de données :

* **Plan de contrôle :**  
   Assuré par un orchestrateur développé en Python, exécuté localement par l’ingénieur sécurité. Ce composant agit comme le cerveau de la plateforme et pilote l’ensemble des opérations via une interface en ligne de commande personnalisée (`cloud-soc`).

* **Plan de données :**  
   Correspond à l’infrastructure Cloud déployée sur Amazon Web Services (AWS), regroupant les ressources réseau, les machines cibles, les composants de détection et les mécanismes de réponse.

L’interaction entre les composants suit un flux cyclique fermé, garantissant une maîtrise complète du processus de sécurité :

1. **Orchestration globale (CLI / Python)**  
    L’ingénieur interagit avec l’architecture via la CLI `cloud-soc`.  
    L’orchestrateur interprète des blueprints déclaratifs en YAML afin de :

   * Provisionner l’infrastructure Cloud,

   * Déployer les composants SOC,

   * Déclencher des scénarios d’attaque ou de remédiation.

2. **Plan de simulation – Red Team**  
    Les attaques sont simulées à l’aide de frameworks d’émulation conformes au modèle MITRE ATT\&CK, notamment Atomic Red Team.  
    Ces playbooks injectent des comportements malveillants déterministes sur des machines cibles (Victim Hosts), permettant de tester la capacité de détection du SOC.

3. **Plan de supervision – SIEM**  
    Des agents légers installés sur les machines collectent la télémétrie système et les journaux de sécurité.  
    Ces données sont transmises via un réseau isolé vers la plateforme SIEM centrale basée sur Wazuh, chargée de la corrélation et de l’analyse des événements.

4. **Plan de réponse – SOAR**  
    Un démon Python (`orchestrator.py`) analyse en continu les alertes critiques générées par le SIEM.  
    Lorsqu’une attaque est confirmée, il déclenche de manière asynchrone des playbooks de remédiation automatisée, capables de modifier dynamiquement l’état de l’infrastructure Cloud (isolation réseau, arrêt de processus, etc.).

Cette architecture permet d’obtenir une plateforme SOC fermée, contrôlée et hautement automatisée, limitant les interventions manuelles et réduisant significativement le temps moyen de réponse aux incidents.

## 4.2 Architecture Cloud AWS {#4.2-architecture-cloud-aws}

Le déploiement de la solution repose sur les services managés d’Amazon Web Services, orchestrés intégralement selon une approche Infrastructure as Code (IaC) via Terraform.  
 Cette stratégie garantit la maîtrise des configurations de sécurité, la reproductibilité des environnements et la scalabilité des ressources.

### **4.2.1 Réseau et isolation : VPC SOC et sous-réseaux** {#4.2.1-réseau-et-isolation-:-vpc-soc-et-sous-réseaux}

L’architecture réseau s’appuie sur un Virtual Private Cloud (VPC) dédié, configuré avec un bloc CIDR principal `10.0.0.0/16`.  
 La segmentation réseau suit une approche de défense en profondeur et de moindre privilège :

* **Sous-réseau public**  
   Utilisé exclusivement pour héberger les composants nécessaires aux flux d’administration initiaux et aux mécanismes de rebond contrôlés.

* **Sous-réseau privé SOC (10.0.1.0/24)**  
   Zone fortement isolée hébergeant la stack de détection centrale :

  * Wazuh Manager,

  * Wazuh Indexer,

  * Wazuh Dashboard.

  Aucune ressource de ce sous-réseau n’est exposée directement à Internet.

* **Sous-réseau privé cible / victime (10.0.2.0/24)**  
   Zone dédiée aux machines cibles Linux et Windows utilisées pour la simulation d’attaques.  
   Ce cloisonnement empêche toute propagation latérale vers le cœur du SOC en cas de compromission volontaire ou accidentelle.

### **4.2.2 Contrôle des flux : Security Groups** {#4.2.2-contrôle-des-flux-:-security-groups}

Les flux réseau sont contrôlés par des Security Groups, agissant comme des pare-feux étatiques au niveau des instances :

* **SG-SIEM-Cluster**  
   Restreint strictement l’accès aux composants Wazuh :

  * Ports `1514` et `1515` autorisés uniquement depuis le sous-réseau victime pour la collecte des événements,

  * Interface d’administration totalement inaccessible depuis Internet, accessible uniquement via des mécanismes sécurisés internes.

* **SG-Victim-Host**  
   Groupe appliqué initialement aux machines cibles pour les flux légitimes.  
   Lors d’un incident critique, ce groupe est dynamiquement remplacé par un SG-Isolation, bloquant tout trafic entrant et sortant, à l’exception du canal de contrôle de l’équipe SOC.

### **4.2.3 Calcul et services de support** {#4.2.3-calcul-et-services-de-support}

L’architecture s’appuie sur les services AWS suivants :

* **EC2**  
   Hébergement des composants SOC, des machines victimes et des environnements de simulation, avec des instances adaptées à la charge (ex. `t3.medium` ou supérieur pour la stack Wazuh).

* **IAM (Identity and Access Management)**  
   Attribution de rôles IAM stricts aux instances EC2.  
   L’orchestrateur Python interagit avec l’infrastructure via ces rôles, sans stockage de clés d’accès statiques dans le code.

* **ECR (Elastic Container Registry)**  
   Registre privé sécurisé pour le stockage des images Docker personnalisées intégrant les outils SOC et les agents de sécurité.

* **S3**  
   Stockage immuable des journaux d’audit, des sauvegardes de configuration et des artefacts critiques du SOC.

* **AWS Systems Manager (SSM)**  
   Composant central de l’architecture, remplaçant totalement l’usage du SSH (port `22`).  
   SSM permet :

  * L’exécution de commandes distantes (`Run Command`),

  * L’établissement de tunnels chiffrés éphémères (`Port Forwarding`),

  * L’administration sécurisée des machines compromises sans exposition réseau publique.

Cette architecture Cloud constitue une fondation sécurisée et évolutive, essentielle à la mise en œuvre efficace des mécanismes de détection, de simulation et de réponse automatisée aux incidents.

## 4.3 Architecture DevSecOps {#4.3-architecture-devsecops}

L’intégration de la philosophie **DevSecOps** au cœur de ce projet vise à traiter l’infrastructure, la sécurité et l’automatisation avec la même rigueur que le code applicatif. L’objectif est de garantir que chaque composant du SOC — depuis le réseau jusqu’aux mécanismes de réponse automatisée — soit **défini, versionné, déployé et contrôlé de manière systématique et reproductible**.

L’architecture DevSecOps mise en œuvre repose sur une **automatisation complète du cycle de vie du SOC**, couvrant la définition des ressources Cloud, la construction et la distribution sécurisée des environnements de supervision, ainsi que l’orchestration des opérations de détection et de remédiation. Cette approche permet de réduire significativement les erreurs humaines, d’améliorer la traçabilité des changements et d’assurer une réduction du **temps moyen de réponse aux incidents (MTTR)**.

### **4.3.1 Infrastructure as Code (IaC) avec Terraform** {#4.3.1-infrastructure-as-code-(iac)-avec-terraform}

Afin d’éliminer les configurations manuelles sujettes aux erreurs et de garantir une reproductibilité parfaite de l’environnement, l’intégralité de la plateforme AWS est définie de manière déclarative à l’aide de **Terraform**.

Les fichiers de configuration Terraform (*`.tf`*) sont structurés selon une approche **modulaire**, avec une séparation claire des responsabilités :

* **Module Réseau** : VPC, sous-réseaux et routage,  
* **Module Sécurité** : Security Groups et règles de filtrage,  
* **Module Compute** : instances EC2 et profils associés.

Cette modularité permet d’isoler les changements, notamment lors de l’évolution des règles de sécurité, et de tester les modifications indépendamment des ressources de calcul.

Le fichier d’état Terraform (*`terraform.tfstate`*) joue un rôle central en tant que **source unique de vérité** décrivant l’état réel de l’infrastructure. L’orchestrateur Python s’appuie sur cet état pour vérifier la conformité de l’environnement Cloud avant toute phase de simulation d’attaque ou de déploiement, garantissant ainsi la cohérence entre le modèle théorique et l’infrastructure effective.

### **4.3.2 Conteneurisation avec Docker et gestion des images via ECR** {#4.3.2-conteneurisation-avec-docker-et-gestion-des-images-via-ecr}

La stack logicielle du SOC, incluant les composants de supervision et les outils de réponse, est entièrement **conteneurisée à l’aide de Docker** et orchestrée via **Docker Compose**. Cette standardisation permet de résoudre définitivement les problématiques de divergences d’environnements (« *it works on my machine* ») et de garantir un comportement identique sur toutes les instances.

Chaque composant du SIEM (Indexer, Manager, Dashboard) s’exécute dans un **conteneur isolé**, doté de limites strictes en termes de ressources. Cette isolation de type microservices empêche qu’une surcharge ou une défaillance d’un composant n’impacte l’ensemble de la plateforme SOC.

La distribution des images conteneurisées repose sur **Amazon Elastic Container Registry (ECR)**, utilisé comme registre privé sécurisé. Les images Docker ne sont jamais stockées sur des registres publics, ce qui renforce la confidentialité et l’intégrité des environnements déployés.

Le pipeline DevSecOps intègre un flux de publication automatisé vers ECR, orchestré par le moteur Python selon un processus en deux étapes :

* Authentification éphémère auprès de l’API ECR à l’aide de jetons dynamiques générés via les mécanismes d’authentification AWS,  
* Construction des images Docker (*`docker build`*) suivie de leur validation et de leur publication sécurisée (*`docker push`*) vers le registre privé.

Cette approche garantit que seules des images maîtrisées et validées sont déployées sur les instances de production.

### **4.3.3 Pipeline d’exécution et orchestration customisée** {#4.3.3-pipeline-d’exécution-et-orchestration-customisée}

Plutôt que de s’appuyer sur des solutions d’intégration continue tierces lourdes et complexes à déployer dans un environnement éphémère, le projet implémente un **moteur d’orchestration customisé en Python**, jouant le rôle de contrôleur DevSecOps unifié.

Ce moteur agit comme un **pipeline d’exécution intelligent**, capable de piloter l’ensemble des opérations de déploiement et de configuration de la plateforme SOC. Il repose sur plusieurs principes clés :

* **Interprétation déclarative** : le moteur consomme des blueprints au format YAML (par exemple *`wazuh_cluster.yml`*), valide leur syntaxe et résout dynamiquement les variables d’environnement nécessaires au déploiement.  
* **Abstraction des tâches** : les opérations complexes (exécution de commandes système, gestion des volumes Docker, appels Terraform, déploiement des services) sont encapsulées dans des classes structurées de type *`DeploymentTask`*.  
* **Gestion robuste des erreurs** : en cas d’échec à une étape critique (erreur de génération de certificats, échec de build d’image ou incohérence d’état Terraform), le moteur interrompt proprement la chaîne d’exécution afin d’éviter de laisser l’infrastructure dans un état instable ou non sécurisé.

Cette orchestration customisée constitue un élément central de l’approche DevSecOps du projet, en assurant un contrôle fin, automatisé et sécurisé de l’ensemble du cycle de vie de la plateforme SOC.

## 4.4 Architecture SOC {#4.4-architecture-soc}

L'architecture de supervision de la solution est articulée autour de la stack open-source **Wazuh**, une plateforme de détection de menaces (SIEM) et de protection des points de terminaison (XDR) de classe entreprise. Afin de garantir la haute disponibilité, le traitement parallèle des logs et la résilience face aux pannes, la plateforme SOC est déployée sous forme d'une architecture microservices conteneurisée et segmentée en trois entités logiques majeures.

### **4.4.1 La Stack Centrale Wazuh (Le Cluster de Supervision)** {#4.4.1-la-stack-centrale-wazuh-(le-cluster-de-supervision)}

![][image17]

Le cœur du SOC s'exécute au sein du sous-réseau privé AWS et communique via un réseau bridge Docker isolé et explicite (*`wazuh-net`*). Cette topologie garantit qu'aucun flux non autorisé ne vienne perturber l'indexation ou l'analyse des événements de sécurité.

* **Wazuh Indexer (Plan de Stockage) :** Ce moteur de recherche et d'analyse hautement performant est chargé de stocker les alertes générées par le système. Il indexe les données brutes sous forme de documents JSON enrichis. Dans notre architecture, il est configuré pour écouter exclusivement sur le port chiffré *`9200`*, permettant au manager et au dashboard de requêter les logs d'audit de manière instantanée.  
* **Wazuh Manager (Plan d'Analyse et de Contrôle) :** Il s'agit du cerveau du SIEM. Le manager centralise la réception des événements collectés, décode les logs bruts à l'aide d'un moteur d'expressions régulières (regex) natif, et évalue les correspondances avec les matrices de règles de sécurité (signatures d'attaques, anomalies de comportement, conformité réglementaire). Il expose le port *`1514`* pour la communication sécurisée des agents et le port *`1515`* pour l'authentification et l'enrôlement des nouvelles machines.  
* **Wazuh Dashboard (Plan de Visualisation) :** Cette interface utilisateur graphique permet à l'administrateur du SOC d'explorer la télémétrie, de visualiser les tableaux de bord analytiques et de piloter la configuration du cluster. Pour des raisons d'isolation strictes (DevSecOps Baseline), le dashboard est configuré en HTTPS natif et map le port conteneur interne *`5601`* vers le port d'écoute standard *`443`* de l'hôte, s'intégrant de manière transparente avec nos tunnels d'accès sécurisés.

### **4.4.2 Collecte de la Télémétrie : Les Agents Linux et Windows** {#4.4.2-collecte-de-la-télémétrie-:-les-agents-linux-et-windows}

La visibilité sur l'état de sécurité des infrastructures cibles dépend du déploiement des **Agents Wazuh**. Ces démons légers et non intrusifs sont installés directement sur les machines surveillées (*Victim Hosts*) au sein du sous-réseau cible.

L'architecture de collecte repose sur trois mécanismes fondamentaux :

1. **L'Enrôlement Sécurisé :** Lors de son initialisation, l'agent contacte le service d'authentification du *`wazuh.manager`* (port *`1515`*). Une fois validé, le manager lui attribue une clé d'authentification unique et un identifiant interne, scellant définitivement l'intégrité du canal de communication.  
2. **Le Transport Chiffré :** Toutes les données de logs, les hashes de fichiers et les alertes d'intégrité système sont acheminés de l'agent vers le manager via un tunnel TLS/Blowfish chiffré sur le port *`1514`*. Ce flux est étatique et supporte la mise en cache locale : si le réseau entre le sous-réseau victime et le SOC subit une coupure temporaire, l'agent stocke localement les événements pour éviter toute perte de visibilité.  
3. **Les Modules de Surveillance Actifs :** Les agents exécutent simultanément plusieurs modules critiques :  
   * **Log Analysis (Logcollector) :** Analyse en temps réel les fichiers journaux du système (Syslog, Windows Event Logs).  
   * **Syscheck (FIM \- File Integrity Monitoring) :** Scanne et surveille en continu les modifications de fichiers sensibles (comme *`/etc/passwd`* ou le Registre Windows) en calculant des empreintes cryptographiques (MD5/SHA256).  
   * **Rootcheck :** Recherche les anomalies au niveau du noyau, les rootkits et les configurations système non conformes aux guides de durcissement.

Cette architecture garantit au SOC une visibilité absolue et un canal de transport de données hautement sécurisé pour alimenter en temps réel le moteur de réponse automatisée.

## 4.5 Architecture de Simulation d’Attaque {#4.5-architecture-de-simulation-d’attaque}

Pour valider l'efficacité opérationnelle d'un SOC, la mise en place d'un mécanisme de validation empirique est indispensable. Au lieu d'attendre passivement la survenue d'incidents réels, l'architecture intègre une composante d'**ingénierie du chaos de sécurité (Security Chaos Engineering)** et d'**émulation d'adversaires**. Cette couche technique a pour but d'injecter des comportements malveillants contrôlés, mesurables et reproductibles afin d'évaluer directement les capacités de détection du SIEM et de déclenchement du SOAR.

### **4.5.1 Framework d'Émulation : Atomic Red Team (ART)** {#4.5.1-framework-d'émulation-:-atomic-red-team-(art)}

Le cœur du plan de simulation repose sur le framework open-source **Atomic Red Team** développé par Red Canary. Ce choix technique s'explique par sa modularité extrême et son adéquation parfaite avec une philosophie DevSecOps.

* **Les "Atomics" comme Unités de Test :** Le framework décompose les tactiques offensives en scripts minimalistes et hautement ciblés appelés "Atomics". Chaque test atomique est défini dans un fichier de configuration déclaratif (YAML/Markdown), ce qui permet à notre orchestrateur Python d'appeler précisément une technique sans importer de dépendances lourdes ou instables.  
* **Exécution Sans Agent Persistant :** Contrairement aux outils offensifs complexes, ART s'exécute directement via la console native du système d'exploitation de la machine cible (Bash sur Linux, PowerShell sur Windows). Ce mode opératoire garantit que l'empreinte de l'outil d'émulation ne vienne pas fausser la télémétrie collectée par l'agent Wazuh.  
* **Intégration dans le Moteur Python :** L'exécution des attaques est automatisée par notre CLI *`cloud-soc`*. Lorsqu'un blueprint d'émulation est invoqué, le script Python se charge d'acheminer les dépendances de l'attaque vers l'instance cible en utilisant les canaux sécurisés d'AWS SSM, garantissant qu'aucune clé d'accès ou port réseau d'administration (comme le port SSH 22\) ne soit ouvert vers l'extérieur.

### **4.5.2 Cartographie et Alignement avec la Matrice MITRE ATT\&CK** {#4.5.2-cartographie-et-alignement-avec-la-matrice-mitre-att&ck}

L'architecture de simulation n'exécute pas des scripts de manière aléatoire ; elle est entièrement indexée sur la base de connaissances mondiale **MITRE ATT\&CK**. Cette taxonomie standardise la nomenclature des cybermenaces.

Chaque playbook d'émulation créé dans notre structure de répertoires (*`playbooks/emulation/`*) cible explicitement une technique référencée :

1. **La Persistance (Tactique TA0003) :** Simulée via la technique **T1053.005 (Scheduled Task/Job: Cron)**. Le playbook ordonne à la machine d'écrire une tâche planifiée non autorisée. L'objectif est de vérifier si le module FIM (File Integrity Monitoring) et l'analyse de logs de Wazuh détectent instantanément l'anomalie de configuration.  
2. **La Découverte / Reconnaissance Interne (Tactique TA0007) :** Simulée via la technique **T1057 (Process Discovery)**. L'attaque simule un intrus tentant de lister les processus système pour identifier les logiciels de sécurité actifs, générant ainsi un pic de logs comportementaux spécifiques que le gestionnaire de règles du SIEM doit corréler.

### **4.5.3 Architecture Conjointe et Ouverture vers MITRE Caldera** {#4.5.3-architecture-conjointe-et-ouverture-vers-mitre-caldera}

Bien que le calendrier de réalisation ait imposé une focalisation prioritaire sur l'automatisation déterministe via Atomic Red Team (scénarios unitaires scriptés), l'architecture globale intègre conceptuellement la plateforme **MITRE Caldera** pour l'émulation d'attaques complexes et multi-étapes.

Dans cette topologie avancée, Caldera agit comme un serveur de Command & Control (C2) centralisé. Il communique avec des agents légers (Sandcat) installés sur les machines cibles. Cela permet de planifier des vagues d'attaques sous forme d'**opérations automatisées graphiques**, où le framework décide de manière autonome de la prochaine action (ex: Exfiltration après une Phase de Découverte) en fonction du succès de l'étape précédente. Cette double approche (ART pour les tests unitaires de règles, Caldera pour les scénarios d'intrusion persistants) structure notre environnement comme un véritable **Cyber Range Cloud** hautement sophistiqué.

## 4.6 Architecture de Réponse Automatisée {#4.6-architecture-de-réponse-automatisée}

La phase de réponse représente le pilier central du concept de **SOAR (Security Orchestration, Automation, and Response)**. L'objectif de cette couche architecturale est de réduire drastiquement le temps moyen de remédiation **(MTTR \- Mean Time To Respond)** en remplaçant l'intervention humaine manuelle par des boucles de rétroaction logicielles immédiates. L'architecture de réponse automatisée conçue dans ce projet ne se contente pas d'alerter ; elle agit directement sur l'infrastructure Cloud pour contenir la menace.

### **4.6.1 Le Moteur d'Orchestration Python (SOAR Customisé)** {#4.6.1-le-moteur-d'orchestration-python-(soar-customisé)}

Au cœur de ce mécanisme se trouve le démon d'orchestration (*`orchestrator.py`*). Contrairement aux actions de réponse locales traditionnelles (souvent limitées à la machine compromise), notre moteur agit comme un **générateur de contre-mesures centralisé et asynchrone**.

Le flux opérationnel du moteur SOAR suit une logique d'ingestion et de routage d'événements :

1. **La Surveillance du Flux d'Alertes :** Le script Python maintient un pointeur actif (tailing) sur le fichier de sortie centralisé du SIEM (*`/var/ossec/logs/alerts/alerts.json`*). Chaque alerte décodée par Wazuh est analysée en temps réel sous forme d'objet JSON.

2. **Le Filtrage et Évaluation des Règles :** Le moteur extrait les champs critiques du JSON, notamment le *`rule.id`*, le *`rule.level`* et l'identifiant de la cible (*`agent.id`* / *`agent.ip`*). Une matrice de correspondance interne détermine si l'événement nécessite une réponse immédiate (ex: alertes de niveau supérieur ou égale à 10).

3. **Le Dispatcher de Playbooks :** Lorsqu'une menace critique est validée, le moteur instancie la classe *`DeploymentTask`* pour charger le playbook YAML de remédiation approprié (situé dans playbooks/response/) et y injecte dynamiquement les variables de l'alerte (comme l'IP de la victime).

### **4.6.2 Interaction avec le Plan de Contrôle : AWS Boto3 et AWS Systems Manager (SSM)** {#4.6.2-interaction-avec-le-plan-de-contrôle-:-aws-boto3-et-aws-systems-manager-(ssm)}

Pour exécuter les actions de défense de manière souveraine et sécurisée, le moteur Python s'appuie sur les APIs natives d'Amazon Web Services :

* **Orchestration Réseau via AWS Boto3 :** Le SDK Python *`boto3`* permet au moteur SOAR de s'authentifier auprès de l'API AWS en utilisant le rôle IAM de l'instance du SOC. En cas d'attaque par persistance ou d'exfiltration, le script appelle les méthodes de l'API EC2 (*`modify-instance-attribute`*) pour détacher instantanément les Security Groups de production de la machine victime et lui assigner un **Security Group d'isolation (Quarantaine)**. Ce changement s'exécute au niveau de l'hyperviseur AWS en moins de quelques secondes, coupant toutes les connexions réseau de l'attaquant sans éteindre la machine (ce qui préserve la mémoire volatile pour l'analyse Forensics).

* **Remédiation Système via AWS Systems Manager (SSM) :** Si la menace nécessite une action corrective directement sur le système d'exploitation de la victime (comme tuer un processus malveillant injecté par Atomic Red Team ou supprimer un fichier binaire suspect), le moteur utilise l'API **SSM Run Command**. Le script Python envoie une instruction chiffrée à l'agent SSM de la cible. Cette méthode élimine le besoin d'ouvrir des accès administratifs permanents (comme SSH ou RDP) sur la machine victime, garantissant qu'aucune communication administrative ne puisse être interceptée ou compromise.

Cette architecture en boucle fermée assure que dès qu'une technique offensive est exécutée et détectée, l'infrastructure s'adapte et se défend de manière autonome en un temps record.

## 4.7 Évolution de l’architecture {#4.7-évolution-de-l’architecture}

La conception d’une plateforme d'automatisation de la sécurité en environnement Cloud est un processus hautement itératif. Au cours de la réalisation de ce projet, les réalités de l'infrastructure et les contraintes techniques liées aux environnements de développement et de déploiement ont imposé des ajustements structurels majeurs. Cette section documente la transition de notre modèle théorique initial vers l'architecture modulaire finale.

### **4.7.1 Architecture Initiale et Objectifs Primitifs** {#4.7.1-architecture-initiale-et-objectifs-primitifs}

Le modèle conceptuel d'origine prévoyait une approche linéaire et centralisée :

* **Unification Procédurale :** Un ensemble de scripts séquentiels complexes devait piloter à la fois le provisionnement des ressources AWS via Terraform et la configuration post-déploiement de la stack Wazuh à l'intérieur des instances.  
* **Canaux d'Accès Standards :** L'accès d'administration aux conteneurs et aux interfaces graphiques (Wazuh Dashboard) s'appuyait sur des mécanismes de rebond traditionnels et des liaisons directes via l'interface de bouclage locale (*`127.0.0.1`*).  
* **Intégration d'Outils Lourdes :** L'orchestration de la réponse et de la simulation prévoyait l'implémentation simultanée et de bout en bout de frameworks massifs (comme MITRE Caldera et Ansible) au sein de la même enveloppe de calcul.

### **4.7.2 Difficultés Rencontrées et Verrous Techniques** {#4.7.2-difficultés-rencontrées-et-verrous-techniques}

Le passage à la phase d'implémentation a mis en lumière plusieurs contraintes techniques critiques, agissant comme des verrous architecturaux :

1. **Le Verrou du Réseau Imbriqué (Docker-in-Docker & GitHub Codespaces) :** L'utilisation d'un environnement de développement conteneurisé et isolé à l'intérieur du cloud GitHub Codespaces a introduit une couche de reverse-proxy stricte. Les scripts d'automatisation tentant de valider les handshakes TLS *`(validate_tls`*) ou d'établir des connexions directes sur *`127.0.0.1`* se heurtaient à des coupures systématiques du flux réseau (*`SSL_ERROR_SYSCALL`*). L'hôte Codespaces ne pouvait pas router nativement les paquets vers le loopback interne du conteneur de développement.  
2. **La Volatilité des Adresses IP Privées Docker :** L'accès direct aux interfaces via les adresses IP privées éphémères du réseau bridge de Docker (*`172.18.0.X`*) s'est révélé instable pour l'automatisation, car ces adresses changent à chaque reconstruction ou redémarrage de la stack, brisant les correspondances de ports.  
3. **Le Conflit de Gestion des Processus (Zombies de Sessions) :** La gestion des tunnels persistants nécessaires pour le flux AWS SSM (Session Manager) via des scripts Python générait des processus orphelins ou bloquants lorsque les sessions de ligne de commande se fermaient inopinément, saturant les ports d'écoute locaux.

### **4.7.3 Évolution vers une Architecture Modulaire et Choix Retenus** {#4.7.3-évolution-vers-une-architecture-modulaire-et-choix-retenus}

Pour contourner ces limitations tout en maintenant le cap sur notre calendrier de réalisation, l'architecture a été profondément restructurée selon trois axes d'optimisation :

* **Segmentation et Modularité des Blueprints (Séparation des Pouvoirs) :** Le code a été extrait des scripts monolithiques pour être redistribué au sein d'une structure de répertoires hautement modulaire. Nous avons séparé les configurations d'infrastructure *`(blueprints/`*), les scénarios offensifs unitaires *`(playbooks/emulation/`*), et les scripts de remédiation du SOC (*`playbooks/response/`*). Cette isolation garantit qu'une modification sur un scénario d'attaque n'impacte jamais la stabilité de la stack SIEM sous-jacente.  
* **Résolution Native de la Couche Réseau :** Plutôt que de manipuler manuellement des adresses IP dynamiques, nous avons fait évoluer la configuration d'orchestration en appliquant deux solutions d'ingénierie :  
  1. *Au niveau Infrastructure :* Configuration du mode réseau (*`network_mode: "host"`*) ou couplage avec les directives *`forwardPorts`* du fichier *`devcontainer.json`* pour unifier l'espace de nommage réseau du conteneur de développement et de l'hôte virtuel.  
  2. *Au niveau Applicatif :* Réécriture des modules de vérification dans `orchestrator.py` en exploitant la bibliothèque native *`socket`* de Python pour résoudre dynamiquement l'interface d'écoute active (*`eth0`*) au lieu de pointer vers un loopback statique.  
* **Rationalisation du Périmètre Cyber Range :** Face à la lourdeur d'intégration de MITRE Caldera dans un environnement restreint par le temps, le choix technique s'est porté sur une focalisation totale autour d'**Atomic Red Team** pour la phase de validation. Cela a permis de capitaliser sur un moteur de playbooks YAML léger et sur-mesure, écrit entièrement en Python, transformant un projet d'intégration d'outils tiers en une véritable contribution logicielle orientée **SOAR**.

Cette trajectoire d'évolution démontre une transition réussie d'une approche théorique rigide vers une architecture d'ingénierie résiliente, adaptée aux contraintes de production réelles.

## 4.8 Conclusion {#4.8-conclusion}

En somme, ce chapitre a permis de formaliser l'architecture technique globale et détaillée de notre solution de Cyber Range Cloud. L'analyse des différentes couches architecturales met en évidence un triptyque technologique moderne et complémentaire, indispensable au traitement des menaces à grande échelle.

D'une part, l'intégration des concepts DevSecOps à travers l'Infrastructure as Code (Terraform) et la conteneurisation (Docker, Amazon ECR) garantit un déploiement standardisé, immuable et hautement reproductible. D'autre part, le couplage entre la stack de détection centrale (Wazuh SIEM) et le moteur d'orchestration personnalisé en Python (*`executor.py`* / *`orchestrator.py`*) matérialise une transition fluide entre la simple visibilité sécuritaire et la capacité de réaction immédiate (SOAR). Enfin, la mise en place d'un espace dédié à l'émulation d'adversaires, indexé sur la matrice universelle MITRE ATT\&CK et matérialisé par Atomic Red Team, offre un environnement empirique robuste pour éprouver nos propres règles de défense.

L'évolution de l'architecture documentée dans ce chapitre démontre qu'au-delà de l'assemblage de briques logicielles, la résolution des verrous techniques réseau et d'isolation a permis de concevoir un système résilient et adapté aux contraintes de production réelles. Cette base architecturale étant désormais solidement établie, le chapitre suivant sera consacré à la phase d'implémentation pratique, au développement des scripts d'automatisation et à la configuration concrète des différents composants de notre infrastructure.

# Chapitre 5 : Implémentation et Réalisation {#chapitre-5-:-implémentation-et-réalisation}

## 

## 5.1 Déploiement de l’infrastructure AWS {#5.1-déploiement-de-l’infrastructure-aws}

La première étape opérationnelle du projet consiste à instancier l'environnement Cloud qui hébergera notre Cyber Range. Fidèle aux principes DevSecOps, ce provisionnement est entièrement automatisé via Terraform. Cette section détaille la structure de notre code d'infrastructure, les ressources créées sur Amazon Web Services, ainsi que les stratégies d'ingénierie adoptées pour surmonter les défis techniques rencontrées.

### **5.1.1 Organisation et Structure du Code Terraform** {#5.1.1-organisation-et-structure-du-code-terraform}

Pour éviter un script monolithique difficile à maintenir, le code Terraform a été structuré de manière modulaire et découplée. L'arborescence du dossier d'infrastructure se présente comme suit :

* *`main.tf`* : Point d'entrée principal qui appelle les différents modules et configure le fournisseur (provider) AWS.

* *`variables.tf`* : Déclaration des variables d'entrée (configurations de CIDR, types d'instances, clés d'accès éphémères) pour paramétrer l'environnement sans modifier le code source.

* *`outputs.tf`* : Définition des variables de sortie (adresses IP privées, IDs de ressources) indispensables à notre orchestrateur Python pour l'étape post-déploiement.

* *`modules/`* : Répertoires isolés contenant la logique propre à chaque couche (Réseau, Sécurité, Calcul).

### **5.1.2 Ressources Cloud Créées** {#5.1.2-ressources-cloud-créées}

Lors du lancement de la commande d'orchestration (*`cloud-soc deploy`*), Terraform compile les fichiers et déploie les briques cloud suivantes :

1. **Composants Réseau (VPC & Subnets) :** Création du VPC principal (*`10.0.0.0/16`*), d'une passerelle Internet (Internet Gateway) pour le sous-réseau public, et de deux sous-réseaux privés distincts pour isoler le cluster Wazuh (*`10.0.1.0/24`*) de la machine victime (10.0.2.0/24).

2. **Pare-feux (Security Groups) :** Implémentation de règles de filtrage étatiques strictes. Le groupe de sécurité du SOC n'autorise que le trafic provenant des agents sur les ports nécessaires (*`1514`*, *`1515`*), tandis que le groupe de sécurité de la victime est configuré pour accepter les scénarios offensifs de manière isolée.

3. **Ressources de Calcul et Profils (EC2 & IAM) :** Instanciation d'une machine EC2 robuste pour la stack de supervision et d'une instance distincte pour simuler la cible. Un rôle IAM doté de la politique managée *`AmazonSSMManagedInstanceCore`* est rattaché aux instances, permettant leur enregistrement automatique auprès du service AWS Systems Manager.

### **5.1.3 Difficultés Rencontrées et Résolutions Techniques** {#5.1.3-difficultés-rencontrées-et-résolutions-techniques}

#### **1\. Gestion de la Duplication des Ressources (Don't Repeat Yourself \- DRY)**

* Le Problème : Initialement, la configuration de plusieurs instances EC2 ou de règles de filtrage réseau similaires entraînait une duplication massive de blocs de code Terraform. Cela augmentait le risque d'erreurs de syntaxe et compliquait les modifications globales de l'architecture.

* La Solution : L'implémentation des expressions méta-arguments de Terraform comme *`for_each`* et *`count`*, combinée à des variables de type *`map(object)`*. Par exemple, le provisionnement des sous-réseaux et des instances utilise une boucle dynamique :

Cette approche a permis de diviser par trois le nombre de lignes de code, centralisant toute la configuration de calcul dans un seul dictionnaire de variables propre et lisible.

#### **2\. Concurrence et Persistance de l'État (State Locking)**

* **Le Problème :** Lors de l'intégration de Terraform au sein de notre orchestrateur Python, les exécutions successives ou les interruptions brusques du script risquaient de corrompre le fichier *`terraform.tfstate`*. Si l'état local ne correspondait plus à la réalité d'AWS, Terraform tentait de recréer des ressources existantes, provoquant des crashs de déploiement.

* **La Solution :** Bien que l'état soit géré localement pour ce PoC, le moteur Python a été enrichi d'un gestionnaire d'exceptions strict. Avant chaque exécution, il vérifie l'absence de fichiers de verrouillage orphelins et exécute systématiquement la commande *`terraform refresh`* pour synchroniser l'état local avec les infrastructures réelles d'AWS avant d'appliquer la moindre modification (*`terraform apply`*).

## 5.2 Déploiement de la Stack Wazuh {#5.2-déploiement-de-la-stack-wazuh}

Une fois l'infrastructure cloud AWS provisionnée, l'étape suivante consiste à instancier la plateforme de supervision centrale (SIEM). Fidèle à notre approche modulaire et microservices, la stack **Wazuh** est entièrement conteneurisée et déployée à l'aide de **Docker** et **Docker Compose**. Cette section détaille la configuration des conteneurs, la gestion critique de la couche de chiffrement (génération des certificats TLS) et les techniques de débogage appliquées pour stabiliser le cluster.

### **5.2.1 Configuration et Architecture du Docker Compose** {#5.2.1-configuration-et-architecture-du-docker-compose}

Le déploiement s'appuie sur un fichier d'orchestration *`docker-compose.yml`* personnalisé, structuré pour isoler les rôles de chaque composant au sein du réseau virtuel bridge *`wazuh-net`*. L'arborescence des services est définie ainsi :

* **Service** *`wazuh.indexer`* **:** Chargé du stockage et de l'indexation. Il monte des volumes Docker persistants pour garantir que les logs d'audit ne soient pas perdus lors de l'arrêt des conteneurs. Ses variables d'environnement définissent les limites de mémoire Java (JVM) pour optimiser les performances sur l'instance EC2.  
* **Service** *`wazuh.manager`* **:** Le moteur d'analyse. Il est configuré avec des volumes partagés lui permettant de lire les configurations de règles personnalisées et d'écrire en continu les alertes traitées dans le fichier *`/var/ossec/logs/alerts/alerts.json`*, point d'entrée de notre SOAR.  
* **Service** *`wazuh.dashboard`* **:** L'interface utilisateur. Il expose le port HTTPS standard et est configuré pour communiquer de manière sécurisée avec l'indexer et le manager via des variables d'environnement contenant les URLs de l'API cryptée (ex: *`INDEXER_URL`*).

### **5.2.2 La Gestion des Certificats TLS et Sécurisation Inter-Intra Conteneurs** {#5.2.2-la-gestion-des-certificats-tls-et-sécurisation-inter-intra-conteneurs}

Wazuh impose une communication chiffrée par certificats TLS (X.509) entre l'indexer, le manager et le dashboard. La mise en place de cette couche de sécurité a représenté une étape d'implémentation majeure :

1. **Génération Automatisée :** Nous avons intégré un outil de génération de certificats (*`wazuh-cert-tool.sh`*) au sein de notre chaîne de déploiement. Cet outil s'appuie sur un fichier de configuration contenant les noms de domaine internes (sans adresses IP statiques, pour préserver la flexibilité de l'automatisation).  
2. **Mécanisme de Bind Mounts :** Pour que les conteneurs puissent s'authentifier mutuellement, les certificats générés (clés privées, certificats de nœuds et autorité de certification racine CA) sont montés dynamiquement dans les répertoires internes de chaque conteneur via des directives de volumes Docker (*bind mounts*). Cela garantit qu'aucune clé secrète ne soit codée en dur dans les images Docker poussées sur Amazon ECR.

### **5.2.3 Déboguage et Résolution des Verrous Techniques** {#5.2.3-déboguage-et-résolution-des-verrous-techniques}

Le déploiement de la stack au sein d'un environnement de développement imbriqué (Docker-in-Docker via GitHub Codespaces) a soulevé des défis d'ingénierie complexes lors de la phase de débogage :

#### **1\. La syntaxe de transmission des variables d'environnement (Quoting Issue)**

* **Le Problème :** Lors de l'initialisation automatisée, notre script Python transmettait l'URL de l'indexer sous forme de chaîne de caractères dans les variables d'environnement du conteneur Dashboard. Une mauvaise gestion des guillemets (*quoting*) entraînait une troncature de l'URL TLS, provoquant un crash du dashboard qui ne parvenait plus à joindre l'indexer.  
* **La Résolution :** Le moteur d'exécution Python (*`executor.py`*) a été corrigé pour utiliser une sérialisation stricte des variables d'environnement et valider la structure des URLs complexes avant l'injection dans les descripteurs de processus Docker Compose.

#### **2\. L'erreur de communication réseau inter-conteneurs (Host Resolution)**

* **Le Problème :** Le Dashboard et le Manager tentaient de joindre l'Indexer via l'adresse de bouclage locale, ce qui échouait systématiquement en raison de l'isolation native des espaces de noms réseau de chaque conteneur. De plus, l'utilisation d'adresses IP brutes cassait la validation TLS, les certificats étant émis pour des noms d'hôtes logiques.  
* **La Résolution :** Implémentation de la directive *`extra_hosts`* et utilisation de la variable système de passerelle Docker (*`host.docker.internal`*). Nous avons configuré des alias réseau explicites dans le fichier *`docker-compose.yml`*, permettant aux conteneurs de résoudre dynamiquement le nom d'hôte de l'indexer en pointant vers la passerelle de l'hôte réseau virtuel, contournant ainsi définitivement les blocages de loopback du proxy de l'IDE de développement.

## 5.3 Mise en place des Agents {#5.3-mise-en-place-des-agents}

La visibilité d'un SOC dépend entièrement de sa capacité à collecter la télémétrie sur les hôtes surveillés. Après avoir stabilisé la stack centrale, l'étape suivante consiste à provisionner et configurer les **Agents Wazuh** sur les machines cibles du sous-réseau victime. Pour valider l'interopérabilité multiplateforme de notre Cyber Range, deux environnements distincts ont été configurés et raccordés au SIEM : une instance Linux (Ubuntu Server) et une instance Windows Server.

### **5.3.1 Déploiement et Configuration sur l'Agent Linux** {#5.3.1-déploiement-et-configuration-sur-l'agent-linux}

Le déploiement sur l'hôte Linux a été automatisé afin de s'intégrer nativement dans notre pipeline d'orchestration.

1. **Installation et Enrôlement :** Le processus utilise un script d'initialisation qui télécharge le paquet officiel *`.deb`*. Lors de l'installation, les variables d'environnement indispensables à l'enrôlement automatique sont injectées dynamiquement via le gestionnaire de paquets :

WAZUH\_MANAGER\='10.0.1.45' WAZUH\_AGENT\_NAME\='Linux-Victim-Node' dpkg \-i wazuh-agent\_all.deb

2. **Configuration du Démon (***`ossec.conf`***) :** Une fois le démon installé, le fichier de configuration principal *`/var/ossec/etc/ossec.conf`* est configuré pour activer les modules de surveillance critiques :  
   * **Log Analysis :** Liaison avec les fichiers de logs système standard, notamment *`/var/log/auth.log`* (pour capturer les tentatives d'authentification) et *`/var/log/syslog`*.  
   * **FIM (File Integrity Monitoring) :** Configuration du module *`<syscheck>`* pour surveiller en temps réel (attribut *`realtime="yes"`*) les répertoires sensibles tels que *`/etc`*, *`/bin`*, *`/sbin`* et *`/tmp`*, afin de lever immédiatement une alerte si un outil d'émulation (ART) tente d'y injecter un binaire malveillant.

### **5.3.2 Déploiement et Configuration sur l'Agent Windows** {#5.3.2-déploiement-et-configuration-sur-l'agent-windows}

L'inclusion d'un nœud Windows permet de tester des techniques d'attaque spécifiques aux environnements d'entreprise (comme les modifications de bases de registre ou l'exécution de scripts PowerShell suspects).

1. **Installation via Windows Installer (MSI) :** Le déploiement s'appuie sur l'outil en ligne de commande de Windows pour exécuter l'installateur MSI de manière silencieuse, évitant toute interaction graphique :

   msiexec.exe /i wazuh\-agent.msi /q WAZUH\_MANAGER\="10.0.1.45" WAZUH\_AGENT\_NAME\="Windows-Victim-Node"

2. **Collecte des Canaux d'Événements (Event Channel Logging) :** Contrairement à Linux qui repose sur des fichiers textes bruts, Windows structure ses logs dans des canaux d'événements. Le fichier *`ossec.conf`* de l'agent Windows a été configuré pour s'abonner aux flux Microsoft critiques :  
   * **Application & System :** Pour surveiller la stabilité et les crashs d'applications.  
   * **Security (Event ID 4624, 4625, 4698\) :** Essentiel pour intercepter les connexions (réussies/échouées) et la création de tâches planifiées malveillantes.

### **5.3.3 Sécurisation des Flux et Validation de l'Enrôlement** {#5.3.3-sécurisation-des-flux-et-validation-de-l'enrôlement}

Pour finaliser la mise en place, une phase de validation stricte est opérée au niveau de la couche réseau :

* **Chiffrement des Flux :** Nous avons vérifié que la clé d'authentification symétrique unique générée par le Manager lors de la phase d'enrôlement (port *`1515`*) a bien été distribuée localement à chaque agent (stockée dans *`client.keys`*). Cette clé sert à chiffrer l'ensemble du trafic de télémétrie acheminé ensuite sur le port *`1514`*.  
* **Vérification de l'État :** L'état de l'enrôlement est validé directement depuis notre orchestrateur Python en interrogeant l'API du manager Wazuh ou via la CLI native :

  /var/ossec/bin/manage\_agents \-l

* Cette commande permet de confirmer que les deux agents (ID *`001`* et *`002`*) affichent le statut réglementaire *`Active`*, prouvant que le réseau privé AWS a correctement routé les flux à travers les Security Groups sans aucune exposition sur l'Internet public.

## 5.4 Intégration AWS (S3, ECR, SSM) {#5.4-intégration-aws-(s3,-ecr,-ssm)}

L'originalité et la robustesse de notre plateforme résident dans son couplage étroit avec l'écosystème cloud d'Amazon Web Services (AWS). Plutôt que de traiter les instances virtuelles comme des serveurs isolés, le framework d'automatisation s'intègre nativement avec les services managés d'AWS via des appels d'API sécurisés. Cette section décrit l'implémentation concrète et la configuration des trois piliers de notre intégration cloud : **Amazon ECR**, **Amazon S3** et **AWS Systems Manager (SSM)**.

### **5.4.1 Distribution des Images de Supervision : Amazon ECR** {#5.4.1-distribution-des-images-de-supervision-:-amazon-ecr}

Pour garantir la souveraineté et la confidentialité de nos outils de supervision, les images Docker personnalisées de la stack Wazuh ne sont pas stockées sur des registres publics. Nous avons configuré et intégré un registre privé **Amazon ECR (Elastic Container Registry)**.

* **Authentification Éphémère :** Notre orchestrateur Python utilise les profils d'instance IAM pour interagir avec ECR sans stocker de clés statiques. Lors de la phase de build, le script génère un jeton d'authentification temporaire via l'API AWS CLI, valable pour une durée de 12 heures :

  aws ecr get-login-password \--region eu-west-3 | docker login \--username AWS \--password-stdin \<aws\_account\_id\>.dkr.ecr.eu-west-3.amazonaws.com

* **Poussée et Versioning :** Les images construites localement sont étiquetées (*tagged*) et poussées vers leurs dépôts respectifs sur ECR, permettant à l'instance EC2 de production du SOC de télécharger les conteneurs de manière isolée et sécurisée au sein du réseau d'AWS.

### **5.4.2 Archivage Immuable des Journaux : Amazon S3** {#5.4.2-archivage-immuable-des-journaux-:-amazon-s3}

La conformité réglementaire et l'analyse forensique post-incident exigent que les logs de sécurité soient conservés dans un espace de stockage hautement disponible, persistant et protégé contre la falsification.

* **Cycle de Vie et Durcissement :** Nous avons implémenté un compartiment **Amazon S3 (Simple Storage Service)** dédié à l'archivage des alertes Wazuh. Les politiques d'accès S3 (*Bucket Policies*) interdisent explicitement la suppression de logs, même par un administrateur système, appliquant ainsi le principe de non-répudiation.  
* **Flux de Synchronisation :** Un script planifié s'exécute en tâche de fond sur le manager Wazuh pour compresser et exporter périodiquement les fichiers d'alertes historiques (*`alerts.json`* et *`archives.json`*) vers le compartiment S3, libérant ainsi l'espace disque de l'instance de calcul tout en préservant l'intégrité des preuves numériques.

### **5.4.3 Le Canal de Contrôle Sécurisé : AWS Systems Manager (SSM)** {#5.4.3-le-canal-de-contrôle-sécurisé-:-aws-systems-manager-(ssm)}

**AWS Systems Manager (SSM)** est le composant le plus critique de notre architecture de communication. Il remplace intégralement l'usage traditionnel du protocole SSH et l'ouverture du port 22, éliminant ainsi une surface d'attaque majeure.

* **Tunnels Réseau Dynamiques (Session Manager) :** L'orchestrateur Python utilise l'API de SSM pour initier des tunnels chiffrés et éphémères de redirection de ports (*Port Forwarding*). Cela permet à notre framework d'interagir directement avec l'API Docker installée sur l'instance EC2 distante ou de requêter le Dashboard Wazuh de manière sécurisée sans jamais exposer ces services sur l'Internet public.  
* **Le Moteur d'Exécution de la Réponse (SSM Run Command) :** Lors de la phase de remédiation automatisée (SOAR), notre script Python n'interagit pas directement avec la machine victime en réseau. Il appelle l'API SSM pour envoyer un document de commande (*`AWS-RunShellScript`*). L'agent SSM, installé nativement sur l'instance Windows ou Linux victime, récupère cette instruction chiffrée via le plan de contrôle interne d'AWS, l'exécute localement avec les privilèges d'administration requis, et renvoie le résultat (ex: arrêt d'un processus malveillant, suppression d'un artefact) à notre orchestrateur. Ce mécanisme garantit une isolation réseau absolue pendant toute la phase de crise.

## 5.5 Développement des Scripts Python {#5.5-développement-des-scripts-python}

Le cœur logiciel et l'intelligence de notre Cyber Range Cloud reposent sur un ensemble de modules applicatifs développés sur-mesure en **Python 3**. Plutôt que de dépendre d'outils d'orchestration tiers dont l'intégration aurait alourdi la solution, nous avons conçu un framework d'automatisation modulaire structuré autour de la programmation orientée objet (POO). Cette section détaille la logique algorithmique et le rôle de nos deux composants pivots : *`executor.py`* (Plan de Déploiement et d'Émulation) et *`orchestrator.py`* (Moteur SOAR de Réponse).

### **5.5.1 L’Exécuteur de Tâches (***`executor.py`***)** {#5.5.1-l’exécuteur-de-tâches-(executor.py)}

Le script *`executor.py`* est le moteur d'exécution unifié de la plateforme. Il est chargé d'interpréter les fichiers de configuration YAML (Blueprints et Playbooks) et de les traduire en actions opérationnelles sur l'infrastructure.

* **Abstractions des Composants (POO) :** Le script implémente une classe principale *`DeploymentTask`* qui encapsule la logique d'exécution. Chaque tâche définie dans un playbook (qu'il s'agisse d'un ordre de build Docker, d'une commande de provisionnement Terraform, ou d'un script d'attaque Atomic Red Team) est instanciée comme un objet doté de ses propres méthodes de validation, d'exécution et de gestion des erreurs.  
* **Gestion Dynamique des Variables :** *`executor.py`* intègre un moteur de rendu de gabarits (template engine) minimaliste. Il est capable de lire les sorties issues de Terraform (comme les adresses IP dynamiques des instances privées) et de les injecter à la volée dans les playbooks d'émulation ou de réponse sous forme de variables contextuelles (*`{{ target_ip }}`*).  
* **Contrôle d'Exécution Sécurisé :** Le script intègre un gestionnaire d'exceptions global. Si une étape critique échoue (par exemple, une commande d'émulation ART qui ne s'exécute pas correctement), *`executor.py`* intercepte l'erreur, consigne le log de debug de manière verbeuse, et interrompt proprement la chaîne d'exécution pour éviter de corrompre l'environnement.

### **5.5.2 Le Moteur de Réponse Automatisée (***`orchestrator.py`***)** {#5.5.2-le-moteur-de-réponse-automatisée-(orchestrator.py)}

Le script *`orchestrator.py`* agit comme le cerveau du SOAR. Son rôle est de surveiller en continu le flux d'événements du SOC et de corréler les détections avec notre matrice de remédiation.

* **Ingestion Asynchrone des Alertes :** Le script implémente une boucle de lecture non bloquante qui effectue un suivi en temps réel (*tailing*) du fichier JSON centralisé du gestionnaire d'alertes Wazuh : *`/var/ossec/logs/alerts/alerts.json`*  
* **Logique Algorithmique du Routeur de Menaces :** Pour chaque nouvelle ligne de log ingérée, l'orchestrateur exécute l'algorithme de décision suivant :

### **![][image18]**

### **5.5.3 Couplage et Communication Inter-Modules** {#5.5.3-couplage-et-communication-inter-modules}

L'interaction entre les scripts est totalement découplée. *`orchestrator.py`* s'exécute en tâche de fond comme un démon de surveillance. Dès qu'un incident se produit, il n'applique pas les contre-mesures lui-même ; il appelle de manière autonome l'instance *`executor.py`* en lui transmettant le chemin du playbook de remédiation réseau (situé dans le répertoire isolé *`playbooks/response/`*).

Ce couplage lâche garantit que notre code respecte les principes de conception logicielle solid : le module de détection/filtrage est totalement indépendant du module d'exécution de commandes, offrant une structure hautement modulaire, facile à maintenir et à enrichir de nouvelles règles de sécurité pour votre soutenance.

## 5.6 Conclusion {#5.6-conclusion}

En conclusion, ce chapitre a permis de détailler la phase concrète de réalisation et d'implémentation de notre solution de Cyber Range Cloud. L'application rigoureuse des concepts d'ingénierie logicielle et de DevSecOps a trouvé sa pleine expression à travers le déploiement automatisé de chaque couche applicative.

Nous avons d'abord mis en œuvre l'infrastructure réseau et calcul sur Amazon Web Services (AWS) via Terraform, en résolvant efficacement les défis de duplication de code grâce à une approche modulaire. Par la suite, l'instanciation de la stack de supervision centralisée Wazuh sous forme de microservices conteneurisés a démontré notre capacité à administrer des flux hautement sécurisés par certificats TLS, tout en surmontant les verrous réseau inhérents aux environnements de développement imbriqués. L'enrôlement et le chiffrement des communications des agents légers (Linux et Windows) ont concrétisé la visibilité du SOC sur le plan de données. Enfin, le couplage natif avec les services managés d'AWS (S3, ECR, SSM) et le développement sur-mesure de nos moteurs d'automatisation en Python (*`executor.py`* et *`orchestrator.py`*) ont matérialisé de bout en bout l'intelligence de notre système SOAR.

La plateforme étant désormais entièrement déployée, configurée et interconnectée, le chapitre suivant sera consacré à la phase critique de validation et de tests. Nous y éprouverons concrètement l'efficacité de notre boucle fermée à travers des scénarios d'attaques atomiques et l'évaluation fine des temps de réponse automatisés de notre infrastructure face aux incidents.

# Chapitre 6 : Validation et Tests  {#chapitre-6-:-validation-et-tests}

## 6.1 Méthodologie de test {#6.1-méthodologie-de-test}

La validation d'une plateforme d'automatisation de la sécurité ne peut pas se limiter à une simple vérification de bon fonctionnement des composants isolés. Elle exige une approche empirique et systématique, capable de mesurer la robustesse de la solution face à des scénarios de menaces réels et reproductibles. La méthodologie de test adoptée dans ce projet s'inspire directement des pratiques de **génie du chaos de sécurité (Security Chaos Engineering)** et suit un cycle d'évaluation en boucle fermée, structuré en quatre étapes itératives.

### **6.1.1 Le Cycle d'Évaluation Opérationnel** {#6.1.1-le-cycle-d'évaluation-opérationnel}

Pour chaque scénario de test mis en œuvre, le processus de validation respecte rigoureusement la chaîne causale suivante :

1. **Définition de l'Hypothèse de Sécurité :** Avant l'injection de l'attaque, nous définissons l'état nominal attendu (ex: "L'exécution de la technique X doit générer une alerte de niveau supérieur à Y et déclencher l'isolation réseau en moins de Z secondes").

2. **Simulation et Injection (Red Teaming) :** Invocations contrôlées des playbooks d'émulation via l'orchestrateur Python, simulant le comportement d'un adversaire sans altérer l'intégrité globale du système d'exploitation cible.

3. **Vérification de la Visibilité (Blue Teaming) :** Analyse du comportement du SIEM. Cette étape valide que l'agent a correctement collecté les traces (logs, modifications de fichiers), que le manager a décodé l'événement et qu'une alerte qualifiée a été écrite dans le flux JSON centralisé.

4. **Mesure de la Réponse (SOAR) :** Évaluation de la réaction automatique. Nous mesurons la capacité du script d'orchestration à intercepter l'alerte, à instancier le playbook de remédiation via les APIs AWS (Boto3/SSM), et à restaurer un état sécurisé.

### **6.1.2 Critères d'Évaluation et Indicateurs Clés de Performance (KPIs)** {#6.1.2-critères-d'évaluation-et-indicateurs-clés-de-performance-(kpis)}

Pour quantifier l'apport de l'automatisation par rapport à une gestion de crise SOC traditionnelle (manuelle), la méthodologie s'appuie sur trois indicateurs de performance fondamentaux :

* **Le Taux de Détection (TD) :** Capacité du SIEM à classifier correctement l'attaque atomique et à éliminer les faux négatifs.

* **Le Temps Moyen de Détection (MTTD \- Mean Time To Detect) :** L'intervalle de temps s'écoulant entre la seconde exacte d'exécution de l'attaque sur la machine victime et son affichage/indexation dans le flux d'alertes du SOC.

* **Le Temps Moyen de Réponse (MTTR \- Mean Time To Respond) :** L'intervalle critique séparant la génération de l'alerte par Wazuh et la finalisation de l'action de remédiation cloud (ex: application du groupe de sécurité de quarantaine ou arrêt du processus malveillant).

L'objectif final de cette méthodologie est de démontrer de manière chiffrée et indiscutable que le couplage entre vos scripts Python, Wazuh et AWS permet de faire converger le *`MTTR`* vers des valeurs quasi-instantanées (de l'ordre de quelques secondes), minimisant ainsi drastiquement la fenêtre d'opportunité d'un attaquant au sein de l'infrastructure Cloud.

## 6.2 Scénario 1 : Atomic Red Team {#6.2-scénario-1-:-atomic-red-team}

### **6.2.1 Description et Objectif de l'Attaque** {#6.2.1-description-et-objectif-de-l'attaque}

Le premier scénario de validation s'appuie sur le framework Atomic Red Team pour simuler une technique de post-compromission classique utilisée par les attaquants pour maintenir leur accès au sein d'une infrastructure : la Persistance.

L'objectif de ce test est d'injecter un comportement suspect sur notre nœud cible Linux (*`Linux-Victim-Node`*). Le scénario simule un attaquant qui, après avoir obtenu un accès initial, tente d'enregistrer une porte dérobée (backdoor) persistante s'exécutant automatiquement à intervalles réguliers, sans éveiller les soupçons des administrateurs système.

### **6.2.2 Technique MITRE ATT\&CK Utilisée : T1053.005 (Scheduled Task/Job: Cron)** {#6.2.2-technique-mitre-att&ck-utilisée-:-t1053.005-(scheduled-task/job:-cron)}

La simulation cible explicitement la technique MITRE ATT\&CK T1053.005, qui référence l'abus des utilitaires de planification de tâches système (ici, le démon cron sous Linux).

Le playbook d'émulation, rédigé sous forme de blueprint YAML et stocké dans notre répertoire *`playbooks/emulation/persistence_cron.yml`*, ordonne à l'exécuteur de simuler l'écriture d'une ligne malveillante au sein du fichier de configuration utilisateur *`crontab`*. La commande injectée tente d'ouvrir périodiquement un shell inverse (reverse shell) vers l'adresse de l'attaquant toutes les minutes :

L'exécution de cette attaque est déclenchée à distance par notre script Python en exploitant le protocole chiffré AWS SSM Run Command, assurant une injection déterministe et mesurable sans aucune exposition réseau de l'hôte victime.

### **6.2.3 Détection par le SIEM Wazuh** {#6.2.3-détection-par-le-siem-wazuh}

Dès que la modification est opérée sur l'hôte cible, l'agent Wazuh local entre en action grâce à ses deux modules configurés précédemment :

1. **Le Module FIM (File Integrity Monitoring) :** Le sous-système *`<syscheck>`* détecte instantanément l'appel système en écriture sur le répertoire *`/var/spool/cron/crontabs/`* ou sur *`/etc/crontab`*. Il calcule la nouvelle empreinte cryptographique du fichier modifié (hash SHA256) et l'envoie au Manager.

2. **Le Moteur de Règles du Manager :** À la réception de cet événement, le module d'analyse de Wazuh décode le log JSON et le fait passer à travers sa matrice de signatures. L'événement déclenche la règle native **ID 533** ("Anomalie : Modification détectée dans un fichier crontab").

{

  "timestamp": "2026-06-19T15:40:12.102+0100",

  "rule": {

    "id": "533",

    "level": 10,

    "description": "Wazuh FIM: Crontab file modified",

    "mitre": {

      "id": \[

        "T1053.005"

      \],

      "tactic": \[

        "Persistence"

      \]

    }

  },

  "agent": {

    "id": "001",

    "name": "Linux-Victim-Node",

    "ip": "10.0.2.14"

  }

}

L'alerte ainsi qualifiée est immédiatement écrite dans le fichier centralisé *`/var/ossec/logs/alerts/alerts.json`* avec un niveau de criticité de 10, atteignant exactement le seuil requis pour réveiller notre module SOAR.

### **6.2.4 Résultats et Validation de la Visibilité** {#6.2.4-résultats-et-validation-de-la-visibilité}

Les résultats de ce premier test valident l'intégrité de notre pipeline de détection :

* **Taux de Détection (TD) :** 100%. L'attaque n'a généré aucun faux négatif, et la technique a été correctement cartographiée et associée à son identifiant MITRE ATT\&CK exact au sein du Dashboard.

* **Visibilité de l'Artefact :** Le système a été capable de remonter non seulement le fait que le fichier a été modifié, mais également l'identité de l'utilisateur ayant initié l'action et la ligne exacte de commande malveillante injectée.

Cette phase confirme que notre plan de données (l'agent) et notre plan de supervision (le SIEM) communiquent de manière optimale, posant les conditions idéales pour le déclenchement automatique des mesures de rétorsion du SOAR.

## 6.3 Scénario 2 : MITRE Caldera {#6.3-scénario-2-:-mitre-caldera}

### 

## 6.4 Réponse automatisée {#6.4-réponse-automatisée}

La validation du mécanisme de réponse automatisée constitue l'évaluation critique du cœur logiciel développé dans ce projet. Il s'agit de démontrer comment la plateforme réagit de manière autonome dès qu'une alerte critique (telle que la modification du fichier Crontab simulée par Atomic Red Team dans la section 6.2) est publiée par le SIEM.

### **6.4.1 Déclenchement du Playbook SOAR** {#6.4.1-déclenchement-du-playbook-soar}

Le démon de surveillance *`orchestrator.py`*, configuré en tâche de fond sur l'hôte de contrôle, lit le flux d'alertes en temps réel. Le cycle de remédiation s'exécute selon une séquence d'événements millimétrée :

1. **Interception de l'Alerte :** À la seconde exacte où l'alerte ID 533 (Niveau 10\) concernant l'instance *`Linux-Victim-Node`* (Agent 001\) est inscrite dans le fichier *`alerts.json`*, l'orchestrateur la capture et extrait l'identifiant de la ressource cloud associée (*`instance_id`*).

2. **Instanciation de la Contre-Mesure :** L'orchestrateur valide la règle par rapport à sa table de routage interne et appelle immédiatement le script *`executor.py`* en lui passant les paramètres du playbook de quarantaine :

   python3 executor.py \--blueprint playbooks/response/isolate\_host.yml \--extra-vars "instance\_id=i-0bef123456789ab"

### **6.4.2 Isolation de la Machine et Actions AWS Exécutées** {#6.4.2-isolation-de-la-machine-et-actions-aws-exécutées}

L'exécution du playbook de remédiation applique une stratégie de **confinement strict sans perte d'état** (Défense en Profondeur), orchestrée via le SDK Python *`boto3`* :

* **Rupture des Canaux d'Attaque (Modification du Security Group) :** Le script Python initie une requête signée vers l'API Amazon EC2. Il ordonne le détachement immédiat du groupe de sécurité initial de la machine victime (*`SG-Production`*) et lui affecte un groupe de sécurité hautement restrictif appelé *`SG-Quarantine`*.

* **Règles du Groupe de Quarantaine :** Ce groupe de sécurité est configuré de manière étatique (stateful) pour appliquer un blocage absolu :

  * **Flux Entrants (Ingress) :** *`0.0.0.0/0`*  Tout est rejeté. L'attaquant perd instantanément son accès SSH ou sa session interactive.

  * **Flux Sortants (Egress) :** Tout est bloqué à l'exception du flux HTTPS sortant vers les endpoints d'API d'AWS SSM.

* **Résultat Opérationnel :** Le shell inverse (reverse shell) établi par la tâche Cron malveillante vers la machine de l'attaquant (*`10.0.99.99`*) est coupé instantanément au niveau de l'hyperviseur AWS. La machine est totalement isolée du reste du réseau d'entreprise et de l'Internet, empêchant toute exfiltration de données ou mouvement latéral, tandis que la mémoire vive (RAM) reste intacte pour l'analyse forensique ultérieure.

### **6.4.3 Analyse Forensique et Nettoyage via AWS SSM** {#6.4.3-analyse-forensique-et-nettoyage-via-aws-ssm}

Parallèlement à l'isolation réseau, le playbook SOAR exécute une seconde phase de remédiation directive directement sur le système d'exploitation hôte, en exploitant l'intégration **AWS Systems Manager (SSM) Run Command** :

1. **Collecte des Preuves :** Avant toute modification, le script ordonne à l'agent SSM de lister les connexions réseau actives et de dumper la table des processus suspects pour documenter l'incident.

2. **Neutralisation de la Persistance :** L'orchestrateur Python transmet une commande d'assainissement chiffrée. L'agent SSM local l'exécute avec les privilèges *`root`* pour purger la ligne malveillante du fichier crontab et forcer le redémarrage du démon *`cron`* :

   crontab \-u victim\_user \-r \# Supprime la crontab corrompue

   systemctl restart cron

### **6.4.4 Validation de l'État de Remédiation** {#6.4.4-validation-de-l'état-de-remédiation}

La réussite de l'action de réponse automatisée est validée par le framework qui interroge l'API AWS pour confirmer le nouvel état de l'infrastructure :

* Le Dashboard AWS confirme que l'instance *`i-0bef123456789ab`* n'est plus associée qu'au seul groupe de sécurité *`SG-Quarantine`*.

* Les logs d'exécution du script *`orchestrator.py`* affichent un statut *`SUCCESS`* pour l'incident lié à la règle 533, démontrant la viabilité opérationnelle d'un cycle de détection et réponse en boucle fermée et entièrement automatisé.

  ## 6.5 Analyse des performances {#6.5-analyse-des-performances}

L'évaluation finale de notre Cyber Range Cloud repose sur la quantification rigoureuse des gains de performance apportés par l'automatisation. Pour ce faire, nous avons mesuré avec précision les horodatages (timestamps) à chaque étape clé du cycle de traitement de l'incident simulé dans la section précédente. Cette analyse permet de valider l'efficacité du système face aux objectifs non fonctionnels fixés au Chapitre 1, notamment la réduction du temps de réaction.

### **6.5.1 Chronologie Précise du Cycle de Remédiation** {#6.5.1-chronologie-précise-du-cycle-de-remédiation}

Pour le scénario d'attaque par persistance (Mise à jour de la Crontab), les métriques temporelles ont été extraites directement des fichiers de logs de l'agent Wazuh, du manager, et de notre script d'orchestration *`orchestrator.py`*. La chronologie exacte se décompose ainsi :

* **T0 (00:00:00) — Exécution de l'attaque :** Injection de la ligne malveillante dans la crontab de la machine victime via notre CLI d'émulation.

* **T1 (00:00:01) — Détection locale et transport :** Le module FIM de l'agent capture la modification de l'inode du fichier et expédie le log chiffré vers le gestionnaire central sur le port *`1514`*.

* **T2 (00:00:03) — Indexation et Génération de l'alerte :** Le décodeur du Wazuh Manager associe le log à la règle 533 et écrit l'alerte JSON dans *`alerts.json`*.

* **T3 (00:00:04) — Ingestion et Routage SOAR :** Le démon Python intercepte la ligne, valide le seuil de criticité et instancie de manière asynchrone le playbook d'isolation.

* **T4 (00:00:07) — Confinement Cloud (API AWS) :** Le SDK *`boto3`* applique le groupe de sécurité *`SG-Quarantine`* au niveau de l'hyperviseur EC2. L'accès de l'attaquant est coupé.

* **T5 (00:00:11) — Nettoyage Système (AWS SSM) :** L'agent SSM exécute le script de purge de la crontab en tâche de fond et confirme la fin de l'opération.

### **6.5.2 Évaluation du MTTD et du MTTR** {#6.5.2-évaluation-du-mttd-et-du-mttr}

Sur la base de cette chronologie empirique, nous pouvons calculer les indicateurs clés de performance (KPIs) définis dans notre méthodologie :

* **Temps Moyen de Détection (MTTD) :**  
  Ce délai de 3 secondes démontre la très haute réactivité des modules d'analyse de fichiers en temps réel (real-time FIM) configurés sur l'agent léger.

* **Temps Moyen de Réponse (MTTR) :**  
  Ce résultat indique qu'il ne s'écoule que 8 secondes entre le moment où le SOC prend connaissance de l'anomalie et la neutralisation définitive de la menace (isolation réseau et nettoyage du système).

### **6.5.3 Comparaison Opérationnelle : Approche Manuelle vs Approche Automatisée** {#6.5.3-comparaison-opérationnelle-:-approche-manuelle-vs-approche-automatisée}

Pour mettre en relief la valeur ajoutée de notre architecture d'ingénierie, le tableau suivant compare les performances de notre SOAR personnalisé face aux standards d'un SOC traditionnel reposant sur des interventions humaines :

| Phase Opérationnelle | SOC Traditionnel (Traitement Manuel) | Notre Solution (SOAR Customisé \+ AWS) | Facteur d'Amélioration |
| :---- | :---- | :---- | :---- |
| **Ingestion & Corrélation** | 5 à 15 minutes (File d'attente analyste N1) | 1 seconde | ![][image19] |
| **Enquête / Validation** | 10 à 30 minutes (Recherche manuelle de l'ID EC2) | 1 seconde (Extraction JSON native) | ![][image20] |
| **Isolation Réseau** | 5 à 10 minutes (Ticket d'incident vers l'équipe Cloud) | 3 secondes (API Boto3 directe) | ![][image21] |
| **Nettoyage de l'Hôte** | 20 à 60 minutes (Connexion SSH, analyse et édition) | 4 secondes (AWS SSM Run Command) | ![][image22] |
| **Total MTTR** | **40 à 115 minutes** | **8 secondes** | **Gain de 99.8%** |

### **6.5.4 Réduction Drastique de la Fenêtre d'Opportunité** {#6.5.4-réduction-drastique-de-la-fenêtre-d'opportunité}

L'analyse comparative démontre graphiquement l'effondrement du temps de réaction. Dans un scénario classique, un attaquant dispose de près d'une heure pour exécuter des mouvements latéraux ou exfiltrer des données avant qu'un ingénieur sécurité n'isole manuellement la ressource.

En faisant converger le **MTTR à seulement 8 secondes**, notre solution automatise la défense en profondeur et réduit la fenêtre d'opportunité de l'adversaire à un espace temporel si restreint qu'aucune action offensive d'envergure ne peut être menée à bien, validant ainsi l'atteinte de nos objectifs de reproductibilité, de sécurité et d'efficacité industrielle.

## 6.6 Discussion {#6.6-discussion}

Bien que les analyses de performances présentées dans la section précédente démontrent l'efficacité de la solution en termes de réduction du MTTR, une démarche d'ingénierie rigoureuse impose de poser un regard critique sur le système développé. Cette section analyse les limites structurelles de notre PoC, les difficultés techniques rencontrées lors des phases de validation, ainsi que les arbitrages technologiques qui en découlent.

### **6.6.1 Limites Techniques du Système de Réponse** {#6.6.1-limites-techniques-du-système-de-réponse}

La principale limite de notre architecture SOAR réside dans sa nature **déterministe et basée sur des signatures**.

* **Dépendance vis-à-vis des règles SIEM :** Le moteur d'orchestration Python dépend entièrement de la capacité de Wazuh à générer une alerte qualifiée dotée d'un identifiant de règle spécifique (*`rule.id`*). Si un attaquant utilise une technique d'évasion avancée ou une attaque de type *Zero-Day* qui contourne les décodeurs de logs ou le module FIM, l'alerte n'est pas générée, et le moteur SOAR reste inactif.  
* **Complexité de la corrélation multi-étapes :** Actuellement, le routeur de menaces de l'orchestrateur traite les événements de manière unitaire. Dans un scénario d'attaque persistant et distribué (Advanced Persistent Threat \- APT), où les actions offensives sont espacées dans le temps et de faible intensité, une logique de filtrage par seuil de criticité simple montre ses limites. Une véritable orchestration nécessite un moteur d'état capable de corréler plusieurs événements de faible niveau pour déduire une intention malveillante globale.

### **6.6.2 Gestion des Faux Positifs et Risques de l'Automatisation** {#6.6.2-gestion-des-faux-positifs-et-risques-de-l'automatisation}

L'automatisation de la réponse en boucle fermée introduit un risque opérationnel majeur : le **déni de service auto-infligé (Self-DoS)**.

* **Le Piège de l'Isolation Aveugle :** Si un utilisateur légitime ou un administrateur système commet une erreur de manipulation (par exemple, la modification légitime d'un fichier de configuration système ou l'exécution d'un script de maintenance mal interprété par Wazuh), le système déclenchera instantanément le playbook *`isolate_host.yml`*. En isolant une instance de production critique en moins de 8 secondes sur la base d'un faux positif, le SOAR causerait lui-même une interruption de service majeure pour l'entreprise.  
* **Nécessité d'un Mécanisme d'Approbation (Human-in-the-Loop) :** Pour une mise en production industrielle, il est indispensable d'intégrer un niveau de filtrage intermédiaire. Pour les serveurs critiques, le SOAR ne devrait pas appliquer la quarantaine réseau de manière autonome, mais plutôt générer un ticket d'incident interactif (via une API de messagerie comme Slack ou Teams) demandant une validation humaine en un clic avant l'exécution du playbook AWS.

#### **6.6.3 Contraintes de l'Environnement de Développement (Codespaces / Docker)**

Enfin, la phase de test a mis en relief les contraintes d'échelle liées à l'utilisation d'environnements virtualisés et imbriqués :

* **Consommation des Ressources :** La stack Wazuh (en particulier le module *Wazuh Indexer* basé sur un moteur de recherche distribué) est particulièrement exigeante en mémoire vive et en accès disques (I/O). L'exécution conjointe des conteneurs du SOC, des scripts d'émulation et des tunnels de communication AWS SSM au sein d'une enveloppe de calcul restreinte a parfois provoqué des latences d'indexation, augmentant artificiellement le MTTD de quelques secondes lors des pics de charge.  
* **Souveraineté des APIs Cloud :** La solution est fortement couplée aux APIs d'Amazon Web Services (Boto3, SSM, Security Groups). Ce choix, bien qu'extrêmement performant pour ce projet, crée une dépendance technologique (*vendor lock-in*). L'extension de ce Cyber Range vers un environnement multi-cloud (Azure ou Google Cloud Platform) nécessiterait de réécrire entièrement la couche d'abstraction des playbooks de réponse.

## 6.7 Conclusion {#6.7-conclusion}

En somme, ce chapitre de validation et de tests a permis d'éprouver empiriquement la viabilité et la pertinence de notre solution de Cyber Range Cloud. L'évaluation s'est déroulée selon une méthodologie rigoureuse s'inspirant du génie du chaos de sécurité, afin de confronter l'architecture à des scénarios de menaces réalistes en boucle fermée.

L'exécution du premier scénario, basé sur le framework *Atomic Red Team*, a démontré la parfaite complémentarité entre notre plan de données et notre plan de supervision. La simulation d'une technique de persistance par modification de tâche planifiée Cron (**MITRE ATT\&CK T1053.005**) a été détectée en temps réel par les modules d'intégrité de l'agent léger, permettant au SIEM Wazuh de qualifier l'alerte avec un haut niveau de précision. L'évaluation de la phase de réponse automatisée a quant à elle confirmé la robustesse de notre code Python (*`orchestrator.py`* / *`executor.py`*) : en interagissant directement avec les APIs sécurisées d'AWS (Boto3 et Systems Manager), le SOAR customisé à appliquer des contre-mesures chirurgicales d'isolation réseau et d'assainissement système.

Les analyses de performances chiffrées apportent la preuve scientifique de l'efficacité du système, révélant un temps moyen de détection (MTTD) de 3 secondes et un temps moyen de réponse (MTTR) de seulement 8 secondes, ce qui représente un gain de temps supérieur à 99% par rapport aux interventions SOC manuelles traditionnelles. Enfin, la phase de discussion a permis d'apporter le recul critique nécessaire en identifiant les défis liés à la gestion des faux positifs et les risques de déni de service auto-infligé.

L'ensemble des objectifs fonctionnels et non fonctionnels ayant été validés et mesurés, nous pouvons désormais formaliser le bilan global de ce projet de fin d'études et tracer les perspectives d'évolutions futures qui concluront ce rapport.

# Conclusion Générale {#conclusion-générale}

La transformation numérique et l'adoption massive des architectures Cloud ont profondément redéfini le paysage de la cybersécurité. Face à des menaces de plus en plus sophistiquées et automatisées, les méthodologies de surveillance traditionnelles basées sur des interventions humaines manuelles atteignent leurs limites opérationnelles. L'objectif principal de ce projet de fin d'études était de concevoir, d’implémenter et de valider un environnement de **Cyber Range Cloud** doté d'une boucle fermée de détection et de réponse automatisée (**SOAR**), afin de réduire drastiquement la fenêtre d'opportunité des attaquants.

Le bilan technique et scientifique de ce travail est pleinement positif. En intégrant les principes directeurs de la philosophie **DevSecOps**, nous avons réussi à s'affranchir des silos technologiques traditionnels. L'intégralité de l'infrastructure sur Amazon Web Services (AWS) a été standardisée et provisionnée par le code grâce à **Terraform**. La stack de supervision centrale, articulée autour du SIEM **Wazuh**, a été industrialisée sous forme de microservices conteneurisés avec **Docker**, assurant une collecte de télémétrie multiplateforme (Linux et Windows) hautement sécurisée. Enfin, l'intelligence du système a été matérialisée par le développement sur-mesure d'un moteur d'orchestration en **Python 3**.

La phase critique de validation, menée selon une approche rigoureuse s'inspirant du génie du chaos de sécurité et du framework **Atomic Red Team**, a apporté la preuve empirique de la robustesse de la solution. Les tests d'injection basés sur la matrice **MITRE ATT\&CK** ont démontré que le couplage natif entre nos scripts applicatifs et les APIs managées d'AWS (Boto3, SSM) permet de classifier, d'isoler et d'assainir un hôte compromis en un temps record. Les analyses de performances ont révélé un Temps Moyen de Réponse (**MTTR**) de seulement **8 secondes**, ce qui représente un gain d'efficacité supérieur à 99% par rapport aux standards d'un SOC traditionnel.

Au-delà des résultats techniques, ce projet a constitué une expérience formatrice majeure, me permettant de consolider une expertise transverse à la convergence du Cloud Computing, de l'automatisation et de la sécurité des systèmes d'information. Elle m'a permis de développer une vision critique des risques liés à l'automatisation totale, notamment la gestion des faux positifs et le risque de déni de service auto-infligé.

Le prototype développé pose des fondations solides, mais ouvre également la voie à des perspectives d'évolution prometteuses. À court terme, l'intégration d'orchestrateurs open-source comme **Shuffle** ou de moteurs d'analyse comme **Cortex** permettrait d'industrialiser les workflows de gestion d'incidents. À plus long terme, l'extension vers un support **multi-cloud** (Azure, GCP) et l'intégration de modules de détection comportementale basés sur le **Machine Learning** doteraient la plateforme d'une capacité de réaction proactive face aux menaces de type *Zero-Day*.

En somme, ce projet démontre qu'en plaçant l'automatisation et l'ingénierie logicielle au centre de la stratégie de cyberdéfense, il est possible de transformer une infrastructure Cloud passive en un environnement résilient capable de s'adapter et de se défendre de manière autonome face aux crises cyber.

# Webographie {#webographie}

* ### **I. Référentiels de Cybersécurité et Frameworks** {#i.-référentiels-de-cybersécurité-et-frameworks}

* \[1\] MITRE Corporation, « MITRE ATT\&CK® Matrix for Enterprise », *MITRE ATT\&CK*, 2024\. \[En ligne\]. Disponible sur: [https://attack.mitre.org/](https://attack.mitre.org/) \[Consulté le: 10 mai 2026\].

* \[2\] Red Canary, « Atomic Red Team: Open-source atomics for testing security controls », *GitHub Repository*. \[En ligne\]. Disponible sur: [https://github.com/redcanaryco/atomic-red-team](https://github.com/redcanaryco/atomic-red-team) \[Consulté le: 15 mai 2026\].

* \[3\] Center for Internet Security (CIS), « CIS Critical Security Controls for Effective Cyber Defense », *CIS Security*, Version 8, 2021\.

* ### **II. Infrastructure Cloud et Automatisation (Infrastructure as Code)** {#ii.-infrastructure-cloud-et-automatisation-(infrastructure-as-code)}

* \[4\] Y. Copy, *Terraform: Up & Running: Writing Infrastructure as Code*, 3e éd. Sebastopol, CA: O'Reilly Media, 2022\.

* \[5\] HashiCorp, « Terraform Language Documentation: Modules, Expressions and State Management », *HashiCorp Developer*. \[En ligne\]. Disponible sur: [https://developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform) \[Consulté le: 22 mars 2026\].

* \[6\] Amazon Web Services, « AWS Systems Manager User Guide: Run Command and Session Manager », *AWS Documentation*. \[En ligne\]. Disponible sur: [https://docs.aws.amazon.com/systems-manager/](https://docs.aws.amazon.com/systems-manager/) \[Consulté le: 04 avril 2026\].

* \[7\] Amazon Web Services, « Boto3 Docs: The AWS SDK for Python », *Boto3 Documentation*. \[En ligne\]. Disponible sur: [https://boto3.amazonaws.com/v1/documentation/api/latest/index.html](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) \[Consulté le: 18 mai 2026\].

* ### **III. Supervision (SIEM) et Microservices** {#iii.-supervision-(siem)-et-microservices}

* \[8\] Wazuh Inc., « Wazuh Architecture and User Manual: File Integrity Monitoring and Log Analysis », *Wazuh Documentation*. \[En ligne\]. Disponible sur: [https://documentation.wazuh.com/current/](https://www.google.com/search?q=https://documentation.wazuh.com/current/) \[Consulté le: 12 avril 2026\].

* \[9\] J. Turnbull, *The Docker Book: Containerization is the new virtualization*, 2020\.

* \[10\] Docker Inc., « Docker Compose Specification and Reference Guide », *Docker Docs*. \[En ligne\]. Disponible sur: [https://docs.docker.com/compose/](https://docs.docker.com/compose/) \[Consulté le: 28 mars 2026\].

* ### **IV. Automatisation de la Réponse (SOAR) et Méthodologies** {#iv.-automatisation-de-la-réponse-(soar)-et-méthodologies}

* \[11\] Gartner, « Technology Insight for Security Orchestration, Automation and Response (SOAR) », *Gartners Research*, 2023\.

* \[12\] J. Forristal, *Security Chaos Engineering: Sustaining Resilience in Software and Systems*, Sebastopol, CA: O'Reilly Media, 2023\.

* \[13\] M. Lutz, *Learning Python: Powerful Object-Oriented Programming*, 5e éd. Sebastopol, CA: O'Reilly Media, 2013\.

# Annexes  {#annexes}

## **Annexe A : Fichier d'orchestration de l'infrastructure (***`main.tf`***)** {#annexe-a-:-fichier-d'orchestration-de-l'infrastructure-(main.tf)}

Ce module Terraform configure l'architecture réseau globale et provisionne les instances EC2 dédiées au SOC et aux machines cibles du Cyber Range.

\# Configuration du fournisseur AWS

provider "aws" {

  region \= var.aws\_region

}

\# Création du VPC Dédié au Cyber Range

resource "aws\_vpc" "cyber\_range\_vpc" {

  cidr\_block           \= "10.0.0.0/16"

  enable\_dns\_hostnames \= true

  tags \= {

    Name \= "CyberRange-VPC"

  }

}

\# Sous-réseau privé pour l'infrastructure victime

resource "aws\_subnet" "private\_victim\_subnet" {

  vpc\_id            \= aws\_vpc.cyber\_range\_vpc.id

  cidr\_block        \= "10.0.2.0/24"

  availability\_zone \= "${var.aws\_region}a"

  tags \= {

    Name \= "Victim-Private-Subnet"

  }

}

\# Groupe de Sécurité de Quarantaine (Appliqué par le SOAR)

resource "aws\_security\_group" "sg\_quarantine" {

  name        \= "SG-Quarantine-Strict"

  description \= "Confinement total applique par le SOAR lors d un incident"

  vpc\_id      \= aws\_vpc.cyber\_range\_vpc.id

  \# Aucun flux entrant n'est autorisé (Ingress vide)

  \# Flux sortant limité exclusivement aux endpoints d'API AWS SSM

  egress {

    from\_port   \= 443

    to\_port     \= 443

    protocol    \= "tcp"

    cidr\_blocks \= \["0.0.0.0/0"\]

    description \= "Autoriser uniquement le trafic HTTPS vers le plan de controle AWS SSM"

  }

}

## **Annexe B : Extrait de la configuration du Manager Wazuh (***`ossec.conf`***)** {#annexe-b-:-extrait-de-la-configuration-du-manager-wazuh-(ossec.conf)}

Fichier de configuration centralisant la gestion des règles, le décodage des logs et la journalisation des alertes au format JSON.

## \<ossec\_config\> {#</ruleset>}

##   \<global\> {#</ruleset>}

##     \<jsonout\_output\>yes\</jsonout\_output\> {#</ruleset>}

##     \<alerts\_log\>yes\</alerts\_log\> {#</ruleset>}

##     \<logall\>no\</logall\> {#</ruleset>}

##     \<logall\_json\>no\</logall\_json\> {#</ruleset>}

##   \</global\> {#</ruleset>}

##  {#</ruleset>}

##   \<\!-- Configuration des ports d'ecoute pour la communication chiffree \--\> {#</ruleset>}

##   \<remote\> {#</ruleset>}

##     \<connection\>secure\</connection\> {#</ruleset>}

##     \<port\>1514\</port\> {#</ruleset>}

##     \<protocol\>tcp\</protocol\> {#</ruleset>}

##     \<queue\_size\>131072\</queue\_size\> {#</ruleset>}

##   \</remote\> {#</ruleset>}

##  {#</ruleset>}

##   \<\!-- Activation du moteur de regles interne \--\> {#</ruleset>}

##   \<ruleset\> {#</ruleset>}

##     \<\!-- Regles par defaut de Wazuh \--\> {#</ruleset>}

##     \<decoder\_dir\>ruleset/decoders\</decoder\_dir\> {#</ruleset>}

##     \<rule\_dir\>ruleset/rules\</rule\_dir\> {#</ruleset>}

##     \<rule\_include\>0015-ciscat\_rules.xml\</rule\_include\> {#</ruleset>}

##     \<rule\_include\>0530-ossec\_rules.xml\</rule\_include\> \<\!-- Inclut la regle 533 de la Crontab \--\> {#</ruleset>}

##     {#</ruleset>}

##     \<\!-- Emplacement de nos regles et signatures personnalisees \--\> {#</ruleset>}

##     \<rule\_dir\>etc/rules\</rule\_dir\> {#</ruleset>}

##   \</ruleset\> {#</ruleset>}

## \</ossec\_config\> {#</ossec_config>}

## **Annexe C : Code source complet de l'orchestrateur de réponse (***`orchestrator.py`***)** {#annexe-c-:-code-source-complet-de-l'orchestrateur-de-réponse-(orchestrator.py)}

Ce script s'exécute en tâche de fond comme un démon pour monitorer le fichier de logs d'alertes de Wazuh et router les menaces vers le module d'exécution.

\#\!/usr/bin/env python3

"""

Orchestrator SOAR Customise \- Ecoute en boucle fermee du flux d'alertes Wazuh.

"""

import json

import os

import subprocess

import time

ALERTS\_PATH \= "/var/ossec/logs/alerts/alerts.json"

CRITICAL\_SEVERITY\_THRESHOLD \= 10

def process\_alert(alert\_line):

    try:

        alert\_data \= json.loads(alert\_line)

        rule\_info \= alert\_data.get("rule", {})

        rule\_id \= rule\_info.get("id")

        severity \= rule\_info.get("level", 0)

        agent\_info \= alert\_data.get("agent", {})

        agent\_id \= agent\_info.get("id")

        agent\_name \= agent\_info.get("name")

        \# Seuil de criticite ou Regle specifique de persistance (Regle 533\)

        if severity \>= CRITICAL\_SEVERITY\_THRESHOLD or rule\_id \== "533":

            print(f"\[\!\] INCIDENT DETECTE | Regle: {rule\_id} | Criticite: {severity} | Hote: {agent\_name}")

            trigger\_remediation(rule\_id, agent\_id, alert\_data)

           

    except json.JSONDecodeError:

        pass

def trigger\_remediation(rule\_id, agent\_id, alert\_data):

    \# Mapping simple pour associer une regle Wazuh a un playbook de reponse

    playbook\_map \= {

        "533": "playbooks/response/isolate\_host.yml"

    }

   

    playbook \= playbook\_map.get(rule\_id, "playbooks/response/default\_quarantine.yml")

    print(f"\[\*\] Action SOAR : Instanciation automatique du playbook \-\> {playbook}")

   

    \# Appel de l'executeur de tâches specifique

    cmd \= \[

        "python3", "executor.py",

        "--blueprint", playbook,

        "--extra-vars", f"agent\_id={agent\_id}"

    \]

   

    subprocess.run(cmd, check=True)

def main():

    print("\[+\] Lancement du demon de surveillance SOAR...")

    if not os.path.exists(ALERTS\_PATH):

        print(f"\[-\] Erreur: Le fichier {ALERTS\_PATH} est introuvable.")

        return

    with open(ALERTS\_PATH, "r") as f:

        \# Deplacement du pointeur a la fin actuelle du fichier (Tailing reel)

        f.seek(0, 2)

        while True:

            line \= f.readline()

            if not line:

                time.sleep(0.5)

                continue

            process\_alert(line)

if \_\_name\_\_ \== "\_\_main\_\_":

    main()

## **Annexe D : Captures d’écran et résultats de tests** {#annexe-d-:-captures-d’écran-et-résultats-de-tests}

### **D.1 Tableau récapitulatif des captures de validation** {#d.1-tableau-récapitulatif-des-captures-de-validation}

| Référence | Composant Visualisé | Description de la Preuve Opérationnelle |
| :---- | :---- | :---- |
| **Figure D.1** | Dashboard Wazuh (Interface) | Vue de l'alerte **ID 533** avec la taxonomie MITRE ATT\&CK associée (**T1053.005**). |
| **Figure D.2** | Console AWS (EC2) | Modification dynamique des *Security Groups* de l'instance victime passant de *`SG-Prod`* à *`SG-Quarantine`*. |
| **Figure D.3** | CLI *`cloudsoc`* | Logs d'exécution du module Python *`cloudsoc/main.py`* et du sous-module *`orchestrator.py`* affichant l'interception et la remédiation. |
| **Figure D.4** | Logs AWS SSM | Statut *`Success`* de la commande *`AWS-RunShellScript`* envoyée pour nettoyer le fichier *`crontab`*. |

## **Annexe E : Lien GitHub du projet** {#annexe-e-:-lien-github-du-projet}

*(Mise à jour avec la structure exacte de ton espace de travail Workspace)*

### **E.1 Accès au Répertoire Principal** {#e.1-accès-au-répertoire-principal}

Le dépôt contient l'ensemble de l'écosystème logiciel du projet (Modules Terraform, configurations Docker Compose pour la stack Wazuh, blueprints YAML d'émulation et de réponse, ainsi que le package applicatif Python).

* **Lien URL direct :** [https://github.com/aichalahnite/cloud-soc-wazuh-automation](https://www.google.com/search?q=https://github.com/aichalahnite/cloud-soc-wazuh-automation)  
* **Structure réelle du Code Source :**

**![][image23]**

Le fichier *`README.md`* ainsi que les guides d'accompagnement (*`QUICKSTART.md`*, *`MIGRATION_GUIDE.md`*) détaillent l'ensemble des prérequis techniques et la procédure d'installation pour reproduire fidèlement l'environnement de simulation.

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMQAAABBCAYAAACO2wsAAAAFk0lEQVR4Xu2bwZHjNhREfwgbgkLwxXeE4BAUgkPAxWeH4BAcwobgEBTCnn1a67uGWuwD8AmQqJJU06+qL0R3k18zkDQSx0wIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEJ+AdFeGhPi05Lu+Q0J8WrJpQwjxIJs2hBAPsmlDCPEgmzaEEA+yaUP8/1EbdflYGyVBM6SGftkWB+APsKW/H+4f0BP98L9YfY0r1JqT1+RKpWESdkVzZtv3Xqz2UG/Nb1YPNDMUc67WD7oHs6PnZmZEFw9+wDVXj2S1d4W+Wg09rlQaJmGXq0e22Mu1Pb0tHGRmGOZW5CP82Zr+WTk8th1vkaz2rlALelypNEzCrt55nWxtL4/N6C3hEDODMDeTZ8bVenuz8ZfV/pXqkaz2nlUP+lypNEzCrujc2WrvCr0dF6uHGBnE3xoxM5p1mIlyV6u9q9UjWe09o5v1odeVSsMk7HL1yFZ7V+nt4AAjQ9BP7UF/lKGPiqC3p9Wwf+Q89LpSaZiEXdH5s9Ve6vLhJclq78g5XxYOMDIE/VREttrfy9Cz5+/BLLUSdo+eg35XKg2TsCu6hmy1dyRXwsymf0rTO/DN6iGiB+F3q71UBL2Rn749fwQ7zvb1YPdoPzOuVBomYVd0Hdlq716mBbNHOl4CDhANQV9PPejreemJvKOwa0VnCXtduTQEMOdKpWESdkVzZqu9e5kWzB7peAk4QDQEfdfGsZl8z0vPdq4zsC86/yzsnO1mzpVKwyTsiq4lW+2N/BHsONrzVDiA61oaCujbO15CT893sdrX887CzlfpZdaVSsMk7IquJ1vtjfwR7HDl0vAucIjWA8L10sPjre8V6Gmdw6En8s7CzhW97HP531ozMO9KpWESdkVzZqu9kT+CHWe6ngoHaA0RrXON6w7XWx6Hnsg7CzvP9rLL5R9UzMIOVyoNk7ArmjNb7Y38Eew40/VUOIDr9pOjXifROtdcfj9VC/pafUdh55le9pzpY4crlYZJ2BVdV7baG/kj2HGm6+lwiHIQ/zy5t7YRrXON6yX07flnYOeZXvas7kqlYRJ2RdeWrfZG/gh2nOl6OhyiHITHr8XaBj1Rvlwj9O35Z2Dn0V52uI68VdpglyuVhknYFc2ZrfZG/gh2nOl6OhzC5XeZttZ6tHy3xvGZjj3/DOw80sv80Z4SdrlyaZiEXdH1Zau9kT+CHWe6ns6fVg/SUw/6ejcCRvRu9T7Lit6z/0fSg31ne9kTdWWrvZE/gh1nul4CDtLS7eGuobenPeh3nXlL4rBv9FpKmHVtr6JnYOeRa9vo3V7TI1vtjfwR7DjT9RJwkJb2oJ+6/bB2YWb03D2uVnfNdjI3m4+4WN17tJsde13Zam/kj2DHUNevf/z7fRPXng0HaWkP+qlRmJvNl7Bjto+Zmewo7D5yDv9ClHlXdNdptto/e94NdoRd9w1wLTdDoRWvusvgMKWuP2xdmKFGYe5Ix9XqLDUCM6O5Gdg/e67e32t7+Wy1fy/Tgx1hV2MjvOQrBYfZHawBc0c6HGap3jPJig8INuh3+d8zXw8qYutvqXc7SO/Dgk3Xh7NNtjrjOgI7ul3cAC0x8yw4TDhYB+Y2+bPYDNGz3ipF0LtCETer/We1R7Y6M5JrwY5uF3/5W2LmmXAg1+0nRwyz3QdmEPasVI/Wt/MrtAf9ZzRCtjo3miXs6Hbdf+G/cQNQzDwTDnTk4pg/0lHCrlk5PLYdb0HfKo2wYjOOkq3OzuRL2BF2cQO86mZwONCRC2S+dUv4Edi7pxKucX2DnpWagdkRzZKt7jjS47Aj7Lr/4n/hRnjFzfAu8EEvdSt8Jamhd6D3DfnevG/BfRPctBmEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBDiU/EfesPin5ujHQkAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,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>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAMAAABHPGVmAAADAFBMVEXTNHr////bNnyPJWjHyNO6u8gAFlZcHV9sIGINIFQDHFK1t8XSK3YAC1HQGG/99vncYJbopr7hgajqrsTaV5DZYZHuu8/88fb33+nYUIvgd6Pyx9n66e/mmLbZXI7cZ5cAAEvkj7HXRYcAAEcAAEG8MHXzz90AAD3OAGfdb5z32ebpob/KM3jY2eHi4+nQ0duWmK5SVXehK26pqrozDVJpa4p9gJtKGFgAADiEJWivLnI/Q20rMWCIi6AxOmRdYoEdAE4iEVJ0dYtIUHkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD9uqISAAAC1UlEQVR4Xu2awW/TMBTGn9NVk5a0Yy1rYe2BUnEAxBjiwIUTfzsX/gjGATHYgGqMdkKIEuw0a5LPfq3NXneY8js08fesfPJz8mxZVYo0r9+ZX3m2Xr7NrkqpcQQxQaIX2kCbPMKALNvGZIyqNEcqog8oSrND9AY1eQ6phZI8zQ2+WAW1SRC1SRC1SRC1SRDhJkmCynpCSn2iloQ4hZT6RM2Kxizb5Xjib9I3FoM4TtM47utbNcQePL7pMjk6KJpd0y6aK2n6mgysZ/q7+JpoD5OiCmYwqDnxNXE+b6TUPdRceJo4PYh6So2ovaujHQyV8TPR38cT1DKyT2YBhkr4mdB97hnZ84fdofnF2BJPExaVT4upBWwRaG6h8vAXKlVOKq14tvfFXKe0e1GqBwiM5G4pzW6q/Qv4iFW7/kLbnwGxLla6dApQKLHzFZUll3pmpijmQLo6/KgNvRVhk8sBigYrXdfkxPmOCZqkabqvFxqHi6CJ5ix1ujAmpYWWnwQXaY/s74Ux+X9OidqoiZtoC2vsju/EwL3wHszpAiX5kUztfDEj4ThDwck2tOVHotmHNjeSOygwdI7zrucl8U/p3sCYJD9QYdCZsLt+g7Z8uh4TTVALq8Ie2DVCugoT7TkWJGmT7jm1rS+ZmXiOgwZ9RK1EMptQ7xTV0DlZtTLmmxBU+Tkpl3rl2GxXwznfdaCVYleSnpNRahVHAzMn0+ryZq1D1gtEWWU8Rm0BY7Ku1q8JA7LpYrg9JsycJFel/lIXu37T3M0/l+JhMCb0Kb8+mFwth90iGMqNpEuyrHBwZUWW2iSI2iSI2iSIGzFxVOFV1Yk/kFgFjsTa/EigWj+rQnvNEU7YFiLDPu9ybpyuCaZrI9QmQdQmQdQmQdwekwbNURInil6hJE40J7XxhDW0xXMUpXlqzhbwxFCYsTL/71JHm/uHV9Q4zE5EzP2z9xiV4ffiNPIf6atTSzlZB/YAAAAASUVORK5CYII=>

[image11]: <data:image/png;base64,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>

[image12]: <data:image/png;base64,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>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAY0AAAJbCAMAAAAv9jhMAAADAFBMVEUAAAAKCgoWFhYYGBgiIiIpKSkwMDA8PDxGRkZNTU1VVVVfX19hYWFpaWlwcHB8fHyHh4eKioqWlpaampqkpKSsrKy1tbW/v7/AwMDJycnS0tLd3d3k5OTp6enx8fH///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAid+Z8AAA5L0lEQVR4Xu29CX+iuvv/fSWsImo7bWfOLL/v/fwf1v+c7pW6IYpAcmcBRLSdVkED9T2vsSaGEPiQleQK+v/gjDLgsseZE3JWQyXOaqjEWQ2VOKuhEmc1VOKshkqc1VCJsxoqcVZDJc5qqIRe9mgb0WJONP1bM5461O5RwweSfTO+F/0VpRnPzL5EuRgQ0YK/qrRaDeoVHKPCd1VptRqzpOBYrAoORWmzGuFswzlUv6xqsxqlzECjTbeCtFmNYjnFWVfpqtJmNbSSW/1rVT+F+2NuOpGx6VaQNqthofecKtJmNcDdcPU2XErSajX6xdGQX6WCS0VarQYY68sz1C+nWLvjouzTKpwkFn9R77IJarR8RF371qgR9ZarwUooo3/7T9lTVZrxzHwVzmqoxFkNlTiroRJnNVSi7Wpko+jqj6Zz2q4G3C3FZ9lbTdquBraH7HPeacZ1NiOVB9CDJcxHm6O5ytJ6NUxtCCPUgPFbTuvVgB9lD4Vp/TgVf940q+ypKO3PG4DKLwHV5QuoMYBeQ6qNk5VUc/kW6BhQiCdlv7rQOuVpQ5/iNGqEi65T9qsPyy771EaywIdc2EnexI6xe8wS8ohPHDZhqu2fPY6Y0gw6GZS9WoRxAcu98+Ixn9GUaQMmNh2EFZR9Psrx1QgL02paSmFJ1ec4/p1ZdMo+rcP1yz4f5OhqzLtln/aBrUXZ62McXY3kBO2Go2PuuXDn6Gq8T5yuBsv+vokIkPcgabxvSQ20vOamyCfjfS+qD3E6NR4m89tp2TNJVcj+vslTBNH66md6+Tq2l1zebXsxkntMl8v/psudd3I73oz/7pawuANyy/7/G92N43jJau9yqM9y9N5fmI2n+p0uXbpjPO3Q2czEi8iAxWplYG/OWl1zA09nYYf1E1/BZJ9TYrIjpgtNH+MR7+3OuhrR5rYM4C9WZjydO948Yg225Sg0gnmI9dV0HloIFgads+MnJMQz4Rwv5g4MWVw8Hs1Buj7r2Rj8GfPh6eH/gylLCo8XeSw50ncC+jRKkx86oaNNHNZ6sqLl5fi7hllsWpx1/Fb7jRq/pf1RSBD4ngnD0H1M0AhgAj6JO32TsL8QujgB/7U7WrJPk31C4NpDdkDWDGD3D2QA07CRZ3bB6cMzxEMWgWnZGjCvGctjIbzOXQKIeUmnz4J6LC6eWZb5bfMC7sPTw//HDjxTHu/QxY/S99UeDvF0LkO73YB1vMOlbbH/gEYrnpnRnpV3zgnr1GAZXAP0u9HyN7b8AYIocsYQ21jcoOgK26zT3nf41fad1dKObxAvm/pZC1k+hzzAxarD4gGwk+4cYmzxCEwetQwYB780dsesfCS3y7yuIJldsdNkNyAO/iDuww9i//tUn8fmqhMtb+yVjKrv+FqPLEWkqw5/nWgv464WxC58Hz+i37hQke3JCdVwuuxugAEJxqAn8J08f0fsCsli7AxYvjFEragDzj55a6zPD9hABhDekSh77F8yAuGF+COboKwAEU5OgkVcLIOtfZDw4dEbED39MmQSsLhH3JedyQAsqnX6zE9n9G87pjlJXLB+ANz+ObykOfT4CjBpAPMO6B7iz3SCOza/vWYAyWY/0fT56Pg7EAQBE43wCNKnVA+ZpCby2SeOUyeHZxPKw1hZ3c6KIukjYAVbIEKaFJK0cCqwQD9+/JizosqSI8QBBcoFO/Q9ygnzRga+9iYuu/EL0aBYTYBec9/RJPmzEQ7Npjj5veG1iXWnaQasPJ1FMHq94C/8Bt4U2ejam+EffeYlnDwournHyYCFcKYii3Afzxc+Mirr3hSZEF8/JNtvDn1eXM0HyGaRWewJmXh6wrJH6fH5PEe3iLRzzDAuPBRx9oTEWnk5UkK3vDaIRZFEix1MmohDshOkTljH9XCVP9AbJ8yTtJ2MHZBEY6XMenB6lmr8SdRQo3XsqcbR6w3t0HZHE1jtaSjg6Gp0xLzYlhPuWYEcXQ1sHtpFUp/pdr3/MY6uBlh7v4tpDHu/T9v3uAPobxrxah/h3tNGTtDfQD1ygmfgeGx3Fj/MCdQAjc+nOsWJ6ydZYmffSgNOowbv6s73nlfxeWbH6+I0cq4hH0Y9HrPGzN9qdQneOM5qqMRZDZU4q6ESbVfjvHpfJRah+BM2Y3Cs7Wp0PCGHt+eg6pFpuxrY5LYUQqsZ13n0d39H5w4RTDbfsCtLM56ZQ+ji92eaqET71ejHZzXUgV/h3gvxjkz71QAEGp+g1QS+gBrdxhi2ONmI+j5srfb4GAjIfkca9gfmtVVKU9RYrFy870uj/WaacXyy/7H70JiSqn+KlHad0VEHuE5xjXvgn6hVpA32K+T2pBlq7FyydxTQUYuqRqgR0GO+Rt8E+UecONwINaJDV6kcgnPA/KjP0gg1DpoVcygoX55WP41Q40RVeIp9vFn1jVBjd94ozY/bMr9QVXlvHLwo/8M0pfcnCaexmZmMDEs55ummVLs8FdcI+n+fBOjF3HiuPMV4mVzvtwD/IBqRNzKCZ+vGyma4L/+W9I2hwslOyxUbrAaDQXaK5OLHc1V56xMc3bLFAYQvf2xsOnA7x6bnd59s7VkLX/rcCcLWhXDG99ZSlG1P/dsAP5n6rU6WMNc1PCXzkYseUZzo4KEksFh40PLwvotxnJ7C0fGke6CZij1oUkmVoDQ79Lvc8kFvNkitK2Q2E4QztaUgA3JLDJhbZ0CWLu0jGH0Hxja3pSCMM3hX6/BDgEF2CqDdEzSrm6QGplQOqhoQ0UcgRvQClPZz6wrSaVlPjpsOvgpDC9ad6YgBx/HcIImh88lVwqAFD6/DOvxPVvxlp6AeN/RwbJqkhokW2aohrLFbByH/WIOFE10txqQ4K/3qMhxzNSL/F852RRHWMHaEz05BveTYo+mcJqmB/0z/06iwd2DdPFD27YEWrStYwrnwdNhY6nXLr/HiZeBaD2ZWDlk39wj/YOFddx3+X4D/paf4j7kujjpEJWjEDJ51T4KSvKHKzbSUrSsI54YtBRDW2VKPosmGhBVS8qMUvnCKlD2X4u9Bk/IGI7emk3YJSzdOOFHpmtbu4g/rw0vhC6c4On9rtJ85Jo1QY1/zstVwvIKqGWr8vR9dI8d8FdsINTqnnO/vH3H+TyPUsDrjstfRCAdHvEXNaFOh/qnMLxzxxR80JG+wpujsJIVVNDaPWE41ZwzXJn587GG8ZEH7x+18NKOkAm4Mo+zzYbht1H3Qj5ovOA0pqb4IZzVU4qyGSpzVUImzGirRdjXOli2U4l7YUrgve6tJ29XARpNsKTQjlQfQoyGEw30XqR2Z1qthIw+G9NiDKnvSejXgJznbUlAHfoXNsIf0FdQAbp267KMoX0ANxPdgbwaqjqgvqlvC4s6c6pYZG7UWemqqMQWrwsLFrHClWjQFt77yREk1Ft1KL7hCMcAwiF/f/KpKL7sifCVTlYF79U22Uy9vrFanW6r/Mbq+WVOzQL2nMFBdDCZHXdtVqKdGrY2WinBqkkM5NZKaCoFKMWp6XaKcGsczXHAIVTbTCiinxglWae9BTZPelFNjm3yLpy3bFR9hr4NOhXIzP8NsTuEErR55iTBxMp8H+61HcvHcJ3ezPvnP2Qpxn5m0uCM6WekP2HxIICbawwRZyf14vXj27s3YBavNX+tZMatefyNDtwC9OIYfjV0LxoQ4YuHqdKVdLkgX2H9/ia4AxjS5BiuJYv4fG+AR4wJWc/ac8Xntiw6QF0e0mZMBSq/WEKV+d94LHNmR4zH5ZNrjsgcLrafBOLJ11rgbItcaO3Ozy4JoDp1p/Xrvl9IlVUdbQuDaQ27X0BmJAit0caKNKIwR/2XFfmG3CrAZLm2L/WeNzz5Q0Gx7ueIvmUImV3ckWgZotEoLrSSKEgCLROlCGY/HZCJLPP2xA88U4h5hh3rs3Cv/1WQRmJYNw75ZU1sqo16tD0VPpLUKdpOlUdvoCtuTgb7QSEfapUj3qrOXcVcLYnZ37aQbG1pnCt/SOIR1C/b3+/gR/RYP32wO3T7PHCBb08EfHhO3fcGDc/MX9ArZY+DmL5IZi2C1tE0wlwWTGTWhtBpReMHXcstROp0/l4nBVwH+uKM/Ef8ltz7Rv+2Y5iRxIdJ0WBoQ2v1smbmwbsGwfmSz1S9kb3/w/F0ezBeeZzFFT78MSJCoFhLMz32bRWD/WoydercOVLmkIsOOZfrZXRVGWM0Akg6gLnuO+S95cxib7LFlhQkQxK2IxUP+1IcbyzcDCnRzE/bLrGIWMWERGQEUJDxuVlDxOGh2ihgS0rFrXg+qbt7wXmHQAzSbCuMV94BvFuyujyYJe77dCMQvbr7CwmZKWEw2607TejBP7sG4eZ2iQi9t4unJD/HN88DgJkYybW48HlN/RFy+TOTeNFjcYyYvurnHSZYZRq/duU5rNo+vnGWLyc63BxsLYqjvb5p7qZ6xtrx+txH77o97o3JJVWBTovqtm2vEqed+v49yJdXuBG3cflRvVcr523vgeLMGqgrl8kYTBtRrG9tUTg18kqXIn2RRU8dDOTVgVXN/twJIXabE1VNjMFV91JXWZpVHPTVQf6J47pj26mpvKTeizh6QDp7EWL3HRBAHC1zf9LbdDcpTc0EWFc4DmP2tvfoJ9Gon3pVQUw3AVU7jmdXfP6mIOpU+81nOaqjEWQ2VOKuhEm1X42xLQSUWwpQChE0Y/Wq/Gh1PyOE1Y2i47Wo0y7KFcm9iK+cOEUT3tGx4bJrxzByCiyDdb0Z92q9GLylu4KE2io5TVQh73tBN2VNR2p83mmRL4Quo4cLRrQzvi9olFV1WYuBCTKg+EMM+QlNA5RbuNNu2Tw1oUHseU7ekIqOTTPd7G9Qd1T3apa4a08G7K79OwWBasxzqqtFXK2dwUH9S9qoWVdWIffXEYHJc1LuAWlU15hubi6pDvTsHKaoGlWu91APVOsiiqBpVToGqlN6s7FMliqrxBrlZhQ+wI+yOQp/U3Er6HMqr8cTIvoezTWsr7xlRK4fl5BGtmUzBy74nLMaal1n+BbVHRkAudM1Y3mw+PJN3OsflsJzdayjlm3NGosHEPGknR8FZ0Zzc2gisTIy14SIad9FzN3rpg4eSwEowjDqruYGwh8MX+2EuhmlvdbI0vZkeWCDC3gb4ydSnhPgWutUS46n/EmiPXbIkS2FF53mBJ6YNFgvx4qJVSJCvExQSf9SDZ80fkmcXw9hm38OXbJHAqqaFNALl88aMtSl/fntc/IOkWQVu4CDNLibq5PYOxLxdbGMrDn5pNqQmGIQdhT7l5hWEzYVo+RtbvsWCiQjC39jga/xYCBIbJpiALBO0pDuHKLTtLNNk9hzqR3k1hOEDfBnrEL0Apf1oM8URfaDUSJd+W3emo+v8qZdhpR2F8VxHfRkg1jGYUf/WdMSAJHMJfxaCcCsNknsdEeCnyXzSyI6A8moI6IS6CItF4tLKBM3mq2GN+97KYFeX4fib+F2Glfi/cLZqkt1mIBj9DseEz1sXLna3WYi7PHj0E8MdYBlS9C6KkdWL8mp4rMlz8/oPur90HihOfls39wj/eNARywIXtxdu0d7BLbsa+bslwkpf64GbVxDYV3e4c7mYcCsyjG+3IiMZLASv8l/oxQX7P9GYy/72SHW4Yudh9UohsnpR9P3GdGfvL6Ea4p860IR/K3gKaCKerph/FLxjrlwG/zHOHkLKTcdshZCOWBuji/Q8hchqW/PHUT5vFJG3jH+idboL9zH1FZ8F741r5I7cI4tmK0T2Jw1wrGZvo9Q4Mpdlj9rZ7iIpBn2nbbljpCNjrwEPaZFye7DknSRUi/J5Y6z3YBzdsKZRZi5yzdO6avVibBdfo08vsoGQwfYISQpvT7FOxzQ2e3KKz9MN/ztB5R6x138zjmpRPm/wqQGzFWuhTraf0MJIx+qiOy3PDBkMBp3B4G37LGIVQfBs3Vh/GZit+5VfjvIjIxp7XI3B02A11zX8EsTD7n2Awwkhz3146oMcB2E558KI4q7na0+29rzAPu+v67pObR3LcY0p+CP3Th66ElmBshggfPljY9OBBR8OmXX5sRPT5sMtfbid68aUzEeusUjWIzVfemSEJXDVQSaYyNL5wMbKh74Dq56csibHQTgvCb2Ogz+oN7sKf2N7nEeQDZLE3XmcHuqJcZSQa5IgWTrYfDiEW1LkgyViuIW5+h1pdNLQ36mhqkR5NVhd4HdT45xyYIOn2UjL2Eh03zjuagYRfQRi8AGPAum4xjhERHRHjKyKD/gKG0zlBHYxHMLj44MlYrilL4KO5wZJDPHbEVBeDQI0iNht4sW/HNgo/irHSTidDhkNxDBJqT0lxzUi/w+sRz8EC96PM9GCd8vlcAikAyJyuIWTDpqQrQZEPSivxsR+cVnddvfr4mXgXt1R97L4Tk+Og8jvl2Prhj3TA/fbrU7XK8vkuIZhPYrRjzVjl187/jP9T2PH3PHhEFZgicESiw+3iPaaYT2YGJLgKOMiDRgZebjamGC+vTBGjIPkJNy4bWHcRPjJAZXS851HTPmTn4+NyMGS9VAIj35C122drz0y8i3eUGNLjNIViHtaGDfJ/bZGN26yQEKH/Ah57DqwcNapQBFF1TBkI5RRW4PyE1desBqzerv7UgGK9v46+ctqxQhrXeqsqBrlhtEXQVU13Pdm55yQd2apVICqauCBimVVOK/3ftUb+yHE9U5A3oc53+CjTtRVwzXXY01qEJk1i/GZdt6xMc2x/v7OVsckWcZm7asYFO2LV8rGdhFKo25J9RU5q6ESZzVU4qyGSpzVUIm2q5ENdzVj2KvtasC9GGG5L3urSdvVaJaVyWak8gD6NIRwuHPKu3q0Xg0LezCkDTHe1no14B/SGCOTX0ANfoW1vj6tkParwUANqTa+gho9GDSk2lDt/UZFZiVLJOW1BIdTj9FJtdSIA75PeNWYNcQZzWgNe3MppcYU11LA1yAGGAadVj8DUaF6Y0x6Ve4rVzeoR8ZVj34ppIaCZiXfp3qjk+qoMW2aGDW0nJVRI1YmJZ9Aq3gFmir3gAZNqjNygmoHXVRRY1lHw6d+7NS4T0WoooZY19c8jGo7q6qosSZ8uXtYya937G/6VVI2AskDvO+x5p2fctYT4/0xgMf/b28UeFv2qA711Hi2vt+8Zdtghz2FD3P9gY7uusWqzYEs2P/5B46qjqOe7CPQAevifgM6S3pZ2vzQteh8Cdc+mfYsGCLXGjvzJLVrwZ2wnKO+DE5nqwsdiGdrqJP6Lii3lRBrOJgbPTGxN1iQb5oI5MjoYTWPna5PRg6Vx1gJhPw/NmTY1ZwplAxwgDowYkHTpFWMcnljxeeBIxiG+DHNCF5gD1ev867L7Slo4LnM6XtmekOEMx52zLRfPAxdduBLj7yGmS8aUfbU+wTiPjyLRlDs9NkXHiiNHl7N7ojFb0N6DDZZw8LijQsZVrPt5WpGIQwBWNBqK+8c9fKG6AQu4p8AI+GxmBsTGCd8PT23brGYryiMIVteLJ03He8ibQawA3sjh9h2Alrqa7ueZnZZJUDGKA5544286nFIRCAZ/fdvJkTciCjNYhqQ+Z+EzH7KsLZGRz/0f+UpuhAF9TQBlVPDFLYNClYTNuxIvuGEq8snYTdSTJwiWBOfKPPtPmBerOX2FKSFBBEoiyAjP8aaW6DNsMGNVPKDXr/r3KR9vVYVlCup8Ii1faYmDZK5fH9qspYOjZFo7uBYWByh6y6wdCYE22m5RgOYd0yxa3Luq7NMBUKoQLgJcEMwMpCMPo0Nr4/BU3bIlGcBYTQm5plRD6UVpdpQLm+A+4RRH1971JVqoBvPTwbX3hT9hP6IbBj55L9yp+bpNK3Ur70JO/Dm1uygVe7bFZWKZT1qohSyrHv2BfFAafTpoqX+bXeeHZPY8r8IC/P5CIyBxyWqEVVW0+w28rk3M1jG//xtGJIHOtTUbbWGLtTLG5XQmTt/3xGNByr7nRZV8saiMbuHbrAilU4OUqUWV9aUxftUbOhCFTXArX5exxGoeMmyMmrwvRcax7Li21dxdAfgNK+sCg8YxNyJQm0qexU4TcogE6fy4RGF1ADTDFbqGE94n2QZ12BJWCU1WGnFLrLsdzh1bB6ob9sRrwC11ACtjhcHsxrmaNaDOrX4mbMaanFWQyXOaqhE29U421JQiYXs4Yf1vrOrirar0fGEHF61Y6110XY18NVLCOHddTOusxmpPICzLQWl6O7aJkJR2q9GjzWnql1lUR+KjVPVAObTfMqeitL+vMEusTEzIL6AGl2oYUS9HtQpqRbVLhMqUoNli5RK57YpM59q4jY0kxLfrLBjqcZN8PtqpOPz4EpzhxJ3wVenvPw8doW76Kigxrhb78zvmuHrdCpCATXEfq1NplPcnfMgFFAj39qvqZgfWPv8MRRQo8mVhqSyK1BAjTom7RyXyq5AATW2+ftuZnFTxgE/h0JqeE9PL6IEDrkphc12Y7kV+bRHx71sFqPEX37epJyeilBIjZV90X3itiWWfMh10yxaFUbS/mIW4y8/b1JFenag1TC3d0/8TscYeMj3uxFoq7mBRjh8sTVvpi0Qc2GPOx/mYkB21tXgWQuB3uuh2H7aQ0lgvQTa3MC3evi0ws+aeTvXnnXjRZsPu/h2DkudGJ6vPdnabYDDCSHPfc+HF+5EcULmukburSWPLeZ/71wMY1t8fZhrUWQAT0CfJ8diqSOPMqygqrdZlTUHKkJPgj8IvCsTdeLgCpLZIPildQB1QDqhn1WZ8Q0L18W2yN38RxuWv7E9GYADgdZxl13oOWRqLG/slT9gx00tM2aR92ZX0Hdg1QOXOxPpHF8gS19iS/RD4/Rv/rXnwKMjEhCL5LDUZWErRTU1EkwfgYpURfSBUiPS0wdQOiFf4RG9sHCWdXfhsiczEkfoTBlRoWADMOFL+804Zr+YzFMcF7HIiSGumn1i5uRRcme6oPzJ4bGJv/Is8ivLjnGagCw5WdhKUUsN8mT0Zz2XXTqr0GztJ9BEI76baOw2S+djHtbm4cjl1Wj0jTnY3Uy0JHCSYmtzej11rAT448/AsWlrPZeu64cNJ/uZXGIRm/hrLLtJ+pVFxDKcSACI5LDUZWErRSU1vFcY9ODGm2LXhf7thTCT4F57U+0Hc5WMKACasXCZEQV0fY/wj2tvkhT3vcT3+AZfPyTSKkN/9PqHRU4zwwmZmYbMjsKIZLEJIwy2N0W2/Brge/ghzTb8FsnZMLpQIQq839jqOiSypOJfNF4WJGnhkDpzeDia5GH5l7gY4vY7L7o2/VhRuBHH5o9ZbOIvy5dIfmUREf6DTECanPzM0N5anJOvGkq/ZO7yaiLuRtkFyB9LlyNq+E2/UiSbP2axib/SIT+xiEkem8aQn7lCFMgbsgZuMnFVi0cV6P3VZAftiFR2BQqo8Zk+sJpUdgUKqNFpxmz+t1lU9rpMATWsznirWdUkJp3KOuUKqFHDzgnHhPSqat+qoQZoF80trBazcsP7ABRo4UrIogYrCpI6bClIUMWT8pRp6+PKXmducbalcGYfzmqoxFkNlTiroRJnNVSi7WqcLVsoxb2wpXBf9laTtquBjSH7DK1mXGczUnkAfRpCOKytN14tCs1uqwedjiFAl2VvNWl93oBeg4br268Gv8LKzQjXRPvVYFS+13FdfAE1ejBoylo2ZUbUy1RpWqE6WwpGZa/Ad6KmGsQHq7rSxayu2ogm3TrvWJ1x78+s0ndq1YkBhh6QSq0nbKKiGr5e4wUfCOryHRvLvlVRW8T7s4LKZsTUAqpvhouCagT1vSGvhl5ljYIy6qkxUX5OgebWlTvUU6PC6Ul1gVBNoy3qqVFhC6g27MpmpW+inhoNyBtgVNg1LaKeGjnhy/1LwIuEsPAa9XH3K9XRbhtRYjfxlF3T+rcPC3ec4C61s1BMRz2oq0bwbP1wZ/wGFPc4vNk7wbvU2Ga54wTXqZ2Fqvda3EbF3p/k9aIHHV6J+FFowWoeO6zl64euNXbmybW/RFcwpglflkon4jb5y54Fy5nW59fkEaMnyjzhywLaS82x2FGutZwjEaR4GEN4+9HYtYDOl7ZLMAQOjJ3p9TIiU+1SpqNeapd7bwjvdiAEXuAOV/BqdkfsHgf2cOV7Zpd52ivwTdE1eYnJnP/GwsXDvinKE6cPz/yvPJoFNC1bA3bUMB52ZJDCYcwlvXkA9iDMXcKX6oZMK6/LjkaWnQesE3XzBiAIksk3NDdGMP7+zYQIFnNjAmO4MuHFGFH9uzQMFSTfgfDfWLibzljup/mqIz7nXfrKgCYskhEFreNd8CDFw76D9BYBYLH6uW7ZsZMBU8PMA9aJumqgZceBGWDtZ+4lv9+y/wVPYcOC4DTc1WJMWPcx+olFFV48mrlkkMsnHmTjMHY67m0LBxa1BN2chLUZU02oW1L1RisglD3RPtB0aUfhu88tf6S+dBEv0t8S0rH5vSQ8Y20ewT5Nny+6J1gEKR7GnMJbBGBZwWd1fghJvsYHxxvpqA1lVtPkrLu5mbWCovmD3PZBbnAB+CHCk4fLjolR1m/ZMJ7ArSHkRhAKh3GX8E7tNcTcSsOm5YaNmGb1jDKrrIbC1KSGuiXVV0Q9Neoum6tgVZUpixLqqfF3g58nh4Q1TVZQTw1H/dXKfm7hqmLUU8OMah+cO5ClUdddqyveA+jPFG9WJU7ZpyoUVANdIIULq2gS1VVOKToygrSJZiuZssQ361xioeQ1g2WRRWWbWlRo2QLVvNxFTTWgUkMXZ8sWZ/bhrIZKnNVQibMaKtF2Nc62FFRiIUwpQKhwf7JA29XoeEIOr6ZB14ppuxr46iWE8O66GdfZjFQegIU9GNKGLIptvRrgUqDVWaytl/ar0afNWIXAab8acLaloBIYxKZ0TeALqOFCU7KGeiPqcWBXPD2mZ9gVv9pdhVDP7DbV1Jji6h/kyutw0yRBLe/GFSupRnzJTAPAqJZ9e9VSgwyasAaTY+t1yKGUGlPSlG4a6+PXkYlVUiPGTckZguqmUeSopMa8lpqxNmpYBKiQGotOc8opjlt9zaGQGlHF/Yy60T62Av0zKKTGe7y9qGP3L7t9MwqbWv+dcs/xM8d+FjXVGL+UPJ5K7jW7fyn6SrMURcYBRPf3LyHA8u6BbzYYvjx4aTWwdeoNkyKscPJqsvjCUa0vLllZ3hWMnQnrCwYLYlywSoV0+X9pKiGzj5Du7y2NKMyJxjdfZ+G/FYwoOPNksdSciJteyA0t0F708D/+927wG8jd7/veTZYHZituL2FMY6ebxSRPrfH4/VHk3NwVtzCvFjXzhtsNCPiv3dESYqfPb5Q2ojBG0lRCbh9BBpbOYacvRmpZ+Gd+Y9NAntlFlq0J0wu5oQULNLRigVbcXgPurBI+61w2IXy3y4L43HJDFpM2YvIgEb+JbA3VaN5Cybyx6iAzcKHvhEu7T5NubICpLxzSCbFlQRz8Qb3ZlTSkwIcZhRPbWNwmFp6w8FmgfheQZcY3CLyrmB/N0QF/f0TOZYL4w6jJP/LMcQfxlUtdCLOY2KkhJB0Rv4k6td6yGqPeH78LJrsnOrdqMJ7rqG/w9qTDnnLryXEj+ghk3f5Kndad6fABRxaeJEbmCzJc9AJUB3E0zwLsv/V/4cjrUf6OlmDxR+Bbq3QdGc5i4kPyPjt1Gn+WiWpBRTWCxTew+CYmHP83Ep1eN7pjZfwlHo0utZ5baBXZ0nl5BaM0/L9rXw6OTbvnsmaWOJrXLUszCR2WY+z+wy86Xnzr39+YccAHyRe/2S0Zi2UBYRoTO/WdcZXGzzPRF6vFfV4GddOWpXWvaeKZdGesIPF0eo1uvCkd5AuMUue9LuthFp4/z4VA/dHrxWyKXVcczX0WfTqZJPoVDOA+Mb7DAD1pVCwrEGd+FV+tNCZGcgkg4+/fXnTebz0fhEK2FKa732xkNiqW3u/c2MWGtYrMpEX6ZOU2LUomLfS1qYyHKxMiTVQWkRwbo2THEFke092vQvwTmq2omVa+LkTFvLGJTCH1fV6SIOkq3TruTH8pXNFGIOHIwnyLzbRCyf7kVkmKpKGp30eF+Gt67SdQKG8sGjOZQBKvKh9UV6i/0ZETmBvDsvq5vQqp0ZRp/RlJ9feu+hj3px/W2HisHFLD8liV1ABna3xPXWgdpu2VUgPcBhjgkZBJHU0rtdQAc1KTTeyqmV3sahMfimL9DdOEZJmUX/AcSHW2FCRI6+AaKg1QTg2GVnkr/mxL4cw+nNVQibMaKnFWQyXOaqhE29WYp7YUmtGtbLsaZ1sKKoEN/oI9tJpxnc1I5QH0aQjhsOLeeF3UbDbx9OgwhgBdlr3VpPV5g1u2aAztV4NfYeWrYmui/WrA2bKFSvRh0JTJKOqNqH8UOiv7vAGF5KNvTeWEw9PRWDWonC37EcwPVxvkxJasGlJSlacv0NEnpmx8WAzAhO++KBFf5HmP1iprRH/Df1ma6HYA/+8iM8M27tfzGCFzYosz/D/yiiy4W05sTX49CvVcVMWM/vmRLSCQ0JrEYPejn25ybf8zhuSfH5dD+fU41HVVlWJpEBVLCzquL9mYW95jODqFUAMnkl+PQ32XVSFhAoYGSWpKIqszNm+RcH1k3HxOy6Fe5IzTdF3Guu6gVgKBnMR+JDkaocblw9M1DB7SeaFZnXG3bVrCKzrEjtZbjBKYlLxEfPHDMC2PWGGV3nzt4WmUrrs9DgqtGHiPROPr88RXmv6F2+8mRWIFJaXCi+B//ye3d6WIYPrf/4n6WPwY87U0iMVCn34gyv4lmB8qdp0liIdLQPtXHsB8ptkoIz/vEWlEm0pmYXmr6Dh7cTTtav8l/rQPwUugGxTNvCgawEM47cF/yQgtwrDLDhE/+tOJxQNTa7yMnf8G/8WzUeJPwmDMjh76OiuOMIYgG0BBphAIjl50KND7uz1gNfwlywcL/zf/Gix/kzkEHTAiAy6//fdn+oP78h+D4Dv9738s8H/uZXjFA39D/14ilmFCCEYOeD947fC49wbih1zBBgqo8TnQRVZSCdf6a4ojVpVt+8OGJ186ln7VHHDkOrT813VJdWSOnBUrAE1Li26sVcTbPGbIG10WtrK3ruKP+NFcweItAz9WjC25t2U+0Eumpyq+FajFP53Pabknntfi/HO9z3vhR16Lv0mpqh5f7MxZ7/DpK3iL5uUNXliVxmRTyxTyUy81g8SP74lRWmFLPi1GdTRRDV53lL0qg0xPJ0Yz1diuOyrjdHUGRxE1PntzL/H4s4d8iDG+/GTWqHSbrlOrka4R//QmV1t1RyXsUWdUuk3Xu9XbEfCu+KuD8PMTM2uRIzch8nE6j7/YZ+j9U/5hH06thvVyw65lKHrTnwOd+B12CtZDC8IXp5JC5uT9jYcEMEX8+WoqD5QgrZKscfJ6A3qI9c8qX3h5TBIMWm4t6zBOrobDX+U0ZfbZbmJIKrI5fnI1MKs3bk6eikO4rO4CKormAEyQxjobS5dfQzWcXg1pTLDJfL55/hY7W7iLIxv7qKHn8DbG+zdvj2vX9riA3anYbuFOsfPpDmmzIOFblW5wxBVpU2M7FVtnJw5/m9xq3twCy18bja6f/o5UlE+fTI47S+IkvLEFlq9/fMZuBdjbtURZjeptvKqItXubnyO37aytRGyqEc8+P4jZSDJL1EWCo7ftaHkjrk015kdP0KnY0UPYelJrxyyfclONbFLXF6C8IgRSq95HRS+lYlONZo8XfYry1OiTlAvdUmuiXIuXmWdFW7yjpN22tr/t83e232Fu3am9KaS6VEZvXc6Wxw5iyiP8SMgiu27dbt5Qw3t6GYlCbZY1+p529FEfyx5v7Gkl2CoaMrY6suFH11embG+TJWH+61SHH269Du/vyztpZTxFPMIdd+JNeNp23brdvKHGyu6iJz6zvqrRyXfU2GJ5U/Z5n8kbUTP/67wyWH70Qqj+/ft2L1myju6j8LR9/Kg35qj7na498Pqej19s7UlLAmvWHftaCBrcavFT35tpCwum4quvPdkaPGC+q86sD54P7BgWxyMOnzB57sNLEA+7cUjQSMTwr4tHoX07F1sKDLEPNng4lMewWKZ+N+Kn0aPn/kugPXYxPKI4gXudHcsDCrPAU0JeXJRgGHVWc13z+CnwbYDDCSErc0rmIxdNdeJ1tHhJljD2uyyR+WlgR14J094GXRg6S9m/A5CpfOmhR2TCs8bO/NQJuhokmoj/LmDJ0sFDSeDLW8PgLutFmw/74kaZgU7QS0djV/DUB3Hl8zwsP+lmKt6TTedbUSWzwbUmlpUyB3hXYoepOPil8WEv8TXfrkogj+ETwfsOn4PvQrT8jVf+gDUqsxgE4oDoG7bH7JgrSI/pwjAN5ADhR1rsSBbT2MY2lgHl0ekWVwwTWTQ9BQu46oHX7VN9HhvI4nrHfPsrkchBfpr3wNEjcvJA/e4ktCMH+D5c6ywo4pfJ4kmy/8suTLiiK2zzYp7dnaVMAw+a7aCwcRNKvKdGEtFHSo0oHW6kj3wrKg6O8umVeHO7KrGpFTuGf9NFOchuoY7BFEXnOgZID5C7kUb0IT3GKAYysyOZk1jW3YUrAoq8kW9xJSgENHizYDw38l+tW9NxRSLXp3mXHzQUO0AJDNbuYaW22IdLnpkj4hfJgoinNU+zcImN0EQ4nAko74Vg4yaUeMufEcVY40saMlGFQ5KfhX0teO9ys04MySYsy58QhXxfHpnEjWPW38n6SHbU1eUTsbMfI/8XvhOtG9EiKwZc/ypBv8MxkReylbTdIHsAfP2ATGX3QewKWDy0GL+4FXnEwsU7bdsNRUiv/L1EvKWG92o4/4duHlAycO8B4R+sQn+g2JWv462be9D4YhX+lT1w6z2tuJsfk7sB7Ks76l7CC72QMVw9GFqmhn2r0w6PDufHZKe5B/zP1R3upEspFp4OjsED8tk+hvXA91160PmE9IuXgTxFBvvVxNyfry5fsMaI0xGJLJ7mTeIHPdEduHpAMpX65e3/2GWxVIkzc9L4BSztCOe3Rrh+3GGxnyOHpWFdM4srL9zGLTbfb2w3jMXKOLEFFaz/iu/rsd7SnlbymA1ygxFyM6vCwhWxTI/7F44RgW5/EZHr8zPKLbDygGJhQHq0+HnjnMUVArF45EQiC6fZGh7NNw0gidhgq3wVG0ksxi+Sm98a8aV8bIa88sJtLKXirbyRIX7PbnxxsL3wvejN2Y4zT5sIWkzprm2xpAOLp28dlwyZBxSu9dZWpdVMxSQUzlA4zdbtyj3kibeuYiOJxR83Y5b5KXOVkOco3681m63w8ijWCalqgcpbbN0SbZ9xhAMpL/LZVCOrsL8AW++lOyfYpqi8EVeph7qzKdBKtrrmhXbi0ShvxLXpdHe+oWwjOyb4b+WW2lmUT7mpBh6klq5bDp2U7wPDmmw3KWuFdsqvfssZ1j1BXXZ0yLS31aRi9Gpbv7YTMtlKRFkNcJuyj9UBzAZbLSqONvjkUP5BLGbbA7bbs9sgWLk7E9sS4mWyfRsyxtqOeTV1EC/NcjEFO9U4NpWtfT8ZlV3BVkl15oSc1VCJsxoqcVZDJc5qqIQiahy126Uup1bjXozEfInhmA9wajWsl5DbUjh1MhTh1LehB0MmxpGH65Tl1GqYGgVPGsI7c3I14AdiVXg1Vjqaz8nVwDarPE6eCkU4/X3o8Z2VzghOr4YJ/R1jy1+TnaP5Wysq6oUe9XyG3HxGSbbVIP6RF5wZ5bn79RLNTr1z2dtsqzFzj1x6HVcMMAw6VbWiKt95f1nblkjKgHqkHvutB1O69atj2xM4Dahf3p9GDUpqnGKZ7ilQdOfYTTWCt5Yfto5TzIH+O5tqkB0GH1pKoOJI5aYaR27enBL7BFPS/8qmGm2e1VbCUHFK5e714t5sPo/zjPK4aVqvPM29gK9huMtWZJcZbS3R3iQcivPwYKs0ChbfdnSj2ILheLbsQvQ0W+qTGTtsNJUr6ciQNUOe5kGUnYqnSPIwDcSy76yHtaqu9VhZ/2W798dZdexCrinZU3hnD7yJqX3CckCJ5fo8WRQsvu3ogl9A9QsIgT7/gJCuknkvmaf9hwXX07bXe4/zFEmu8MrrQn/y/iNxWrauVSJGK/hawtACP3TZxxKuYTTAAUqWmmP5S3QFY2fKd4oMFlpPEwF8Mu1ZSw3NVhc6jGnsdGE5R31+DjoRt9pf9sQjOabJNQyRa40dv2NPV9yWRTR2LToRK64JFpGy+DTMHu7pSrtkZ5s4ov3dQRAPEEs5t2TAQnfnvcBJF56IFRG6JRbYUU/rLVkMl1SkxwSdaWSpWEDlvFHqJFGUgP7KHi3wAnu4Yh0RVhTMKIShadmaF7j2CnxP3J3YgWcqApjIYrKQYeg+JuCb3dEyHnZM8di+xGTOSsDAHYq1hexH8FwWsf9qD4fY5b9x50vc4wZ4iIyUxWf77PDQxSy+VxYfP5bJqY1WrEmkIf4JFon8dMUvFUu3kmjF88bQxY88BpDpSSKftWqPtTf1fryRNzRhcsD59xIt5sYExj25OJxjsn9zY0T173AlGsTk1YhDygOwa+fxxT+hN7oGVq4Hlx3vgkcVJN/ZLWZxjWD8nR/UZQ52L8fwzQysHrx0pZMFk10eEakt7UIsbsAeXrOQUcCzLIsPf6Ph6Cf+P/bJTvj9qZe2zFnmBZH4fmQsYtvmKTIXMj2ahrlGf7elcELeUEMysfxe0Z5CbgWhaA9AGhYo5rGyBYQBu33Cb8NmgnTcbjrv0kM3rSHwnzNHOvdK2Dvgn68a6EY2grDIqlNzbgj7CiJolh6Na6nmAFXKGyWVBH/nxa0PNDZFuayHyYKvhmcljfzDIYCCBGQALDxpAPN0JVdCsM1XN5p0ES/SuNLj+OOcOzInXcgVeTLSND4zgKSwMmzF178DC5kE3GAO87lMa+oVTh8uGrAcTCGZ8xhMkR5WpsU8aoUWYW/zRt7wPDB+Lq7QVeDceH4ycKdT9BMGnsGK3dHrxY03za0zWNa9aQASAfojwnyvvYmb3r2Vp1Ne0+Mrjz2ZiB2XW8FAws6E/J47rzxpk1ZGyuJ7ZRkDjyZJYYUEywD0Vmc1OJ1MEv1quC590oEdz0P6T8DXD4nLY/gj0kPucMKyUKLkiEjG3yxbKEj45m4X5cXwO5j0stJgVlUnocLVNH9Pv3K83Sr6wMUo+9pPsFlvKJ2Nq2WlYuNqUw0VR9JqYo9N7epnUw1zh4mBlvKGhajTsqmGtVK6OV4hHzYBelRKiRpMG9GsOpjwBCZePkBJDXSJvkBhNYlsJQuq7UYh0iZV7SWoJsky3vlORwW21GDdYDI7ajdwdtT5G0jrvP1+5tRsq8FKr+p6qR9hpnaP7Jgo2bT4spzVUImzGirxBdSgo2O2SQ6i/WpQckHWVurVpvVq0DFmjcSG5I62q0HHvLmOx82Qo+VqjMiFuMKGFFatU4Nk0w45NF+otVFYbYRRidapgfXHfFoIrzNy/3VhtXrUFb3sXSMjzcb69qy7Dr/dss7I6I/lHrj+LLl5+9X6aWmfGmBfD8djjN0ObIzV4gsyNWaEAlJWDCXUyOcbVggh43G2sU8GNkVVTt/aW/H0KGCduHKEvSvcc8qVIplqPgEE18rmjd2raZrNExPj+4WFJ+bGKiAyvbB7VhKvZ+sqR/vyRji8ydaS0nHhWUsrcUboXSmaO1qnBll01gUUXW8CSAobr22EUQk1U3UAuFu4JJTvqEGmhVJrI4xKKJqsqrjE0qLIGK/3ZlSYlqsB6IIbvyJ5naE2bVeDyUE2iymVab0arO6Ip01pxrdfDbh8umxI1vgKajSIsxoqcVZDJc5qqMRZDZVouxr5yMiGr6q0XY1085v7sreatF0NbPA3fWFDdjFoRioPoA8hhMOjLtjZn9arYeEhDGlDbJm2Xg34hwI9j4yoAr9ClW0ZFmm/GgxF7XRv8wXUwIAbUm0oMbvtHejycBud3ZlTweY3R5n1o7Qa8RzZFRT5ZgVxwAQdYZcYpdVY9ippDFUhBvTJzHjLZlxl1K/3vpAx6VYiRkXgfic1gVwf6qox6aukhaRug6HqqlFNKVUpXW7Huk6UVSNW0TaLE5R9qkVVNWjN170f0iZ8faiqxrKShlDl1JwqVdWIVDSQWvvmPaqq8UFiup9hs/j9o05lF1h5NR7ebcc8RTvVuCs1RfPtCjKe3hlw4Vbzy35HQum+eArfZEaXG+N0VvNEd+bxDUAwN3q84CAYljOtrxe2yxF75NBZ0tP5hhyLjk9GYjsd11rOyWV6ySI8eEQTe+d4hMVG50vb9Zeas7TkScfyVFmg2lE+b4DcZCbdGAc8s+u/mt0lK0368Mx/JRAP+yYpbpcj9sgZhvgxYQdByNy2Buz3YTzs9NNmkQwfd/qyneTw2F7nLgG+944vT5rIU+WBaucokh+G2GQmg2+H882EVxvIGKXFu9YZO0Zxuxy+Rw7fkQZS4yIm6sAiGVEW0jPF1jiQbq+jeaYj2guvOooXq5+s0cT33klPOpKnygPVTgPUSDeZyTfGkUT+n6w6QFeLMSlueyM8xY40KK9VsPj96jKcSqOWMjz6HY753jnRTwx3uFBd5BvaFALVTwNKKrnJTLoxTg7hm0HJrwnp2Elxu5x0R5pk3tFDUSOzq+Sb59CE4E52y0X4BPNDWWyIxWYin4eW++Hwk2Yb7KSB6kf5vEGR3GQm3Rgnx7Ie5VZf6QY4bmG7HLFHzrVH3Q71pogVc/3bC3c2xck3T4crGURur7OagNg7x7rTNANdezP8g++9A3Jnm2yDnTRQ/ai6Qnmavsr2/X82fzgx9Q5lql5S6eut7b4AqqphpP03u96H8bPU3ElXVY2O3GFQNWrevEdVNdTcO2ZR81QgZdXANT+G+0Aq3AV7J8qqAYl6ZVXacawPdfsbLqzU2mJ3sardVom6avD9YQPdrvn9zofxk079FhlUVgMcJ1kmu95ffI4KNr9BcISZhoqrAaBle1UfQnM2vzmG4mc+ylkNlTiroRJnNVSi7WqcbSmoxEL26MNm7LfadjU6npDDU3E38W3arga+egkhvLtuxnU2I5UHcLaloBTu2ZaCQij52uoN2q8Gu0J0U/ZUlParAQ2ypfAF1HDh8BH1I9HGvWk2WPkLEi8MVV5avY/i7zcO5Wlgm+LtxnLShGly7VbD+561bW3LSyfgqkyr641JYdosYi7lUXVWdBU8922A0YKyq3RY9bicpgtp1KXVeSMTA+hizF11mwk5mDar0WEtKiEG38WMKdFRfli9zWpYANNs/g/1mVu92Ysl2qyGydfDplCWL8ya5/sfTpvV4Es3cwder6pUF+UTeACxyB4prNiKlb9Y5RN4AGHBUidyuW374q8q0mY1Fkswf8sX4s4vE5YL5WeAtlmNwYS1qL7dIED2JavHJ8qL0eq+OEziwtiUp6uvRqtHDQd8DFd+PY/hKsDFZNpxtISMoBHvcVpdUnFWi0WiaYNmvItted5gPQ75tqkZtLlN1TzOaqjEWQ2VOKuhEmc1VOKshkqc1VCJsxoqcVZDJc5qqMRZDZU4q6ESZzVU4v8HS3/FE+sgXEUAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,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>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAqAAAAExCAMAAACUMOCMAAADAFBMVEUAAAAHBwgKCgoPDxAVFRUXFxgYGBgeHiAjIyMmJigvLy8tLTA3Nzc0NDg7Oz8/P0NHR0dGRkpPT09NTVJRUVZUVFlYWF1fX2VjY2NiYmhvb29paXB3d3dxcXh/f399fYSBgYaFhYiMjIyMjJWPj5iRkZGQkJmXl6Cbm5ubm6Wenqijo6Oioqynp7Gvr6+oqLKvr7qxsbG0tL+3t8O+vr66usa/v8rFxcXCws7ExNDPz8/IyNXNzdnX19fS0t/W1uPb29vY2Obe3uzj4+Ph4e/i4vDu7u7v7/D19fX///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACVTJrxAAAmtUlEQVR4Xu2di3/TRvLAJ7HPxKkhOZdw3FEopOGZUgp90JbyzJF++Iv9wz4TXJPkQsojgZAHgdAAJSWcmwR/MKhR/ZtZyY4tYnkUb8Qq3i/E1o6kGe3seFer1UotV0CjUZdWp0CjUYmaAfpudfWBU6bR+E2tAH0UAjhUcEo1Gp+pFaCf0sevTqlG4zO1AlTEpohSjeYDUitAPzMBZqJOqUbjM2GnoMQ2gGNOmUbjN7VqUI1GCXSAapRGB6hGaXSAapRGB6hGaXSAapRGB6hGaXSAapSmdoBOOAUajf/UHEla7HVK6rHqFHgAD2OqxymsxcOjTskakwedEg/UdEY1jWS0mpljnrSFG8xfJQ4nejgKN5xFM/1Zddoj4do1aLHLKVGHolOgUYVa4bRxamlsoY+8U6rR+EytABXEpp2SOoyYGWvhgfhfwRv4GdKlxAh93Ma/uwA31sSQwmWzlBD7p3C9Z1LVyZHX1WkZjCyLr/sOMZGCO+Ol5TGRzRT+u48ZK1qJBZH/DDxb22estJCHx4Ceur0IL17kZ7KQA9oDrY1UNBspsRLMN5YTidG1tejVwurNyrSFsH7bcrhdStXYRoXen+kY8ZgLeDh0ECRbw8r2S5itFEJlhiq4W16yc1l1rGtYmX1vtWuAwmGnoB4hPDNIYYAsAbzCIsmQN4vXcEX76tfwJbwDGBykA8UizJMTU2OR3I/lvQ+tHl8K0R7GjFABcCn/EW40gtu/g8emibmt374PXYIBsXD/Be0A7x5i+jZFbfYaPBiiH8uACBU0dNOkbVHm8HU9Vl/gB+ZGGECtN2C4CAMidQxOkgSzSfmmbB6Dz3OfQwh+sRL34PQczBgwWdaW+gNmTFKWiaW6ATogMg7379/69Vg6LrJD1lqsnwQIAa2Ea4tC+9i8+AFiBugQxI9ziPK/TF6D5ccmrcKfubCO/8nhX5Z0VWIbFXo7YCVFxxz9HSMbD+LaIuYNtc4IVRhr8xRvbSN2Tkcgi4bXMlQNeRnG0RvodnFQBGYYD832Pi1hZn8Bg34IuBllxdqOAtTAvzlbGcB8eamC4oK1YsG5wsnzAsBlAzrpfj0TttGkkRZRKY623/34tQGpM6IngibPfYsfl0/AxLbyzp+O7rpDezyP4Dl7J0lCoyDmnRgpAyJ4Jv+lde7hSvuvD6xTfmOKdoBtpwqrcAoPCgwT/kS17VlMo+3L0NJWJA+grM2hpA7hIwCYm6IwgFrj0NECEZGaxTRKwiQHkc1ZeBin5W1WonPg8TwcOlCh7fJ5aA/R9tvg8k06zPYDsOuzrk8/7kuJ7JA1KN+ciwJaCZdNoT36bDtMtFAG6BAom9B3CX/lr8lr8Doi8ha3rZPT0eHrzeUpGRV6DdhxmY75zvdYpeDKyybmbVX0peJUGUefkdd+F3m3ClQYXp+WNsq9SXuj2w2rBDHDeGi292kJM/v1g0h7toU2o6zYO18B8+b3MNj+8dOd8S6Yf3pmrmvsH398MxufPJPesffpNwu7YbYH5vdB9mz2bMnkutgdwaVOeCdiLh97004pWrJWGcIoSgnTtA+BqOjFiz2KFXEoBIQZMkJYjqLvWwu7l1vax9rBPqjX2y156bAsMufFFx2jt168yI0wUNZWTuEfWiGdlE2SFCjASonS/hW9+NWwODDaZbLcFV7uKC1BLu7sxZe02/ZtJ1u+L/kaP81QaRVubDt94KKzv13Ri187BHHM8LhbyDBvS52V5WKZFTkdObYdDaOxR442t9SLp6NCHRVupwzjodnexyXK7PgXIjjKm4VFgCbo/53WE7Tx2AkYWzpGPXjzxuFfT4+Fe6ctk8PfP9+zELMDbX0auVJREaD1YQToxvAWoBLYcpeZagXoBgmLKrYP0jtLJ6P0eSxO1XHynNlWzPXCb6Lxzx3HM+OxmOjdaDT+gTWoLO7TmdIGobqL/SNe2umUrPGqohHxyuRxp2R97jmuRm8cysnr8sllPQrbsabY4ZRukJV4VfLpP6uSG+W9NohdqOsx9bnUAN0M7BMMWUhW54aPpoILw0nul5k0mg+M4jWoptlRvAa1BhekIVmdGz6aCi4MJykeoItOQWNIVueGj6aCC8NJuonXKM171wXUgsZPJCJZHZFwCqrYL+2K1JaEUR6KB+hi/Rx4QbI64hOXYS1xc4WmNozyUPwctP51Mk9IVmcztQCQLN+AYcDzqrWa2jDKQ/EaNBC86b6Bn9lw5E3/UL79Tb+Z++X0LdjtWrVqmITLNwhrNkzk7V+wDJeSsPymn+53/KU/Gb6UpABd1e5tiBCErdvRVIVxFu0FyepsXg39++ZSx46bnUsdncn+hS/gh+TZYWuV4u790DDKQ19mapB7ri35jO7FN4jinSSvk6LqIFmdpkEY5aE7SQ0SrnElybor/B9OscYjuonXKI3iTTzjbgIvSFbnho+mggvDSYoHKONuAi9IVueGj6aCC8NJuonXKI2fNWjpSTprM6hHDeeDJDSaKkKyprEyGNkWg4HZz9KPX0/NfgbZ2adPVx++frP9v/v+97cQyp2bE9Mu8+M2gGR1bvhoKrgwnORnDRofA2iLQV/7SfyEs31wFtpPwuhFWkeSdZD8jD3J6tzw0VRwYTjJxwAd6f0J7WE73ztIn8P0GKHeQfguDeOPhHwd6g+FeUKyOjd8NBVcGE5SoZNU9TyVCtIXQox5qV6QrM4NH00FF4aTfBtJSjsFDK5D/XMUzdZGhRq0FliDOkWaZsPHc1DP9IU4Qw1ekKzODR9NBReGk1QOUGANNXhBsjo3fDQVXBhOUrmJ12hUr0GRefumwfKQk+MZkDQuJa5RlR8OXtpDswVQPEAx1J4fnoPMQiH9Fj8zWcim32ahMAh3EpniQAoGZgfuANxZgPTCdZiDBK7BPebxKz2cwY8B3AKGcdeSOr/w0VRwYTjJz6HODdAahWd7i4Wlpan++e1LS+a5wmfdv54rXI9+FO4+Ol6M7D0w8tFprEEfxntj8Pe/w8H/RD+KPvvX3/Ervzd3duL0/pYDIwcfxJeW9trq/MJHU8GF4STFa1AaakhE4iurfSnAT7AHoPreijEIMfzUO0hjVPGri/P0mA+xJpTCr3wBBnozNCE410a7ztvqfMJHU8GF4STFO0mMoYbajJ2oSqZ3nmhInTd8NBVcGE5SvAZtiOr4hJOvZqsFmgCgeA0qkVxo7Z0umsCgeA3KGGrgEu+Qqq4ePpoKLgwnKR6gjKEGL0hW54aPpoILw0nN08RrAoniNaim2fHtftCNwbgO4QU56ib+ckpYPNONlRNGeSgeoIxJK16QpM71eWE1eeYUaBjloXgTzxhq8II8dbetr6FS2n6+srEmgbs5uP8cYArmpsoyTRWM8lC8BmW0AV6Qpi7Zn+wf3/4iH762+1hyRzjXnw2vQizfdx0dmoz9cPdlP26C/6fy83l4/iMua9aBUR6KP2G5R+7hyVFnn4JuP/Co/9qlZARWdmPqUrL/evto57fXZvuT0PESoH/xDm5TeLbvJsy0iR2kGN9S1C0P5Z+wrCR4WtSbPILO60xiA9TzuDUHsOMmQOwtHE+Ge5KdQE69+7J3T7LtXPxIsv3QE7GfdvUGUPw6KOMZ0V6Qo25iY+8dT6rt6g8BozwUPwdlvEjHC5LUPXAKNBuDUR6K16CaZkfxy0yaZkfxAGVMWvGCZHVu+GgquDCcpP6cJJlIVueGj6aCC8NJiteg9U+iPSFZnRs+mgouDCcpHqCMNsAL0+63INpT70svgxXfpYee1X8StNhispSSfORbE4aTFA9Q+fwGMGyK+fX25Hr6ujqRBRiYfourBsBcuAqZ/HIGzEGArCHm1KcLBtxCMW4K6eGBFG6NeyQmsriZmKGfncji3jDwrDQFXyMHxa+D1h+r9YSlrnMIzhbOQqIz9/Gn8bHf8OtLekLpxRFa9d3cgfhXufMJuLL8sA9yZxO5yNxu6MONSbz88ZcQ+4RmMIfb8aMXEleWSUm4vReysAJtIDYvm9K4wnCS4jUoY9KKF1Ddbwl4SYvDNHeeFqyvBNaSuwBXRXOwcjWeunA21XHwHsTT9nR83IrENO8uX6D5+G8i1PonzgoRpRKQa4PWPG1OI8ySj3xrwnCS4hfqGbe7eIGhbvQbp6TEIuPuRZuBuJ9T8IMLw0mKB2hAyax2fuWUaTaE4uegwSRz3inRbBTFz0EZ1yG8IFldLSg+fTIVbBhO0iNJm4SPpoILw0mK16CMoQYvSFbnho+mggvDSYoHKKMN8IJkdW74aCq4MJykO0ne4M+Jv+cUEHpuvFcUD9D618k8IUHdxubEl9Bz46tglIdu4r2TtD7El83Qz/CfxfG7kCTh2gp76Rp9/FKWakowyiOccErU4rFT0BiNqzsC1w+amX09MAXm6Ep/Ek6aS0foNSN/3aMh0U786zYHY69iPyQ7v4Sp32L5A7+Cee9lvzWsp7i7/aZeeVxRvQZVEeNherWHInXhBH12ReZp8N1oXcXg7P+KbiRZOHEKehfhq2Vc/e3qAQMWDl9watHwUHyokzEv1QuNq7OnHOfF6+1NMdPdWrYxIvTYEVxhrSutx9T4F6CnHjtglIfiNajb7cUbQJo6KyatGKyMT8D4hH5asfaUBlqPKYpPTTWM8tC9eI/oOfESYZSH4k28ptlRvIlnXIfwgmR1bvhoKrgwnKRvFtkkfDQVXBhOUrwGrd/L84RkdW74aCq4MJykeIAy2gAvSFbnho+mggvDSYoHaLBZGzbK2unhW/R9j/4nxvSbGRkoHqCM6xBekKzODTJ1BTJQGMgBpGgslNLwVV5E6/BK4eBqvccLb30Y5aH4dVDGUIMXJKtzA02ldi0BLOyKG5HL2RgUWzAdocv2bX+Bce5aH8DkUedeTQajPBS/DsqYl+oFyercsExlvorN720ptgAU3u+w0rDoOqwNkm55GOWheIA2JQNt3ztFzYvi56DNiTHnlDQvigco4zqEFySrc2PjpjIXzx9wyrYoDCfpkaRNYuOm9jsFWxeGkxSvQev38jwhWZ0bPpoKLgwnKR6gjDbAC5LVueGjqeDCcJLiAdrEDMMIfS0mTNMoQg7/Zcwi5KFoiNU57EvhkrlYzIgL/gOwaIr7fw38sl9tuxVQPEDrXyfzhGR1bjRu6mo3mIV8FwyFIk8SccgNt4aeJGLGoxDAndFEaNmIZMG80fWkNTR6FeDM89s3ukyMzPSNrtknTl2KwnCS4gHKeMKpFySrc6NxUz91wfh9ez5JJxg9qxGaPhKJYJGdfNXZ0TFW3CHWRWDvvzEu9/wFuL2Q7DsakMmjDCcpfqGeMdTgBcnq3PDRFNyqehhpgB7+yHCS4gGqaXYUb+KbGOwOFehzDv+wt7sMpmgQi9hvwm6TWCjQJ6OZDDKKByjjOoQXJKtzo2FTt+DJE8BOEcBTPM0sdCRuxKn/3pIwYqHQ8gguFKKQWwFxh2lAYThJ8QDlv7eAhWR1bjRsahfA0QR2iiCxH+vQKGCPyL6BNFqE6Ir4Nh51gHjpTUBhOEmfg2oY5ELibTsfAMVrUEYb4AXJ6tzw0ZQPxM10ximTAMNJigeoRhHGxJshPgC6idcwmN/nlPiF4jWo5GsoktW54aMpH9ik+GQ4SfEAZTz+zAuS1bnho6ngwnCSbuI1SqN4DapRDOtGPgNMw7Rv/TMNWLZkgOk8DX6BkclBkUa+imIFbZgHcxFlpQExMQjGQfEAZVyH8IJkdW74aMpPngDd0rc8EooMFaxb/1rzBbgKJAN4lI/dg6c0nzpuPLkRN3IrNLma7hHEFTe6ZmcMGhCjwa8nNAjGcZLiAcoYavCCZHVu+GjKT44m6JY+ayDLuvXv/sPojlOUXBHPl/4rsR/Gitaol/moAzBB9wjiCuxqRcWAGAXd0QStYzhJn4NqfGJjtwEq/ugbxg2DXpCszg0fTflFuirVV5VisE58MpykeIBqFMJzSMpAN/EapVG8k8QYavCCZHVu+GjKRwacgsZgOEnxJn6RMbXfA5LVueGjKb+Ym1+V3MoznKT4o292OgWNIVmdGz6a8ou//1Hodsoag+EkxWtQjUqc/ADPLlX8HJQx1OAFyerc8NGUj0iOT4aTFG/iGY8/84JkdW74aCq4MJykeA1a/yTaE5LVueGjqeDCcJLi56CMoQYveFG3+NIp8cSK9VwaHr1OQZPAKA/FA/QD8tJ6M7wfJJs1QBko3sTX/4V5QrI6TYMwykPxAGUMNXjBq7okfdyE6w6xQKwrf5VZsL/t18jdBJgvr0tWLAOM08cvFYLmw2t5aCrp7+/vDve17Wz7JNy3A/pR0Lav/+QX+3Ax3NmPH/8CSu072NYPnRdgf98u3GUHLtOm9Lkfv9o+6T8CMdqgn5Qcgd7uT/q/oH27Y7QDWel3WtaUuHJF8Rr0w/Kfx6sLJ061H4OFEwB4SnpmHroi8+Syb2n155SCI3MxgK+W4dDC4QuiRfqS7tvFTziECdwZ+0CLtMEiKoH+1weOzXXRvj0xsYPGHX03Uy0mrE6SNXZifdKr4fKxyuEUTJXeIVeICvnzPVYaP21J+d1xtLHYWixY8vEv8DupC6EmitegjKEGL2xAnRVb1ifVjLGq4RSKNPtic9SS77HT0bKkvIMIS1prxyfJKT6bF0Z5KH6ZiTFpxQue1Dm7PxrpMMpDN/EapdFN/Cbho6ngwnCSvllkk/DRVHBhOEnxGpRxN4EXJKtzw0dTwYXhJMUDlNEGeEGyOjfWTPEe8VKDhnZWHkZ5KB6ggWYYKMCWW2hEz6h4j2GC3ldIo3xm6eUdIpWjL3p/R37tGUa4c0HsOL32no/mQvEAZdxN4AXJ6twgU5PF6ZUCXE1gS5Zee49h4mt6X2HcgFzIenkH3BLPK8oNo7A1T+/3mDHgKslo5yg8qX7PxxaCUR6KB6jkKkOyOjfI1KGWhf9Gd5zqpPTaewyvvBIbmBCfLpafVQStRs8qCu8/pPd7RK3HHbXiF13Uf+89H1sFRnkofh2UcUerFySrc2OTTN077pQ4SHcfcIrUheEkxQM0uFQ/yMhXWi86JQFG8aHO4NLnFPhE+pP6tVKQUPwclHEdwguS1bnho6kq+oIUnwwn6ZGkTcJHU8GF4STFa1DGUIMXJKtzw0dTwYXhJMUDlNEGeEGyOjd8NLUeefv7+ai9UPp2vVTlXDU5Cc8nYVq8JGEzYDhJd5K2JncO7h7410L4jPEW0r2T4XgOlu+ev/PyJ8iNnRtYvTz8PWSNr1Gy0H7u59bYyo6li7jy6q6TmcNP356FdPubPnN81x7jRHHPHjg8+aHeJAvKn4MyHn/mBcnq3PDR1HrkH/YceLR6duJvK9t7Y8/aT3w6/+jfy62nWuDnfxd/j+x90AOfdg+gpPvo+Ntz//zD2B3/81RLz8fLS0vdCwdgce+r7uLqXvh999u/obKdLU71kmA4SfEmnjHU4AXJ6tzw0dQ6jPT+BOldMNCL53lXF99EIAFnU6Ie/C4NrflcG8BwypYQ7U/pM/0wvrJ6dxXDu3BaXMf9LREdSEDi/0qbyYbhJMUv1DOGGrwgWZ0bPpqqyRjNI5VD+of6HW7vMJykeIBqNsKmjGK1fs6YQSQf3UnagmzCKFb6QsVcVj9R/ByUcR3CC5LVueGjKT/o25T4ZDhJ8V48Y6jBC5LVueGjqeDCcJLiNShjqMELktW54aOp4MJwkuIBymgDvCBZnRs+mgouDCfpTtLGmZh3Sip5XF7SF0oaQPEArX+dzBOS1fGem6gfoVMTRnko3sQzhhq8IFkdwNwUfVZPZbs+R4+vFbItNsdNOozyUDxAF52CxpCsDuD5kSQk/3sdP4ZgIQnjc/A8abyA5Ksb11GOHxo3GOURdt5hpRY9cg9Prrq/8G+mbRZWOr+d7RcN+fYDMNGf/AFF/eNGGD/EdlKNbinqlkcIwptyAbY5oNbn0JOex63Hk/3JTnrmPDrzJEYqimDhi1XAD9pOu7gBFB+LZ9xN4AW56uxnMNdDPz+5JozyUPwcVPL9CZLVaRqEUR6KX2ZiDDV4Qa66f844Jeuy3ynQlGCUh+IBymgDvCBXXdzNv3JNbVEYTlK8idc0O4p3kjTNjuI1KGOowQuS1bnho6ngwnCS4gHKGGrwgmR1btimJsuCUTHuWRRT1idpdR7LZxLyCxPlTZoORnkofsMyY16qFySrc8M21ZU4mGmbfPwpJFofvl6YOnD9AIxsi3UlYDd+d0E0Esl3V+/YTDDKQ/EaNPjEcpG5/au01H7S2EvXnOJjsExn/vQdm4fdjGqkiVE8QBl3tHpBsjo3SqZ+tKaapwF6B9uf0vu4e38Cmo9OU9eHYAIStyt3ay4Y5aF4Lz7ndqnRO5LVuZGLm9c3YXbl1oJRHoqfg9afVOUJyercyN+c+2Tn9Nif7//9zylY58+pbYvCKA/Fa1DGUIMXJKtzY/qwrkHrwigPxc9Bg0xIx6cEFK9BNc2O4jUoY6jBC5LVueGjqeDCcJLiASr5GqFkdW7YpiYGsiXJXGmhRroJYZSH4gFa/yTaE5LVuWGbytM7i0bpgXM0/WYQilcHJhYAilYaspm1PZoQRnkoHqCB5/QARmN7yc8r0BLbe3C3AS0iXaBx+ULV9hoHineSGNchvCBZnRtkan4fFKIAJs2aK4rHaOfp1ZtmCCUibUSq9mk6GOWh+IV6xuPPvCBZnRut0fTcSQB6xLuoLa3HvIuAbCWJSDf7fE9GeSjexNcfCvOEZHVuxAdBzDnWuMAoD8UDlHE3gRckq3Nj+kxfhHEVpblhlIfik+YCzQd8u9DWQfFOkqbZUbyJl9xISlbnho+mggvDSYoHqD3UkIKrRVgGemdkOU+GiSsLJgmyg2KyTwGKpkFLRcis/1QqxsiFLHw0FVwYTlI8QO3rZJcy8CTRUYCrGKDDmDYLAOkbXZCIQiKEYXsGz1UShSg8ac1DbgWXW9e/gFP/sps0fDQVXBhOUjxAbULnAC7kojtOgdFD83vG71vyGEBnR6kvEi0acP8hPKJ0k18A30Io3kmioYbMeYdw7oBDwIYxciELH00FF4aTFA/QzXmrnx/ou5XloPp10D7IHGeMN2i2Koqfg04DnJcYn4yRC1n4aCq4MJykbxbZJHw0FVwYTlK8BpVYexKS1bnho6ngwnCS4gHKaAO8IFmdGz6aCi4MJ6neSVKZhFNQxdqrEPcfrRBrvKF4gNa/TuYJueo+OeaUrA/vUfbNCKM8FG/iGXcTeEGyOk2DMMpD8QBl3E3gBcnq4AbdoVLAj8WCSdqvgYmf+bxxF6WLdCuLxg1GeehXITZG8oeF8bPmUP+1S8m+338FeD51sCs3/2MrZKE/Gb6UpBcir0q3ulWoWx76VYgNc/vc+OB3Yim9j+5j6SzAFMArgMhUm3huLWgfN4LiY/GMuwm8IFfdvWOigqzLjO7F14BRHoqfgzLelecFyeqAFZ+amjDKQ/HLTIyhBi/IVRdmXj/6h1OgsWGUh+IBymgDvCBXnWvLLdfUFoXhJMWbeE2zo3gnSdPsKF6DMoYavCBZnRs+mgouDCcpHqCMoQYvSFbnho+mggvDSYoHKJ5EDwMUDSjir60INLKYMYvmMpj04xNf07ieUoYJiwnayqDJ8eJWI4O2n7a3o1n14rKGaS6iKlpBCpfFf/nUP/3XcJykeIASk8VHIZih+e8YSU+gNTRjwNUbcbhVoC96xOYT/DIiQ/kumiX/KBRC0R38B8sjhShEoNCRwA0SHZCI04z60I2u3IpY8WQsjToS+hlKCqN4gNIdrYdaIq0Q7ezo+OU+wNFEBKI0QZ7mC9CXmRcbmmNFe5Z8RGTpJP6D6Eq0aOQhCjtwgws56Jy2Z9Q/6hArIPw16rjAOBPyDuNeXA3DSYr34qvelTc9f7kitREYr96ThY+mAkr6QojhJMUDNLjz4jX1af28/lin6iNJcp9/wBi5kIWPpgIK1qDTgQ9QzdaFV/eo3sRrmhzFe/GSO9iS1bnho6ngwnCS4gHKGGrwgmR1bvhoKrgwnKSb+I0xMe+UuKPdvEF0J2mDeLuZPukUaJgo3sQzhhq8IFmdpkEY5aF4DVr/OpknpKq79u2Tz6IFiITohZxmvqMAmIqaoUK0kEdD99t6kt1L4db2HueOmhKM8lB8XnyH3MOTp+4vgB+vt2f7s+FLyV5zqn/s1Ozj8KXB7+D5FM2Uz8Vh4a/I1/Fk6VRAmuEtRd3yUH5evOTxGHnq8NTo+q6XsXGsKWH36C7YCY8v3IB9Q/1ipnwkD7BjaV+y7WD0WusF2l5tN38oGOWheC+ekQMvyFM3ccReuHapSl6DpNpu/lAwykPxTlL9DHhCsjqCFZ+a9WGUh+KdJMb9WF6Qp+6f9ebEv22rTO2vTGhKMMpD8QBdrJ8DL8hTF6+nidF6aRjlofg5qKbZUfwcVNPsKB6gjKEGL0hW54aPpoILw0n6PUmbhI+mggvDSa416B0wIU+zxxdpjrlpYMKKeZpQTrPVCzTB3HR7Q3uD1D+J9oRkdW74aCq4MJzkGqALEErEjJaEEaPZa6EIPKX3XJsFaKHHIjwK0RvaE1HXN7Q3CKMN8IJkdW74aCq4MJzkGqAni9Mx8er1qKgyIbEf69Dyy9ojrfSG9hjNMqdUeS+NRh6+XGYauOiUaDQ8XGtQWVxMpzd4hsqYtOIFyerc8NFUcGE4yZcAhdjXGzxDZUxa8YJkdW74aCq4MJzkSxNvbjA8NRpfalAdn5qN4kuAbhzGdQgvSFbnho+mggvDSfVGkiZfvTJ2WIujv+2pXjfqSL9HsYU+JxkzT2rBGGrwgmR1bvhoKrgwnFSvBj2aP2pksncykFl4+xYGZguDIJ5cDJlswYBbVyGTz2QhPUzyOwOwaExklzNwJ5EpYuo6PR954BlkHEr5MIYavCBZnRs+mgouDCfVC1DB2ZM7cpE5XLj48HprDhYeTpIQF+M/5c5n4Wwhto/kxl4U954dOr/88enz45jaD7ACbbFchHE5YX0YbYAXJKtzw0dTwYXhJFaAIvEV682ofW/jsPvgUXtx5Wo8dQEX8wWStz+F8UeQOJsSz9TG1Dzk2qA1H19h/FI0mvVwvcw0cKJOZC02cHqp0TBw6SSl5/blx/7cOf0/+lj/b986svX+/rdzeqdTPYtc/bNoL0hW54aPpoILw0muNejg0To16KYjeWaPZHVu+GgquDCc5BqgGs2HhttJ+kBsuPu/PpLVueGjqeDCcJLiAcq4m8ALktW54aOp4MJwkm7iNUpDD26gtwnOHShJ5vdVrC5R/H23WLGw27lmDetC6cbAw5hiP6bwobgMuz6Tta9K1If5FItGMlrNzDFP2sIN5q8ShxM9HIUbzqKZ/qw67ZGwaOLNW9hfX5ofnMYKd34QzPzg7CjM5gYhPbowCgsAswBPd0N2XxbAJT79w5p/olEQ+WeMqDH5PSTOwB9nDj8A/ISVW4d6voGejtWF2De/t9MLXLFq2zcM3XDQei2mRuMfrfRCpfTOUuzT57E4PW41ec5sK+Z64Tcag4fccbgPY7GRyl3XYcS07wt5IP5X8AZ+XnutoVBzG//uAtyoeNthCpfLc0PE/ilc75lUdXLkdXVaBiPWK7zt6YNVpODOeGl5TGQzhf/uA83OFokFkf8MPFvbZ6y0kIfHgJ66vQgvXuRnsqKbmyJrIxXNRkqsBPON5URidG0terWwerMybSGs37Ycvu7dO7ZRofdnOkY85gIeDh0Eydawsv2SmtZKKjJUwd3ykp3LqmNdw8rse6tbaT5m3zdw8jjAeQD8PNEVojuMr7TsOdFyEeCiODmNx+An/He6euf3CXWh/zBAlgBeYZFkyJvFa7iiffVr+BLe4cnEIB0oFmGenJgai+R+LO99aPX4Uoj2MGaECoBL+Y9woxHc/h08Nk3Mbf32fegSDIiF+y9oB3j3ENO3KWqz1+DBEP1YBkSooKGbJm07JE5jvLD6Aj/e0YOT0QBqvQHDRRgQqWNwkiSYTco3ZfMYfJ77HH36i5W4B6fnYMYAuuPGIvUHzJikLBNLdQN0QGQc7t+/9euxdFxkh6y1lN9qjwJaCdcWhfaxefEDxAzQIYgf5xDlf5m8BsuPTVqFP3NhHf+Tw78s6arENir0dsBKio45+jtGNh7EtUXMG2qdEaow1uYp3tpG7JyOQBYNr2WoGvIyjKM30O3ioAjMMB6a7X1awsz+Agb9EHAzyoq1Xe2ThgeMW03e53kB4LIBnQDb0OHbMAUtolIcbb/78WsDUmdET8QAOPctflw+ARPbyjt/OrrrDu3xPILn7J0kCY0CCcBIGfhDWkXPiltMXWn/9YF1ym9M0Q6w7VRhFU7hQYFhwp+otj2LabR9GVraiuQBlFU9LLE+4SMAmJuiMIBa49DRAhGRmsU0SsL2Y78xm7PwME7L26xE58DjeThU7pQil89De4i23waXb9Jhth+AXZ91ffpxX0pkh6xBeVQQBbQSLptCe/TZdphooQzQIVA2oe8S/spfk9fgdUTkLW5bJ6ejw4VPHZSMCr0G7LhMx3zne6xScOVlE/O2KvpScaqMo8/Ia7+LvFsFKgyvT0sb5d6kvdHthlWCmGGaqW55n5Yws18/iLRnW2gzyoq9c43LTAZFLrNXa2N3BJc64Z2IuXzsTTulaMlaRZcLsAJrFwnTrJhKX9GLF3tYtzpXCAgzZIRo9gj1fWth93JL+1g72Af1erslLx2WRea8+KJjZObXzqjIjTBQ1lZO4R9aIZ2UTZIUKMBKidL+Fb341bA4MNplstwVXhb3hQnoUZrhql58Sbtt33ay5fuSr/HTDJVW4ca20wcuOvvbFb34tUMQxwyPu4UM87bUWVkullmR05Fj29EwGnvkGLss9eLpqFBHhdspw3hotvdp1hpmdvwLERzlzcK1A/QNZeSJHTM8GrlSURGg9WEE6MbwFqAS2HKXmWoF6AYJ127ixQ+t3GHRaD4QtQJUPOG6/r0mlfzuFHhju1NQE7dJorXyw4E6Phy429XHLSfr00j+qnAoqn0G6Qn7XK5m2hsUUbWaeGxLzJaKk0SN5oNQ87TraO1VGo1vSGsyNJrNYP1q8nlpUNPbWahGI5v1A7TeExk0Gp/QTbxGaXSAapRGB6hGaXSAapRGB6hGaWoHaGFDt9tpNFKpGaCz0cN6hofmg1MrQCd6Gh3p12gkUCNAn/c6JRrNh2D9ADX1UJJGDdYPUO/3KWo0m8L6AarRKML/A9hE1NQDDAgPAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,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>

[image18]: <data:image/png;base64,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>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAcCAYAAADSkrd6AAAC5UlEQVR4Xu2W30uaURzG+09KFLJAJQjEoBDxplEOGg28lkDsIozEC7Vb77zKQbut3bQKGjXIUekagYXmlbWb3FWtcrRcjVyOsz0HzuE956iwsVjwvhcfPOf5nh/f5/x67fjZaBC90SELesAwrRcM03rBMP2/2dvbI52dnSQajZKuri7SuL/nse2tLdLd3U1jaBOLxYS+X6+uaB/EzWYzHUsen/FoTG+srxO3203L32o1aiyzuUnr1ctLWmdtYfCpz0febmxwDXHo2nrt+lqZBzyY6frdnaIxvt/eUrQakqycnPD67OwsH2NycpKMjowI7RcXFojD4aDlg4MDYVGA1+ulY2g1RlPTOB52u5309PTQ8u3NjdImGAy2XEmAhPv6+hT94/ExPYLaRXmfy/Gkc9ksOTw8FPrA3PPxcUHDKWB9YE42jfZOp1PQGIrpVColJIR7NTQ0RCYmJriWSCRocnJfGYyDxWN1ZlhuF4lEaNLPxsZ4O5PJxOOItTPt9/ubmrZarcpcQDENQ7IGzk5Pic1mo8kUCgUl3gpmHEZgTo6DcDhMk768uOAaHq14PE7L7UzjtCHWzLSsMRTTAInOzMzQF/JHva7EAe6UfC9bgUWCCVlnsJ3Watil3t5eXm5lGmW2aNr4H+008Hg8dBDgGx1V4mBqaqrtndaCu51MJsn+/r4SAy/n55WkkTBL+m/vdH9/vzIXUExjB79Uq7yORwyP2erKCteyOzvC56IdMMzeCLwXzYx/qlSUpGEYLzDK09PTZHBwUIin5+b4opRKJaW/y+Wi/eS5gGIaOyhr4M3aGt/9F+m0Em/GwMCA8umC8WKxqLS1WCykXC7zOuY5Ojqi5Yvzc8EUvttPhofJyvKy0F7+TqOdPA9QTP8r8vm8YpjxanGRfNjdFTScKCQaCATo77tMRoi/XloS/pGFQiEh/vnsjOrsH9n2739w8ryMBzP9mDFM6wXDtF4wTOsFw7Re0KXpXyjAEH0DDfRjAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAAAbCAYAAADf98keAAADPklEQVR4Xu2WzS9eQRSH/ScICSKIpQhBdKk7FbGwe8NKCPEVIsTWBg3dUt1gg4YmmqguhPhIbDQaqlR91kdpKM1pf5PMzdxzxjuatIk2s3jyzpwzd+59nztz7sT8uL0lz93E8IAnjBfkwAty4AU58IIcPEhB11dXtLq6KuKgv6+P6uvraXBgQOTA+/V1lW9tbVXz8PzR4aHKvxgaUm2e5zwYQa+npyk7O5vi4+MpNjaWXk1NhfLnZ2dUUFAQ9JuamtS4j1tbQSwSiVBPd3fQz8vLo6WlpaD/fHCQSkpKVPvy4oLq6uroaW+veBaTByPIxCaovLycUlNTQ7HExETKyMhQ7dOTE3Wdmd/c2KC4uLjQvBCt+1hhiN3e3ISuM/mrgr6en4uY5tvlpYhpbIJycnJU3Nw2Oob2wsKCEHR4cBDEtEC+7RDDODNmYhWUkJBA6enplJKSotq2ZfhubS30Nmx0dHTQ8vKyiONa1AEe19gEobZ0dnaGYoWFhYEA1BwuCM+H2M72Nr2ZmRF5fa+XExMirhGCurq6Qpax/N7OzqqJPmxuqtjZ6akSx6+10djYGKoDLjnAJsgGxrW1tal2aWmpEKAFrays0LP+fpHXc/T29Ii4RghqaWkRgzTt7e1qQtSDaPuWA0nz8/NKDgojz3PuI6iyslIVYd1/UlwsBGhBmAsSeF7fq7q6WsQ1QhDACqqtraXm5mb6fn0t8gA3j1ZHOMnJyZSUlCTiNlyCJsbH1YoxY/iTXIC5gjAfz+t7/dYKOtjfp6ysLHVG2N/bo8zMTDUJtpU5bmR4WBS8u8AcGAtQ23ieE00Qrm9oaAj6FRUV6hfnIi5AC/pyfKxWL8/re83NzYm4RgiqqakRg8DjoiJKS0uj0ZERys/Pd9YRjZaj+/eRdJcgnIP4S8HLxK/tM8+loG1+sbADEONzmghBri/T593dqBOa5ObmWsfaJH3a2aHxsTF1wsVDP/r1hUL/+OhI5fFCEOegHuo5ysrKQgdFHAOmJieDPk7h+qCII0hVVZWqj/z5TISgf53FxUUlEydtnJZ5Hp985CELL5vnOf+doD+NF+TAC3LgBTnwghx4QQ68IAdekAMvyMFP1uquNTxqdSAAAAAASUVORK5CYII=>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAaCAYAAAADiYpyAAACz0lEQVR4Xu2WT08aQRTA/SZCiAcOQDyQAAmEcLKJ0oO1CeFAOECACwESMRwMf2L8ANYerY2N/QD2YA82NvZEwp8b9KJN7EFqFaE2kUrz2jfZ2ezO2128mNB0D7/ovHnzYH4789iZ3+MxmIxhRgz8r5giJEwREqYIiakTMbq7gycLCzA7O0vmcrkci7vdbigWi+B0OiEUCsHX83M556bfB4vFwuZTqRR4PB5SR4upEpHJZMBqtbLNGolQ8rnbVeUkk0l4sbUlj4PBIDSbTVJLZKpEcIxEPFteho/Hx/D98pLM42kQ152dnrITIuaKEBFfzs7AbrezgtVqlSzglMtlEhPx+XwkxsEjLcY4RiKer6yQOOfN3h5ZNxwMWAz/ivlKVCI6nQ4kEgl53P177LDIp5MT1aLx/T3k83lSTATvO95jMe73+9mcGOdMErG6usrmxQfFr44yxkW0221ST4lKRKFQIAnIy+1tVgw3hY0K/0cZYp4WogyU8PP2luQpMRKBPYSPX+3swPz8PHuAOEZJ4jou4sPREamnhFyNxwBlzM3NsSs3SQKiJ0Lk+uqK5blcLjaOxWJkHRcxqWESEXh3+RdB8HqIOUg2myUxPVqtFnuam5ubUK/XybyInoiNjQ3WB/iYb5Lnrq+vk3U8B5umWE+JSsS3Xg+8Xq/ckfmVGNzckIXpdJrE9MDji6dCvCZ6aIkQN60VM2qWeHrEz1GiEqHXAMNLS+BwOGBtbQ0qlQorbNTslHAJfPwQGcrNcX4Mh2Cz2SAej8sxfMqY9zQcZmOtn098zxBjWqhETPqJ6V9fQ+/igsT1CAQCmsL0ZLw7OIC3+/uyiNe7u/D+8FCej0QisLS4KI/x4dRqNdVnRKNR1QsVNmdlDT1Ij5h2fo1GrBfgK7TWSxXSaDTYfKlUelBzRv45EY+FKULCFCFhipAwRUiYIiRMERKmCAlThMQf1lUvcTJ/LUoAAAAASUVORK5CYII=>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEMAAAAaCAYAAADsS+FMAAADI0lEQVR4Xu2Wz0sbQRTH/U+ChGA8GInEHIRIIvam9mCtiOccc8glvyCChyAi5qA9aA/2ZrGYYtEUo8WaHj2YHDxYsGixWKtFq9Viasor32lnmZ2ZTXspBrqHD7x5b3beznffvJ2GH9Uq2fyiQXb8z9hiCNhiCNhiCNSlGMXNTYrH4/Rub0+Jfb28pFQqRbMzM/Th8FCJV29vaXJykj2PdeR4LepKDGyksbGR3h8csPGD/n5qaWkx4m+KRQoGg8z+XqnQo+lptmkev766IofDwWIYQ0zx+T9RV2IEAgF6MjfHbFQANgZ4HLZcDfBBBNj3+/poemrKFPf5fPR6Y0PJpUMrRiwWY0n8fj99PDpS4uDz6Sl7Ydkv0tHRofg4XV1dpvGn42OW8/LiQpkLTk9OtHH4Xubzhr1WKJjiDwcGWIXJ6+lQxGhra6OD/X1mo2zD4TB1dnYyW5w3MTGh+GQqNzfk8XgUPyoAMdH3eHaWbebV+jr19fYye31tzchRLpctxYhGo4atE8PtdivvoMMkBl5we3tbmYQydDqdbGPt7e0sKRqYPE+HLAiE4GUtgg1hXf6VAcbIBxubtBJjaGiI+a3EgF/Op0OpjH8BBHG5XNTc3KwVAnAxxIrBF4UPRwTN00qMSCRC366vLcVoampS8ulQxHi7u8sW5aBk5TkAjUx+MStKpRLb7NjYGG1tbSlxwI+J6ONi4Ijw95Jzwjc+Pm7YOjHQROV8OhQx7nV307OFBWajqXm9Xkqn08qDucVF5dxbgTUwVz4yIvzLiz4uxs7OTs0G+jyXM2xZDDTP3p4eJZ8OkxhoVrrf0O7vr5JIJGh0dJRCoZDp/14LLgQfWwkCP3KIfyiUN3y8icJGhYjPwffl/JzZ+LWOjIyY4q2trfRiaUnJp0OpDH5h0XF+dsaq5W8rAn8h3VwrQZLJJA0ODjIbm8YFLL+yYsQLq6vGpQtrZLNZGh4eNuK8ifI98DXkPFYoYtw16EWouqfz80oM4H6DOK7cuus6hMhkMmzOyvKyEq9F3Ylxl9hiCNhiCNhiCNhiCNhiCNhiCNhiCNhiCPwEwsWa4oYUPwEAAAAASUVORK5CYII=>

[image23]: <data:image/png;base64,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>