#!/bin/bash

set -e

echo "🚀 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installing Python 3, pip, and virtualenv..."
sudo apt install -y python3 python3-pip python3-venv curl unzip net-tools lsof

echo "📦 Installing required Python libraries..."
#pip3 install prometheus-api-client requests

echo "📦 Installing Node Exporter..."
cd ~
wget https://github.com/prometheus/node_exporter/releases/download/v1.9.1/node_exporter-1.9.1.linux-amd64.tar.gz
tar -xvzf node_exporter-1.9.1.linux-amd64.tar.gz
sudo cp node_exporter-1.9.1.linux-amd64/node_exporter /usr/local/bin/

echo "🧩 Creating systemd service for Node Exporter..."
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
ExecStart=/usr/local/bin/node_exporter --web.listen-address=0.0.0.0:9100
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter

echo "📈 Installing Prometheus..."
cd ~
wget https://github.com/prometheus/prometheus/releases/download/v3.5.0-rc.0/prometheus-3.5.0-rc.0.linux-amd64.tar.gz
tar -xvf prometheus-3.5.0-rc.0.darwin-amd64.tar.gz
mv prometheus-3.5.0-rc.0.darwin-amd64 prometheus
cd prometheus

echo "🛠️ Configuring Prometheus to scrape Node Exporter..."
cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF

echo "📊 Creating systemd service for Prometheus..."
sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
[Unit]
Description=Prometheus
After=network.target

[Service]
ExecStart=$HOME/prometheus/prometheus --config.file=$HOME/prometheus/prometheus.yml --web.listen-address=0.0.0.0:9090
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now prometheus


echo "✅ Setup complete!"
echo "🌐 Prometheus: http://<your-ec2-ip>:9090"
echo "📈 Node Exporter: http://<your-ec2-ip>:9100/metrics"

sudo apt install docker.io -y
docker run -d --name hello-alive alpine tail -f /dev/null

pip3 install requirements.txt


