#!/usr/bin/env bash
# Run on the app server (Ubuntu). Installs node_exporter as a systemd service.
set -euo pipefail
VERSION="1.8.1"

cd /tmp
wget -q "https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/node_exporter-${VERSION}.linux-amd64.tar.gz"
tar xzf "node_exporter-${VERSION}.linux-amd64.tar.gz"
sudo cp "node_exporter-${VERSION}.linux-amd64/node_exporter" /usr/local/bin/
sudo useradd --no-create-home --shell /bin/false node_exporter 2>/dev/null || true

sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'UNIT'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
echo "node_exporter running on :9100"
