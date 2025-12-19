<div align="center">

# 📡 Cosmote Router Metrics Monitoring

### 🚀 Real-Time DSL/VDSL Performance Monitoring & Visualization

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

**Automated web scraping solution that transforms your router's web interface into beautiful, actionable metrics dashboards**

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Documentation](#-supported-routers)

</div>

---

## ✨ Features at a Glance

<table>
<tr>
<td width="50%">

### 🤖 **Automated Collection**
Headless Chrome scrapes your router every 60 seconds—no manual intervention needed.

### 📊 **Professional Dashboards**
Pre-configured Grafana dashboards auto-provision on startup with stunning visualizations.

### 🐳 **One-Command Deploy**
Single `docker compose up -d` deploys the entire monitoring stack.

</td>
<td width="50%">

### 💾 **Persistent Storage**
Full metric history with automatic retention and container-safe persistence.

### 🏥 **Health Monitoring**
Built-in staleness detection and health checks ensure reliable data flow.

### 🔄 **Dual Router Support**
Monitor multiple routers simultaneously on different ports.

</td>
</tr>
</table>

---

## 🎯 Supported Routers

### 📟 ZTE-H1600
> **Full-Featured DSL Monitoring** with 20+ comprehensive metrics

<details open>
<summary><b>📊 Collected Metrics</b></summary>

- 🚀 Actual & Attainable upload/download rates
- 📡 Noise margin (SNR)
- 📉 Line attenuation
- ⚡ Output power
- 🔄 Interleave depth and delay
- 🛡️ Impulse Noise Protection (INP)
- ⚠️ CRC and FEC errors
- ⏱️ Uptime, link status, modulation type, profile

</details>

**🌐 Access Points:**
- 📊 Grafana Dashboard: [`http://localhost:3000`](http://localhost:3000)
- 🔍 Prometheus: [`http://localhost:9090`](http://localhost:9090)
- 📈 Raw Metrics: [`http://localhost:8000`](http://localhost:8000)

📖 **[→ Full ZTE-H1600 Documentation](ZTE-H1600/README.md)**

---

### 🌐 Sercom Speedport Plus
> **Streamlined VDSL Monitoring** with 10 essential metrics

<details open>
<summary><b>📊 Collected Metrics</b></summary>

- 🚀 DSL upstream/downstream speeds
- 📡 Signal-to-Noise Ratio (SNR) - Up/Down
- 📉 Line Attenuation - Up/Down
- ⚠️ CRC and FEC errors
- ⏱️ System uptime
- 🔧 Connection info (transmission mode, firmware)

</details>

**🌐 Access Points:**
- 📊 Grafana Dashboard: [`http://localhost:3001`](http://localhost:3001)
- 🔍 Prometheus: [`http://localhost:9091`](http://localhost:9091)
- 📈 Raw Metrics: [`http://localhost:8001`](http://localhost:8001)

📖 **[→ Full Sercom Speedport Plus Documentation](Sercom-Speedport-Plus/README.md)**

---

## 🚀 Quick Start

### ⚡ Prerequisites

| Requirement | Description |
|------------|-------------|
| 🐳 **Docker** | Container runtime |
| 🔧 **Docker Compose** | Multi-container orchestration |
| 🌐 **Router Access** | Admin credentials for your router |

### 📦 Installation

```bash
# 1️⃣ Clone the repository
git clone https://github.com/athamour1/cosmote-router-metrics.git
cd cosmote-router-metrics

# 2️⃣ Choose your router implementation
cd ZTE-H1600              # For ZTE routers
# OR
cd Sercom-Speedport-Plus  # For Sercom routers

# 3️⃣ Configure your credentials
cp .env.example .env
nano .env  # Edit with your router IP, username, and password

# 4️⃣ Launch the stack 🚀
docker compose up -d

# 5️⃣ Access Grafana
# Visit http://localhost:3000 (or 3001 for Sercom)
# Default login: admin / admin
```

> [!TIP]
> On first run, Grafana will prompt you to change the default password. Choose a strong password for production use!

---

## 🏗️ Architecture

```
╔══════════════════════════════════════════════════════════════╗
║                    MONITORING PIPELINE                        ║
╚══════════════════════════════════════════════════════════════╝

    🌐 Router Web Interface
         │
         │ ◄─── 🤖 Selenium WebDriver (Chrome Headless)
         │      Scrapes every 60 seconds
         ▼
    📝 Python Scraper
       (Helium Framework)
         │
         │ ◄─── Extracts & normalizes metrics
         │
         ▼
    🌍 HTTP Metrics Server
       (Port 8000/8001)
         │
         │ ◄─── Exposes Prometheus /metrics endpoint
         │
         ▼
    📊 Prometheus TSDB
       (Port 9090/9091)
         │
         │ ◄─── Scrapes, stores & queries metrics
         │
         ▼
    📈 Grafana Dashboards
       (Port 3000/3001)
         │
         └─── 👁️ Beautiful real-time visualizations
```

---

## 📂 Project Structure

```
cosmote-router-metrics/
│
├── 📄 README.md                       # You are here!
│
├── 📁 ZTE-H1600/                      # ZTE Router Implementation
│   ├── 🐍 helium_script.py            # Selenium scraper script
│   ├── 🐳 docker-compose.yaml         # Container orchestration
│   ├── 📦 Dockerfile                  # Custom image build
│   ├── ⚙️  prometheus.yml             # Metrics scraping config
│   ├── 📁 grafana/                    # Dashboard definitions
│   │   └── provisioning/
│   ├── 📖 README.md                   # Detailed documentation
│   └── 💡 IMPROVEMENTS.md             # Future enhancements
│
└── 📁 Sercom-Speedport-Plus/          # Sercom Router Implementation
    ├── 🐍 speedport_script.py         # Selenium scraper script
    ├── 🐳 docker-compose.yaml         # Container orchestration
    ├── 📦 Dockerfile                  # Custom image build
    ├── ⚙️  prometheus.yml             # Metrics scraping config
    ├── 📁 grafana/                    # Dashboard definitions
    │   └── provisioning/
    └── 📖 README.md                   # Detailed documentation
```

---

## 🔍 Router Comparison

| Feature | 📟 ZTE-H1600 | 🌐 Sercom Speedport Plus |
|---------|:------------:|:------------------------:|
| **📊 Metrics** | 20+ detailed | 10 essential |
| **🧩 Complexity** | High (tab navigation) | Medium (single page) |
| **🔐 Login** | Always required | Conditional |
| **🎯 Parsing** | Element IDs | HTML tables |
| **🔌 Ports** | 8000, 9090, 3000 | 8001, 9091, 3001 |
| **💼 Best For** | Deep diagnostics | Quick monitoring |
| **⚙️ Setup Time** | ~5 minutes | ~3 minutes |

---

## 🎭 Running Both Routers

> [!IMPORTANT]
> Each implementation uses different ports, allowing simultaneous monitoring of multiple routers!

```bash
# 🖥️ Terminal 1: Start ZTE-H1600
cd ZTE-H1600
docker compose up -d

# 🖥️ Terminal 2: Start Sercom Speedport Plus
cd Sercom-Speedport-Plus
docker compose up -d
```

**Access Your Dashboards:**
- 📟 ZTE-H1600: [`http://localhost:3000`](http://localhost:3000)
- 🌐 Speedport Plus: [`http://localhost:3001`](http://localhost:3001)

---

## 🛠️ Troubleshooting

<details>
<summary><b>🔄 Container Keeps Restarting</b></summary>

```bash
# Check container logs
docker compose logs -f <service_name>
```

**Common causes:**
- ❌ Invalid router credentials in `.env`
- ❌ Wrong router IP address
- ❌ Router web interface not accessible
- ❌ Network connectivity issues

</details>

<details>
<summary><b>📊 Dashboard Shows "No Data"</b></summary>

**Verification steps:**

1. **Check Prometheus targets:**
   - Visit [`http://localhost:9090/targets`](http://localhost:9090/targets) (or 9091)
   - All targets should show `UP` status

2. **Verify metrics endpoint:**
   - Visit [`http://localhost:8000/metrics`](http://localhost:8000/metrics) (or 8001)
   - Should display raw Prometheus metrics

3. **Check scrape success:**
   ```promql
   scrape_success
   ```
   Should return `1` (not `0`)

> [!TIP]
> Wait 2-3 minutes after startup for initial data to appear!

</details>

<details>
<summary><b>⚠️ Metrics Are All Zero</b></summary>

**Possible causes:**
- 🔄 Router firmware was updated (HTML structure changed)
- 🏷️ Element selectors no longer match
- 🔐 Login flow has changed

**Fix:**
```bash
# Check scraper logs
docker compose logs -f router-metrics
```

Look for element extraction errors and update CSS selectors in the Python script accordingly.

</details>

<details>
<summary><b>🆘 Need More Help?</b></summary>

1. 📖 Review router-specific README in implementation directory
2. 💡 Check `IMPROVEMENTS.md` for known issues
3. 🐛 Open a GitHub issue with:
   - Container logs
   - `.env` configuration (redact credentials!)
   - Router model and firmware version

</details>

---

## 🔧 Technical Stack

<table>
<tr>
<td align="center" width="16.66%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python"/>
<br><b>Python 3</b>
<br><sub>Scraping Logic</sub>
</td>
<td align="center" width="16.66%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/selenium/selenium-original.svg" width="48" height="48" alt="Selenium"/>
<br><b>Selenium</b>
<br><sub>Browser Automation</sub>
</td>
<td align="center" width="16.66%">
<img src="https://www.vectorlogo.zone/logos/prometheusio/prometheusio-icon.svg" width="48" height="48" alt="Prometheus"/>
<br><b>Prometheus</b>
<br><sub>Metrics Storage</sub>
</td>
<td align="center" width="16.66%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/grafana/grafana-original.svg" width="48" height="48" alt="Grafana"/>
<br><b>Grafana</b>
<br><sub>Visualization</sub>
</td>
<td align="center" width="16.66%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="48" height="48" alt="Docker"/>
<br><b>Docker</b>
<br><sub>Containerization</sub>
</td>
<td align="center" width="16.66%">
<img src="https://www.vectorlogo.zone/logos/google_chrome/google_chrome-icon.svg" width="48" height="48" alt="Chrome"/>
<br><b>Chrome</b>
<br><sub>Headless WebDriver</sub>
</td>
</tr>
</table>

### 🤔 Why Web Scraping?

> [!NOTE]
> Most consumer routers lack proper SNMP support or have severely limited implementations.

**Web scraping advantages:**
- ✅ Works with **any** router having a web UI
- ✅ Access to **all** visible metrics (not limited by SNMP MIBs)
- ✅ **No firmware modifications** required
- ✅ Captures exactly what users see

**Trade-offs:**
- ⚠️ More fragile (breaks on firmware updates)
- ⚠️ Higher resource usage than SNMP
- ⚠️ Requires browser automation overhead

---

## 🤝 Contributing

We welcome contributions! 🎉

### Adding a New Router

1. **Create directory structure:**
   ```bash
   mkdir Router-Model-Name/
   cd Router-Model-Name/
   ```

2. **Implement required files:**
   - 🐍 Python scraper script
   - 🐳 `docker-compose.yaml`
   - 📦 `Dockerfile`
   - ⚙️ `prometheus.yml`
   - 📊 Grafana dashboards
   - 📖 Comprehensive `README.md`

3. **Update main README:**
   - Add to [Supported Routers](#-supported-routers)
   - Update [Router Comparison](#-router-comparison) table

4. **Submit PR:**
   - Describe router model and firmware version
   - Include screenshots of working dashboard
   - Document any special requirements

> [!TIP]
> Use existing implementations as templates for consistency!

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Built with awesome open-source tools:**

- 🐍 [Helium](https://github.com/mherrmann/helium) - Simplified Selenium wrapper
- 📊 [Grafana Community Dashboards](https://grafana.com/grafana/dashboards/) - Inspiration & design patterns
- 🐳 Docker Images:
  - [`selenium/standalone-chrome`](https://hub.docker.com/r/selenium/standalone-chrome/)
  - [`prom/prometheus`](https://hub.docker.com/r/prom/prometheus/)
  - [`grafana/grafana`](https://hub.docker.com/r/grafana/grafana/)

---

<div align="center">

### 📊 Happy Monitoring! 🚀

**For detailed setup and troubleshooting, see the README in each router's directory.**

[![Star this repo](https://img.shields.io/github/stars/athamour1/cosmote-router-metrics?style=social)](https://github.com/athamour1/cosmote-router-metrics)

</div>