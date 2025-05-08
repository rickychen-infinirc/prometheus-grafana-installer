#!/bin/bash

# 更新系統
sudo apt update

# 下載 Node Exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz

# 解壓文件
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz

# 創建 Node Exporter 用戶
sudo useradd --no-create-home --shell /bin/false node_exporter

# 移動二進制文件
sudo cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter

# 創建 systemd 服務文件
cat << EOF | sudo tee /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# 重新加載 systemd 並啟動 Node Exporter
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter

echo "Node Exporter 安裝完成!"