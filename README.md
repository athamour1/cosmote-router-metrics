# 🌐 COSMOTE Router Metrics - Production Setup

A comprehensive monitoring solution for tracking metrics from multiple COSMOTE routers simultaneously using **Prometheus** and **Grafana**.

## 📊 Supported Routers

- **ZTE H1600** - Metrics exposed on port 8001
- **Sercom Speedport Plus** - Metrics exposed on port 8002

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Access to both routers on your network

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cosmote-router-metrics
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your router credentials and URLs:
   ```env
   # ZTE H1600 Configuration
   ZTE_ROUTER_URL=http://192.168.1.1
   ZTE_ROUTER_USERNAME=admin
   ZTE_ROUTER_PASSWORD=your_password
   
   # Speedport Plus Configuration
   SPEEDPORT_ROUTER_URL=http://192.168.2.1
   SPEEDPORT_STATS_URL=http://192.168.2.1/data/Status.json
   SPEEDPORT_ROUTER_USERNAME=admin
   SPEEDPORT_ROUTER_PASSWORD=your_password
   ```

3. **Start the monitoring stack:**
   ```bash
   docker-compose up -d
   ```

4. **Access the dashboards:**
   - **Grafana Dashboard**: http://localhost:3000
     - Default credentials: `admin` / `admin` (change in `.env`)
   - **Prometheus**: http://localhost:9090


## 📈 Available Dashboards

Three Grafana dashboards are automatically provisioned:

### 1. **COSMOTE Routers - Combined Dashboard** (Default)
Displays metrics from both routers side by side for easy comparison:
- Speed gauges for both routers (ZTE & Speedport)
- Historical speed trends
- SNR and attenuation metrics
- CRC error monitoring

### 2. **ZTE H1600 - Individual Dashboard**
Dedicated dashboard for ZTE H1600 router with:
- Download/upload speed monitoring
- Noise margin (SNR) tracking
- Line attenuation measurements
- CRC error statistics
- Power level indicators

### 3. **Speedport Plus - Individual Dashboard**
Dedicated dashboard for Sercom Speedport Plus router with:
- DSL speed monitoring (downstream/upstream)
- SNR quality metrics
- Attenuation tracking
- CRC and FEC error monitoring
- System uptime display

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Docker Network                     │
│                                                      │
│  ┌──────────────┐      ┌──────────────┐            │
│  │ ZTE H1600    │      │ Speedport    │            │
│  │ Exporter     │      │ Exporter     │            │
│  │ :8001        │      │ :8002        │            │
│  └──────┬───────┘      └──────┬───────┘            │
│         │                     │                     │
│         └──────────┬──────────┘                     │
│                    │                                │
│              ┌─────▼──────┐                         │
│              │ Prometheus │                         │
│              │   :9090    │                         │
│              └─────┬──────┘                         │
│                    │                                │
│              ┌─────▼──────┐                         │
│              │  Grafana   │                         │
│              │   :3000    │                         │
│              └────────────┘                         │
└─────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
cosmote-router-metrics/
├── docker-compose.yaml           # Production compose file
├── prometheus.yml                # Prometheus configuration
├── .env.example                  # Environment variables template
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yaml   # Prometheus datasource
│   │   └── dashboards/
│   │       └── default.yaml      # Dashboard provisioning
│   └── dashboards/
│       ├── combined-routers.json # Combined dashboard (both routers)
│       ├── zte-individual.json   # ZTE H1600 individual dashboard
│       └── speedport-individual.json # Speedport Plus individual dashboard
├── ZTE-H1600/                    # ZTE router exporter
└── Sercom-Speedport-Plus/        # Speedport router exporter
```

## 🛠️ Management Commands

### Start all services
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f zte_metrics
docker-compose logs -f speedport_metrics
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove all data
```bash
docker-compose down -v
```

### Restart a specific service
```bash
docker-compose restart zte_metrics
docker-compose restart speedport_metrics
```

### Check service health
```bash
docker-compose ps
```

## 🔍 Troubleshooting

### No data in Grafana

1. **Check metrics endpoints are accessible:**
   ```bash
   # Check from inside the containers (ports are not exposed to host)
   docker exec zte_h1600_metrics curl -s http://localhost:8000/metrics | head
   docker exec speedport_plus_metrics curl -s http://localhost:8000/metrics | head
   ```

2. **Verify Prometheus is scraping:**
   - Visit http://localhost:9090/targets
   - Both targets should show as "UP"

3. **Check container logs:**
   ```bash
   docker-compose logs zte_metrics
   docker-compose logs speedport_metrics
   ```

### Connection errors

- Verify router URLs are correct in `.env`
- Ensure routers are accessible from Docker network
- Check credentials are correct

### Dashboard not loading

1. **Restart Grafana:**
   ```bash
   docker-compose restart grafana
   ```

2. **Check Grafana logs:**
   ```bash
   docker-compose logs grafana
   ```

## 📊 Metrics Collected

### ZTE H1600
- `actual_download` - Download speed (bps)
- `actual_upload` - Upload speed (bps)
- `noise_margin_download` - SNR downstream (dB)
- `noise_margin_upload` - SNR upstream (dB)
- `attenuation_download` - Line attenuation downstream (dB)
- `attenuation_upload` - Line attenuation upstream (dB)
- `crc_download` - CRC errors download
- `crc_upload` - CRC errors upload

### Sercom Speedport Plus
- `dsl_downstream_bps` - Download speed (bps)
- `dsl_upstream_bps` - Upload speed (bps)
- `snr_downstream_db` - SNR downstream (dB)
- `snr_upstream_db` - SNR upstream (dB)
- `attenuation_downstream_db` - Line attenuation downstream (dB)
- `attenuation_upstream_db` - Line attenuation upstream (dB)
- `crc_errors` - Total CRC errors

## 🔐 Security Considerations

- Change default Grafana credentials in `.env`
- Keep `.env` file secure and never commit it to version control
- Consider using Docker secrets for production deployments
- Restrict network access to Grafana/Prometheus if exposed publicly

## 📝 License

See individual router project directories for specific licenses.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.