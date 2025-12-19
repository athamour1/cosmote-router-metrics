# Cosmote Router Metrics Monitoring

Web scraping-based monitoring solution for DSL/VDSL routers using Selenium, Prometheus, and Grafana. Automatically extracts connection metrics from router web interfaces and visualizes them in real-time dashboards.

## Supported Routers

This project includes implementations for two router models:

### 1. [ZTE-H1600](ZTE-H1600/) 
Full-featured DSL monitoring with comprehensive metrics collection.

**Metrics Collected:**
- Actual & Attainable upload/download rates
- Noise margin (SNR)
- Line attenuation
- Output power
- Interleave depth and delay
- Impulse Noise Protection (INP)
- CRC and FEC errors
- Uptime, link status, modulation type, profile

**Access:**
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Metrics: http://localhost:8000

📖 **[View ZTE-H1600 Documentation →](ZTE-H1600/README.md)**

---

### 2. [Sercom Speedport Plus](Sercom-Speedport-Plus/)
Streamlined VDSL monitoring for Sercom routers.

**Metrics Collected:**
- DSL upstream/downstream speeds
- Signal-to-Noise Ratio (SNR) - Up/Down
- Line Attenuation - Up/Down
- CRC and FEC errors
- System uptime
- Connection info (transmission mode, firmware)

**Access:**
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9091
- Metrics: http://localhost:8001

📖 **[View Sercom Speedport Plus Documentation →](Sercom-Speedport-Plus/README.md)**

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Access to your router's web interface

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/athamour1/cosmote-router-metrics.git
   cd cosmote-router-metrics
   ```

2. **Choose your router directory:**
   ```bash
   # For ZTE-H1600
   cd ZTE-H1600
   
   # OR for Sercom Speedport Plus
   cd Sercom-Speedport-Plus
   ```

3. **Configure credentials:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your router credentials
   ```

4. **Start the monitoring stack:**
   ```bash
   docker compose up -d
   ```

5. **Access Grafana:**
   - ZTE-H1600: http://localhost:3000
   - Sercom Speedport Plus: http://localhost:3001
   - Default credentials: `admin` / `admin`

## Features

✅ **Automated Metrics Collection** - Headless Chrome scrapes router web UI every 60 seconds  
✅ **Prometheus Storage** - Time-series database with full history retention  
✅ **Grafana Dashboards** - Pre-built, auto-provisioned visualization dashboards  
✅ **Docker Deployment** - Single-command setup with docker-compose  
✅ **Data Persistence** - Metrics and configs survive container restarts  
✅ **Health Monitoring** - Built-in health checks and staleness detection  
✅ **Dual Router Support** - Run both implementations simultaneously (different ports)

## Architecture

```
┌─────────────────┐
│  Router Web UI  │ ← Selenium scrapes metrics every 60s
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Python Scraper  │ ← Extracts & converts metrics
│   (Helium)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Server    │ ← Exposes /metrics endpoint
│   (port 8000)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Prometheus    │ ← Scrapes & stores metrics
│   (port 9090)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Grafana      │ ← Visualizes dashboards
│   (port 3000)   │
└─────────────────┘
```

## Project Structure

```
cosmote-router-metrics/
├── README.md                    # This file
├── ZTE-H1600/                   # ZTE router implementation
│   ├── helium_script.py         # Metrics scraper
│   ├── docker-compose.yaml      # Docker orchestration
│   ├── Dockerfile               # Container image
│   ├── prometheus.yml           # Prometheus config
│   ├── grafana/                 # Dashboard & provisioning
│   ├── README.md                # Detailed docs
│   └── IMPROVEMENTS.md          # Enhancement proposals
└── Sercom-Speedport-Plus/       # Sercom router implementation
    ├── speedport_script.py      # Metrics scraper
    ├── docker-compose.yaml      # Docker orchestration
    ├── Dockerfile               # Container image
    ├── prometheus.yml           # Prometheus config
    ├── grafana/                 # Dashboard & provisioning
    └── README.md                # Detailed docs
```

## Router Comparison

| Feature | ZTE-H1600 | Sercom Speedport Plus |
|---------|-----------|----------------------|
| **Metrics Count** | 20+ metrics | 10 core metrics |
| **Complexity** | High (tab navigation) | Medium (direct page) |
| **Login Required** | Always | Sometimes |
| **Data Parsing** | Element IDs | HTML tables |
| **Ports** | 8000, 9090, 3000 | 8001, 9091, 3001 |
| **Use Case** | Detailed diagnostics | Simple monitoring |

## Running Both Routers Simultaneously

The implementations use different ports, so you can monitor both routers at once:

```bash
# Terminal 1: ZTE-H1600
cd ZTE-H1600
docker compose up -d

# Terminal 2: Sercom Speedport Plus  
cd Sercom-Speedport-Plus
docker compose up -d
```

Access dashboards:
- ZTE-H1600: http://localhost:3000
- Speedport: http://localhost:3001

## Troubleshooting

### Common Issues

**Container keeps restarting:**
```bash
docker compose logs -f <service_name>
```
Check for authentication errors, incorrect URLs, or network issues.

**Dashboard shows "No Data":**
1. Visit Prometheus targets: http://localhost:9090/targets (or 9091)
2. Verify metrics endpoint: http://localhost:8000/metrics (or 8001)
3. Check `scrape_success` metric (should be `1`)

**Metrics are all zero:**
- Router firmware updated (HTML structure changed)
- Check browser logs for element extraction errors
- May need to update CSS selectors in scraper script

### Getting Help

1. Check the router-specific README in its directory
2. Review `IMPROVEMENTS.md` for known issues and enhancements
3. Open an issue on GitHub with logs and configuration

## Technical Details

### Technologies Used

- **Selenium + Helium**: Headless browser automation
- **Chrome WebDriver**: Browser engine
- **Python 3**: Scraping logic
- **Prometheus**: Metrics storage
- **Grafana**: Visualization
- **Docker**: Containerization

### Why Web Scraping?

Many consumer routers don't support SNMP or have limited/broken implementations. Web scraping provides:
- ✅ Works with any router that has a web UI
- ✅ Access to all visible metrics
- ✅ No firmware modification required
- ❌ More fragile (breaks on firmware updates)
- ❌ Higher resource usage than SNMP

## Contributing

Contributions are welcome! If you add support for a new router model:

1. Create a new directory: `Router-Model-Name/`
2. Follow the existing structure (script + docker-compose + grafana)
3. Add comprehensive README with setup instructions
4. Update this main README with router comparison
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Helium](https://github.com/mherrmann/helium) for simplified Selenium interactions
- Dashboards inspired by [Grafana Community](https://grafana.com/grafana/dashboards/)
- Docker images: [selenium/standalone-chrome](https://hub.docker.com/r/selenium/standalone-chrome/), [prom/prometheus](https://hub.docker.com/r/prom/prometheus/), [grafana/grafana](https://hub.docker.com/r/grafana/grafana/)

---

📊 **Happy Monitoring!** For detailed setup and troubleshooting, see the README in each router's directory.