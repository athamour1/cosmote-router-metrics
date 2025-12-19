# Sercom Speedport Plus Router Metrics Monitoring

This project monitors your Sercom Speedport Plus router DSL metrics using Prometheus and Grafana.

## Features

- **Automated metrics collection** from Sercom Speedport Plus router
- **Prometheus** for metrics storage
- **Grafana** dashboard for visualization
- Monitors DSL/VDSL connection metrics including:
  - Upload/Download speeds (in bps)
  - Signal-to-Noise Ratio (SNR) - Downstream and Upstream
  - Line Attenuation - Downstream and Upstream
  - CRC and FEC error counts
  - System uptime
  - Connection information (transmission mode, firmware version)

## Prerequisites

- Docker and Docker Compose
- Access to your Sercom Speedport Plus router (http://192.168.1.1)

## Setup

1. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your router credentials and Grafana admin credentials:
   ```
   ROUTER_URL=http://192.168.1.1
   STATS_URL=http://192.168.1.1/html/content/config/system_info.html
   ROUTER_USERNAME=admin
   ROUTER_PASSWORD=your_password_here
   
   # Scrape interval in seconds
   SCRAPE_INTERVAL=60
   
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

> **Note**: This setup uses different ports than the ZTE-H1600 implementation to avoid conflicts if running both simultaneously.

- **Grafana Dashboard**: http://localhost:3001
  - Credentials: Use the username and password you configured in `.env` (default: `admin` / `admin`)
  - The "Sercom Speedport Plus - DSL Metrics" dashboard is automatically provisioned
  
- **Prometheus**: http://localhost:9091
  - Query and explore raw metrics
  
- **Metrics Exporter**: http://localhost:8001
  - View raw Prometheus-formatted metrics

## Dashboard Panels

The Grafana dashboard includes the following panels:

1. **Download Speed Gauge** - Current download rate in bps
2. **Upload Speed Gauge** - Current upload rate in bps
3. **DSL Speeds Over Time** - Time series graph of upload/download speeds
4. **SNR Downstream** - Signal-to-noise ratio for downstream (higher is better, >10dB is good)
5. **SNR Upstream** - Signal-to-noise ratio for upstream
6. **Signal-to-Noise Ratio Over Time** - Time series graph of SNR
7. **Attenuation Downstream** - Line attenuation for downstream (lower is better)
8. **Attenuation Upstream** - Line attenuation for upstream
9. **Line Attenuation Over Time** - Time series graph of attenuation
10. **CRC Errors** - Cyclic redundancy check errors (should be low/zero)
11. **FEC Errors** - Forward error correction errors
12. **System Uptime** - Router connection uptime

## Configuration

### Scraping Interval

Metrics are collected every 60 seconds by default. To change this, modify the `SCRAPE_INTERVAL` value in `.env`:

```bash
SCRAPE_INTERVAL=120  # Scrape every 2 minutes
```

### Dashboard Refresh

The dashboard auto-refreshes every 10 seconds. You can change this in the Grafana UI or by editing `grafana/dashboards/speedport-metrics.json`.

## How It Works

### Web Scraping Approach

Unlike traditional SNMP-based monitoring, this implementation uses web scraping:

1. **Chrome/Selenium**: Launches a headless Chrome browser
2. **Navigation**: Goes to the system info page (http://192.168.1.1/html/content/config/system_info.html)
3. **Authentication**: Handles login if required
4. **Extraction**: Parses the HTML table to extract metrics
5. **Conversion**: Converts units (kbps → bps, uptime string → seconds)
6. **Exposure**: Serves metrics in Prometheus format on port 8000

### Metrics Format

The scraper converts router values to standard Prometheus metrics:

- **Speeds**: kbit/s → bps (multiply by 1000)
- **Uptime**: "0 days, 8 hours, 12 minutes, 45 seconds" → total seconds
- **SNR/Attenuation**: Already in dB, passed through directly
- **Info metrics**: Transmission mode and firmware as labels

## Troubleshooting

### Container keeps restarting

Check the logs:
```bash
docker compose logs speedport_metrics
```

Common issues:
- Incorrect router URL, username, or password in `.env`
- Router not accessible from Docker container
- Login page structure changed (element selectors may need updating)
- Stats page HTML structure changed

### Dashboard not showing data

1. Check if Prometheus is scraping metrics:
   - Visit http://localhost:9091/targets
   - The `speedport_metrics` target should be "UP"

2. Verify metrics are being exposed:
   - Visit http://localhost:8001/metrics
   - You should see Prometheus-formatted metrics like:
     ```
     dsl_downstream_bps 54999000
     dsl_upstream_bps 5495000
     snr_downstream_db 9.9
     ...
     ```

3. Check Grafana data source:
   - Go to Grafana → Configuration → Data Sources
   - Prometheus should be configured and working

4. Check scrape success metric:
   - In Prometheus, query: `scrape_success`
   - Should return `1` if scraping is working
   - If `0`, check the scraper logs for errors

### Login required but credentials not working

If the router requires login and your credentials aren't working:

1. Verify credentials by logging in manually via browser
2. Check if there's a CAPTCHA or additional security
3. Review the scraper logs to see the exact error
4. You may need to modify the login logic in `speedport_script.py`

### Metrics are all zero

This usually means the HTML structure has changed:

1. Visit http://192.168.1.1/html/content/config/system_info.html in your browser
2. Right-click → "Inspect Element" to view the HTML structure
3. Compare with the extraction logic in `speedport_script.py` (lines 90-180)
4. Update the `extract_text_from_row()` function if table structure changed

## Project Structure

```
.
├── docker-compose.yaml          # Docker services configuration
├── Dockerfile                   # Router metrics container image
├── speedport_script.py          # Main scraping script
├── prometheus.yml              # Prometheus configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (git-ignored)
├── .env.example               # Environment template
└── grafana/
    ├── dashboards/
    │   └── speedport-metrics.json  # Dashboard definition
    └── provisioning/
        ├── dashboards/
        │   └── dashboard.yml   # Dashboard provisioning config
        └── datasources/
            └── datasource.yml  # Prometheus datasource config
```

## Port Configuration

This implementation uses the following ports (different from ZTE-H1600 to avoid conflicts):

| Service | Host Port | Container Port | URL |
|---------|-----------|----------------|-----|
| Metrics Exporter | 8001 | 8000 | http://localhost:8001 |
| Prometheus | 9091 | 9090 | http://localhost:9091 |
| Grafana | 3001 | 3000 | http://localhost:3001 |

## Stopping the Services

```bash
docker compose down
```

To also remove volumes:
```bash
docker compose down -v
```

## Running Both Routers Simultaneously

You can run both the ZTE-H1600 and Sercom Speedport Plus monitoring stacks at the same time since they use different ports:

```bash
# In ZTE-H1600 directory
docker compose up -d

# In Sercom-Speedport-Plus directory
docker compose up -d
```

Access them via:
- ZTE-H1600 Grafana: http://localhost:3000
- Speedport Grafana: http://localhost:3001

## Health Check

The metrics exporter includes a health check endpoint at `/health`:

```bash
curl http://localhost:8001/health
# Should return: OK
```

Docker will automatically restart the container if health checks fail.

## Advanced Configuration

### Custom Stats URL

If your router serves the stats on a different page:

```bash
# In .env
STATS_URL=http://192.168.1.1/your/custom/path/system_info.html
```

### Logging Level

To enable more verbose logging, modify `speedport_script.py` and add at the top:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- The router credentials in `.env` are sensitive - keep them secure
- The `.env` file is git-ignored by default
- Consider using Docker secrets in production environments
- Health check endpoint (`/health`) is unauthenticated for container monitoring

## Comparison with ZTE-H1600 Implementation

| Feature | ZTE-H1600 | Sercom Speedport Plus |
|---------|-----------|----------------------|
| **Metrics Page** | Requires clicking "Internet" tab | Direct URL to stats page |
| **Login** | Always required | May or may not be required |
| **Data Format** | Spans with IDs | HTML table rows |
| **Speeds** | Separate up/down values | Displayed together |
| **Additional Metrics** | More detailed (INP, delay, depth, power) | Simpler set |
| **Complexity** | Higher | Lower |

## Known Limitations

- Web scraping is fragile - firmware updates may break the scraper
- No real-time metrics - limited by scrape interval
- Higher resource usage than SNMP (runs full Chrome browser)
- No historical error count deltas (CRC/FEC are totals, not rates)

## Future Improvements

See `IMPROVEMENTS.md` in the parent ZTE-H1600 directory for general enhancement ideas that also apply here:

- Browser session reuse for faster scraping
- Better error recovery and retry logic
- Alerting rules for connection issues
- Multi-router support in single dashboard

## License

This project is open source and available under the MIT License.
