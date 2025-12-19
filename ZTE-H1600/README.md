# ZTE H1600 Router Metrics Monitoring

This project monitors your ZTE H1600 router metrics using Prometheus and Grafana.

## Features

- **Automated metrics collection** from ZTE H1600 router
- **Prometheus** for metrics storage
- **Grafana** dashboard for visualization
- Monitors DSL connection metrics including:
  - Upload/Download speeds (actual and attainable)
  - Noise margin
  - Line attenuation
  - Output power
  - CRC and FEC errors
  - Interleave delay and depth
  - Impulse Noise Protection (INP)

## Prerequisites

- Docker and Docker Compose
- Access to your ZTE H1600 router

## Setup

1. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your router credentials and Grafana admin credentials:
   ```
   ROUTER_URL=http://192.168.1.1
   ROUTER_USERNAME=admin
   ROUTER_PASSWORD=your_password_here
   
   # Grafana credentials
   GRAFANA_ADMIN_USER=admin
   GRAFANA_ADMIN_PASSWORD=admin
   ```

2. **Start the services**:
   ```bash
   docker compose up -d
   ```

## Data Persistence

This setup uses Docker volumes to persist data across container restarts:

- **Prometheus data**: Stored in `prometheus-data` volume - retains all metrics history
- **Grafana data**: Stored in `grafana-data` volume - retains dashboards, users, and settings

Even if you restart or recreate containers, your metrics history and Grafana configuration will be preserved.

## Accessing the Services

- **Grafana Dashboard**: http://localhost:3000
  - Credentials: Use the username and password you configured in `.env` (default: `admin` / `admin`)
  - The "Router Metrics Dashboard" is automatically provisioned
  
- **Prometheus**: http://localhost:9090
  - Query and explore raw metrics
  
- **Metrics Exporter**: http://localhost:8000
  - View raw Prometheus-formatted metrics

## Dashboard Panels

The Grafana dashboard includes the following panels:

1. **Download Speed Gauge** - Current download rate
2. **Upload Speed Gauge** - Current upload rate  
3. **Actual Rates Over Time** - Time series graph of upload/download speeds
4. **Attainable Rates** - Maximum achievable speeds based on line quality
5. **Noise Margin** - SNR margin (higher is better, >6dB is good)
6. **Line Attenuation** - Signal loss over the line (lower is better)
7. **Output Power** - Transmission power levels
8. **CRC Errors** - Cyclic redundancy check errors (should be low)
9. **FEC Errors** - Forward error correction errors
10. **Interleave Delay** - Latency added for error correction
11. **INP** - Impulse noise protection level

## Configuration

### Scraping Interval

Metrics are collected every 60 seconds by default. To change this, modify the `periodic_scrape(60)` parameter in `helium_script.py`.

### Dashboard Refresh

The dashboard auto-refreshes every 10 seconds. You can change this in the Grafana UI or by editing `grafana/dashboards/router-metrics.json`.

## Troubleshooting

### Container keeps restarting

Check the logs:
```bash
docker compose logs router_metrics
```

Common issues:
- Incorrect router URL, username, or password in `.env`
- Router not accessible from Docker container
- Login page structure changed (element selectors may need updating)

### Dashboard not showing data

1. Check if Prometheus is scraping metrics:
   - Visit http://localhost:9090/targets
   - The `router_metrics` target should be "UP"

2. Verify metrics are being exposed:
   - Visit http://localhost:8000
   - You should see Prometheus-formatted metrics

3. Check Grafana data source:
   - Go to Grafana → Configuration → Data Sources
   - Prometheus should be configured and working

## Project Structure

```
.
├── docker-compose.yaml          # Docker services configuration
├── Dockerfile                   # Router metrics container image
├── helium_script.py            # Main scraping script
├── prometheus.yml              # Prometheus configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (git-ignored)
├── .env.example               # Environment template
└── grafana/
    ├── dashboards/
    │   └── router-metrics.json # Dashboard definition
    └── provisioning/
        ├── dashboards/
        │   └── dashboard.yml   # Dashboard provisioning config
        └── datasources/
            └── datasource.yml  # Prometheus datasource config
```

## Stopping the Services

```bash
docker compose down
```

To also remove volumes:
```bash
docker compose down -v
```

## License

This project is open source and available under the MIT License.
