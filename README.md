# prometheus-grafana-installer

sudo chmod +x install_prometheus_ubuntu.sh
sudo ./install_prometheus_ubuntu.sh

sudo chmod +x install_node_exporter_ubuntu.sh
sudo ./install_node_exporter_ubuntu.sh

sudo chmod +x install_gpu_exporter_ubuntu.sh
sudo ./install_gpu_exporter_ubuntu.sh


sudo nano /etc/prometheus/prometheus.yml

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

sudo systemctl restart prometheus


http://your-server-ip:9090