#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

cat > "$CERT_DIR/README.md" <<'EOF'
Copy these certs into the Wazuh dashboard or manager container as needed.
EOF

openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout "$CERT_DIR/wazuh.key" \
  -out "$CERT_DIR/wazuh.crt" \
  -subj "/C=US/ST=None/L=None/O=Wazuh/CN=localhost"

openssl pkcs12 -export -out "$CERT_DIR/wazuh.p12" \
  -inkey "$CERT_DIR/wazuh.key" -in "$CERT_DIR/wazuh.crt" -passout pass:

echo "Created self-signed certificates in $CERT_DIR"
