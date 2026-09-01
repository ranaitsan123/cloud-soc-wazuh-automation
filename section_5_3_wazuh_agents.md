### 5.3 Mise en place des Agents Wazuh

La collecte de télémétrie constitue la pierre angulaire de la supervision SOC. Une fois la stack centrale stabilisée, la phase suivante réside dans le déploiement et la configuration des **Agents Wazuh** sur les hôtes surveillés au sein du sous-réseau victime (`10.0.2.0/24`). Les flux de télémétrie et d’enrôlement sont acheminés de manière isolée vers le Wazuh Manager (`10.0.1.0/24`) via les ports TCP 1515 (enrôlement) et TCP 1514 (collecte chiffrée).

#### 5.3.1 Agent Linux : Déploiement Automatisé et Enrôlement Réel

Le déploiement de l'agent sur la cible Linux (Ubuntu Server) est entièrement automatisé par le playbook Ansible `playbooks/victim_server.yml`. Le processus s'intègre nativement dans notre chaîne d'orchestration :

1. **Installation du Paquet :** Le playbook met à jour les dépendances, ajoute le dépôt officiel Wazuh et installe le paquet `wazuh-agent` :

```yaml
- name: Install Wazuh agent
  type: package
  packages:
    - wazuh-agent
```

2. **Configuration Dynamique de l'IP du Manager :** Pour éviter tout codage en dur d'adresses statiques, l'adresse IP privée du Wazuh Manager (récupérée de l'output Terraform `wazuh_instance_private_ip`) est injectée à la volée dans le fichier `/var/ossec/etc/ossec.conf` :

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

3. **Activation du Service :** Une fois la configuration réseau appliquée, le démon est activé et démarré :

```yaml
- name: Enable Wazuh agent service
  type: service
  name: wazuh-agent
  state: started
  enabled: true
```

#### 5.3.2 Agent Linux : Collecte de Logs et Surveillance FIM

La configuration du fichier `ossec.conf` dépasse le simple enrôlement minimal et prépare l'hôte pour la détection proactive d'anomalies :

* **Analyse de Logs (Log Analysis) :** L'agent s'abonne aux fichiers de journaux système standard, notamment `/var/log/auth.log` (capture des tentatives d'authentification) et `/var/log/syslog`.
* **Contrôle d'Intégrité des Fichiers (FIM - Syscheck) :** Le module `<syscheck>` est configuré pour surveiller en temps réel (`realtime="yes"`) les répertoires critiques, tels que `/etc`, `/bin`, `/sbin`, `/tmp` ainsi que `/var/spool/cron/crontabs/`. Cette couche est indispensable pour détecter les modifications de cron, la création de fichiers suspects ou l'injection d'artefacts lors des simulations d'attaque (Atomic Red Team).

#### 5.3.3 Perspective et Extensibilité Multi-Plateforme (Nœuds Windows)

Bien que le sous-système de validation active et de réponse automatisée de ce projet se concentre sur les nœuds Linux (scénario d'attaque de persistance Cron T1053.005), l'architecture globale est conçue de manière agnostique et multi-plateforme.

Dans le cadre d'une extension de ce Cyber Range à des environnements d'entreprise hybrides, le déploiement sur un nœud Windows s'appuierait sur l'exécutable MSI en mode silencieux :

```cmd
msiexec.exe /i wazuh-agent.msi /q WAZUH_MANAGER="10.0.1.X" WAZUH_AGENT_NAME="Windows-Victim-Node"
```

Sur Windows, l'agent utilise le canal d'événements nativement structuré (`eventchannel`) pour s'abonner aux flux de sécurité Microsoft critiques :
* **Event ID 4624 :** Connexion réussie (Authentification).
* **Event ID 4625 :** Connexion refusée (Tentative d'intrusion).
* **Event ID 4698 :** Création de tâche planifiée (Équivalent Windows de la persistance Cron).

#### 5.3.4 Sécurisation des Flux et Validation de l'Enrôlement

La clôture de la mise en place des agents repose sur la vérification de la couche réseau et du statut du cluster :

* **Chiffrement des Flux :** Lors de la phase initiale d'enrôlement via le port 1515, le Manager génère une clé d'authentification symétrique unique distribuée à l'agent (stockée dans `client.keys`). L'ensemble de la télémétrie acheminée sur le port 1514 est ainsi chiffré de bout en bout.
* **Validation de l'Enrôlement :** Le raccordement effectif est contrôlé depuis le Manager ou l'orchestrateur Python via la commande CLI native :

```bash
/var/ossec/bin/manage_agents -l
```

L'affichage du statut `Active` pour les agents enrôlés confirme que les Security Groups AWS et les tables de routage des sous-réseaux privés autorisent le trafic de supervision, sans aucune exposition des agents sur l'Internet public.
