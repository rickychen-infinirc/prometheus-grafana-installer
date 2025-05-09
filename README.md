# prometheus-grafana-installer
```
sudo chmod +x install_prometheus_ubuntu.sh
sudo ./install_prometheus_ubuntu.sh
```
```
sudo chmod +x install_node_exporter_ubuntu.sh
sudo ./install_node_exporter_ubuntu.sh
```
```
sudo chmod +x install_gpu_exporter_ubuntu.sh
sudo ./install_gpu_exporter_ubuntu.sh
```

```
sudo nano /etc/prometheus/prometheus.yml
```

```
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # 監控 Prometheus 本身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # 監控本機系統資源
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # 如果有 GPU，添加 GPU 監控
  - job_name: 'nvidia_gpus'
    static_configs:
      - targets: ['localhost:9835']
```
```
sudo systemctl restart prometheus
```

http://your-server-ip:9090


dashboard 

4. 在 Grafana 中配置數據源

訪問 Grafana：http://your-server-ip:3000
登入（默認用戶名/密碼：admin/admin）
到 "Configuration" > "Data Sources"
點擊 "Add data source"
選擇 "Prometheus"
設置 URL：http://localhost:9090 (如果 Grafana 與 Prometheus 在同一台機器)
點擊 "Save & Test" - 應該顯示綠色的成功消息

5. 導入儀表板
導入 Node Exporter Full 儀表板

點擊左側的 "+" 圖標
選擇 "Import"
輸入 ID：1860
點擊 "Load"
在 "Prometheus" 數據源下拉菜單中選擇您的 Prometheus 數據源
點擊 "Import"

導入 NVIDIA GPU 儀表板

再次點擊左側的 "+" 圖標
選擇 "Import"
輸入 ID：14574
點擊 "Load"
選擇您的 Prometheus 數據源
點擊 "Import"
