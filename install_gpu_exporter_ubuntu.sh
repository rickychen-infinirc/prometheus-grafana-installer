#!/bin/bash

# 更新系統
sudo apt update

# 安裝依賴
sudo apt install -y wget

# 下載 NVIDIA GPU Exporter
cd /tmp
wget https://github.com/utkuozdemir/nvidia_gpu_exporter/releases/download/v1.2.1/nvidia-gpu-exporter_1.2.1_linux_amd64.deb

# 安裝
sudo dpkg -i nvidia-gpu-exporter_1.2.1_linux_amd64.deb

# 創建專用用戶
sudo useradd -m -s /bin/false nvidia_gpu_exporter

# 創建 systemd 服務文件
cat << EOF | sudo tee /etc/systemd/system/nvidia_gpu_exporter.service
[Unit]
Description=NVIDIA GPU Exporter
After=network-online.target

[Service]
Type=simple
User=nvidia_gpu_exporter
Group=nvidia_gpu_exporter
ExecStart=/usr/bin/nvidia_gpu_exporter
SyslogIdentifier=nvidia_gpu_exporter
Restart=always
RestartSec=1

[Install]
WantedBy=multi-user.target
EOF

# 重新加載 systemd 並啟動服務
sudo systemctl daemon-reload
sudo systemctl start nvidia_gpu_exporter
sudo systemctl enable nvidia_gpu_exporter

echo "NVIDIA GPU Exporter 安裝完成!"