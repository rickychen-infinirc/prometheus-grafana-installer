#!/bin/bash


sudo apt update
sudo apt upgrade -y


sudo apt install -y wget

# 創建 Prometheus 用戶
sudo useradd --no-create-home --shell /bin/false prometheus

# 創建必要目錄
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

# 下載 Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

# 解壓文件
tar -xvzf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

# 移動文件到適當位置
sudo mv prometheus /usr/local/bin/
sudo mv promtool /usr/local/bin/
sudo mv prometheus.yml /etc/prometheus/
sudo mv consoles /etc/prometheus/
sudo mv console_libraries /etc/prometheus/

# 設置目錄權限
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus

# 創建 systemd 服務文件
cat << EOF | sudo tee /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \\
    --config.file=/etc/prometheus/prometheus.yml \\
    --storage.tsdb.path=/var/lib/prometheus/ \\
    --web.console.templates=/etc/prometheus/consoles \\
    --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
EOF

# 重新加載 systemd 並啟動 Prometheus
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus

echo "Prometheus 安裝完成!"