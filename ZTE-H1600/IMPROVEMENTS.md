# ZTE-H1600 Implementation - Proposed Improvements

## Overview

This document outlines potential improvements and issues found in the ZTE-H1600 router metrics monitoring implementation.

---

## ✅ Current Strengths

- **Well-Structured Architecture**: Clean separation between scraping logic, metrics server, and monitoring stack
- **Comprehensive Metrics Collection**: Captures all important DSL metrics (speeds, noise margin, attenuation, errors, etc.)
- **Docker Compose Orchestration**: Proper networking and data persistence with volumes
- **Automatic Provisioning**: Grafana dashboards and data sources auto-configured
- **Good Error Handling**: Multiple fallback attempts for login and proper cleanup
- **Excellent Documentation**: Comprehensive README with troubleshooting guide

---

## ⚠️ Issues & Recommendations

### 1. Metric Units Conversion (Priority: HIGH)

**Issue**: The scraped values may have unit mismatches with what Grafana expects.

**Details**:
- Router likely returns speeds in **kbps**, but dashboard expects **bps** (bits per second)
- DSL metrics like noise margin, attenuation, and power are typically in **0.1 dB** or **0.1 dBm** units
- Current implementation extracts raw numbers without unit conversion

**Location**: `helium_script.py` lines 102-111

**Recommendation**:
```python
def extract_rates(span_id, unit_multiplier=1):
    rates_text = find_all(S(f'#{span_id}'))
    if rates_text:
        rates_text = [rate.web_element.text for rate in rates_text]
        rates_text = rates_text[0]
        match = re.search(r'(\d+)/(\d+)', rates_text)
        if match:
            rate_1, rate_2 = match.groups()
            # Apply unit conversion (e.g., kbps to bps: multiply by 1000)
            return int(rate_1) * unit_multiplier, int(rate_2) * unit_multiplier
    return None, None

# Usage:
metrics['actual_upload'], metrics['actual_download'] = extract_rates('crate\\:0', 1000)  # kbps to bps
```

**Alternative**: Document expected units clearly in README and verify dashboard queries match actual units.

---

### 2. String Metrics Not Exported (Priority: MEDIUM)

**Issue**: Lines 112-116 extract string values but never expose them in Prometheus metrics.

**Missing Metrics**:
- `uptime` - Connection uptime
- `link_status` - Link state (e.g., "UP", "DOWN")
- `modulation_type` - DSL modulation (e.g., "VDSL2")
- `profile` - DSL profile (e.g., "17a")
- `link_encap` - Link encapsulation type

**Location**: `helium_script.py` lines 112-116, 135-195

**Recommendation**:

**Option A**: Convert uptime to seconds and export as gauge:
```python
def parse_uptime(uptime_str):
    """Convert uptime string like '2d 5h 30m' to seconds"""
    # Implementation depends on actual format
    pass

# In metrics output:
uptime_seconds = parse_uptime(metrics.get('uptime', '0'))
response += f"""# HELP router_uptime_seconds Router connection uptime in seconds
# TYPE router_uptime_seconds gauge
router_uptime_seconds {uptime_seconds}
"""
```

**Option B**: Use Prometheus info metric pattern:
```python
# HELP router_info Router connection information
# TYPE router_info gauge
router_info{{status="{metrics.get('link_status', 'UNKNOWN')}",modulation="{metrics.get('modulation_type', 'UNKNOWN')}",profile="{metrics.get('profile', 'UNKNOWN')}",encap="{metrics.get('link_encap', 'UNKNOWN')}"}} 1
```

---

### 3. Hardcoded Element IDs (Priority: MEDIUM)

**Issue**: Element IDs like `crate\\:0`, `cmaxrate\\:0` are hardcoded. Router firmware updates could break the scraper.

**Location**: `helium_script.py` lines 102-116

**Recommendation**:

**Option A**: Add configuration mapping:
```python
# At top of file, after environment variables
ELEMENT_IDS = {
    'actual_rate': os.getenv('ELEMENT_ID_ACTUAL_RATE', 'crate\\:0'),
    'max_rate': os.getenv('ELEMENT_ID_MAX_RATE', 'cmaxrate\\:0'),
    'margin': os.getenv('ELEMENT_ID_MARGIN', 'cmargin\\:0'),
    # ... etc
}

# Usage:
metrics['actual_upload'], metrics['actual_download'] = extract_rates(ELEMENT_IDS['actual_rate'])
```

**Option B**: Add better documentation and logging:
```python
# Extract rates and store them in the metrics dictionary
# Note: Element IDs are specific to ZTE H1600 firmware version X.X.X
# If scraping fails after firmware update, inspect page source and update IDs
print("Extracting metrics...")
print("Looking for element: crate\\:0 (Actual Rate)")
metrics['actual_upload'], metrics['actual_download'] = extract_rates('crate\\:0')
if metrics['actual_upload'] is None:
    print("WARNING: Failed to extract actual rates - element not found")
```

---

### 4. Fixed Scrape Interval (Priority: MEDIUM)

**Issue**: Scrape interval is hardcoded to 60 seconds and may not match Prometheus scrape interval.

**Location**: `helium_script.py` line 220, `prometheus.yml` line 2

**Recommendation**:
```python
# In helium_script.py
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '60'))

if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    periodic_scrape(SCRAPE_INTERVAL)
```

```yaml
# In docker-compose.yaml, add to router_metrics service:
environment:
  - ROUTER_URL=${ROUTER_URL}
  - ROUTER_USERNAME=${ROUTER_USERNAME}
  - ROUTER_PASSWORD=${ROUTER_PASSWORD}
  - SCRAPE_INTERVAL=${SCRAPE_INTERVAL:-60}
```

```bash
# In .env.example:
SCRAPE_INTERVAL=60
```

---

### 5. No Health Check Endpoint (Priority: LOW)

**Issue**: Only `/` serves metrics. No dedicated health check endpoint for Docker or monitoring.

**Location**: `helium_script.py` lines 129-196

**Recommendation**:
```python
class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/metrics' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            # Existing metrics output
            response = f"""# HELP actual_upload Actual upload rate
# TYPE actual_upload gauge
...
```

Add to `docker-compose.yaml`:
```yaml
router_metrics:
  build: .
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

---

### 6. Browser Session Reuse (Priority: LOW)

**Issue**: Each scrape creates a new Chrome instance, which is slow (~3-5 seconds startup) and resource-intensive.

**Location**: `helium_script.py` lines 39-126

**Recommendation**:

**Option A**: Keep browser alive between scrapes:
```python
# Global browser instance
driver = None

def ensure_browser():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        driver = start_chrome(URL, headless=True, options=chrome_options)
    return driver

def scrape_metrics():
    try:
        browser = ensure_browser()
        # Rest of scraping logic
    except Exception as e:
        # On error, reset browser
        global driver
        if driver:
            try:
                driver.quit()
            except:
                pass
        driver = None
        raise
```

**Trade-offs**:
- ✅ Faster scraping (no browser startup delay)
- ✅ Lower resource usage
- ❌ More complex error recovery
- ❌ Browser memory leaks over time

**Option B**: Keep login session (cookies):
```python
# Save session after first login, reuse cookies for subsequent scrapes
```

---

### 7. Logging Improvements (Priority: LOW)

**Issue**: Uses `print()` statements instead of proper logging framework.

**Location**: Throughout `helium_script.py`

**Recommendation**:
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usage:
logger.info(f"Navigating to {URL}")
logger.warning("Failed to extract actual rates - element not found")
logger.error(f"Login failed: {e}", exc_info=True)
```

Allow log level configuration:
```python
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
```

---

### 8. Metric Staleness Tracking (Priority: LOW)

**Issue**: If scraping fails, metrics remain at previous values. Prometheus can't distinguish between "no new data" and "actual zero value".

**Location**: `helium_script.py` lines 15-16, 199-210

**Recommendation**:
```python
import time

# Add timestamp and success tracking
last_scrape_time = 0
last_scrape_success = 0

def scrape_metrics():
    global last_scrape_time, last_scrape_success
    last_scrape_time = time.time()
    try:
        # ... existing scrape logic ...
        last_scrape_success = 1
    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        last_scrape_success = 0
        raise

# In metrics output:
response += f"""# HELP scrape_success Whether the last scrape was successful
# TYPE scrape_success gauge
scrape_success {last_scrape_success}
# HELP scrape_timestamp_seconds Unix timestamp of last scrape attempt
# TYPE scrape_timestamp_seconds gauge
scrape_timestamp_seconds {last_scrape_time}
"""
```

This allows Grafana to show "stale data" warnings.

---

## 📊 Dashboard Improvements

### Add Missing Panels

Since string metrics aren't currently exported, consider adding once implemented:

1. **Connection Status Panel**: Show link status (UP/DOWN) as stat panel
2. **Uptime Panel**: Display connection uptime as a stat or time series
3. **Connection Info Panel**: Show modulation type, profile, encapsulation as stat panel

### Add Staleness Indicators

```promql
# In Grafana, add alert or color coding:
(time() - scrape_timestamp_seconds) > 120  # Alert if data is >2 minutes old
```

---

## 🎯 Implementation Priority

### High Priority
1. ✅ Verify and fix metric units (kbps vs bps)
2. ✅ Document expected units in README

### Medium Priority
3. ✅ Export string metrics (uptime, status, modulation)
4. ✅ Make scrape interval configurable
5. ✅ Add comments/docs for element IDs

### Low Priority (Nice to Have)
6. ✅ Add health check endpoint
7. ✅ Implement proper logging
8. ✅ Add metric staleness tracking
9. ✅ Consider browser session reuse

---

## 📝 Testing Checklist

After implementing improvements:

- [ ] Verify metrics units match Grafana expectations (bps, dB, dBm)
- [ ] Confirm string metrics appear in Prometheus (`/metrics` endpoint)
- [ ] Test health check endpoint (`curl http://localhost:8000/health`)
- [ ] Verify configurable scrape interval works
- [ ] Check Grafana dashboards render all panels correctly
- [ ] Test error recovery (disconnect router, wrong credentials)
- [ ] Monitor resource usage (CPU, memory) over 24 hours
- [ ] Verify data persistence after `docker compose restart`

---

## 🔗 Related Files

- **Main Script**: [`helium_script.py`](file:///home/thanos98/Develop/cosmote-router-metrics/ZTE-H1600/helium_script.py)
- **Docker Compose**: [`docker-compose.yaml`](file:///home/thanos98/Develop/cosmote-router-metrics/ZTE-H1600/docker-compose.yaml)
- **Prometheus Config**: [`prometheus.yml`](file:///home/thanos98/Develop/cosmote-router-metrics/ZTE-H1600/prometheus.yml)
- **Dashboard**: [`grafana/dashboards/router-metrics.json`](file:///home/thanos98/Develop/cosmote-router-metrics/ZTE-H1600/grafana/dashboards/router-metrics.json)
- **README**: [`README.md`](file:///home/thanos98/Develop/cosmote-router-metrics/ZTE-H1600/README.md)

---

**Last Updated**: 2025-12-19
