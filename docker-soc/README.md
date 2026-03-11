# docker-soc

This folder contains the Docker-based Wazuh SOC stack for Task 2.

## 1. Requirements
- Docker
- Docker Compose (v2 or higher)
- AWS credentials (for Task 4 automation script only)

## 2. Start stack
```bash
cd docker-soc
docker compose up -d
```

## 3. Verify services
- Wazuh Indexer (OpenSearch fork): http://localhost:9200
- Wazuh Manager: (agent registration / API) 1514, 1515, 55000
- Wazuh Dashboard: https://localhost:443

## 4. Persistent volumes
- `wazuh_indexer_data`
- `wazuh_manager_data`

## 5. Automation integration
- `automation/isolate_vm.py` → mounted into manager at `/var/ossec/integrations/custom`
- custom rule file (see `docker-soc/rules/wazuh_local_rules.xml`)

## 6. Optional: generate self-signed certificates
If you need internal TLS for Wazuh Dashboard:
```bash
cd docker-soc
chmod +x generate-certs.sh
./generate-certs.sh
```

