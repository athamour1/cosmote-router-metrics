import os
import time
import re
import threading
from helium import *
from http.server import BaseHTTPRequestHandler, HTTPServer
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Load environment variables
URL = os.getenv('ROUTER_URL', 'http://192.168.1.1')
STATS_URL = os.getenv('STATS_URL', 'http://192.168.1.1/html/login/status.html')

# Initialize a dictionary to hold metrics
metrics = {}

def parse_uptime(uptime_str):
    """Convert uptime string like '0 days, 8 hours, 12 minutes, 45 seconds' to total seconds"""
    try:
        days = hours = minutes = seconds = 0
        
        # Extract days
        days_match = re.search(r'(\d+)\s*days?', uptime_str)
        if days_match:
            days = int(days_match.group(1))
        
        # Extract hours
        hours_match = re.search(r'(\d+)\s*hours?', uptime_str)
        if hours_match:
            hours = int(hours_match.group(1))
        
        # Extract minutes
        minutes_match = re.search(r'(\d+)\s*minutes?', uptime_str)
        if minutes_match:
            minutes = int(minutes_match.group(1))
        
        # Extract seconds
        seconds_match = re.search(r'(\d+)\s*seconds?', uptime_str)
        if seconds_match:
            seconds = int(seconds_match.group(1))
        
        total_seconds = (days * 86400) + (hours * 3600) + (minutes * 60) + seconds
        return total_seconds
    except Exception as e:
        print(f"Error parsing uptime '{uptime_str}': {e}")
        return 0

def extract_speed_value(text):
    """Extract speed value in kbit/s and convert to bps"""
    try:
        # Match patterns like "54999 kbit/s" or "5495 kBit/s"
        match = re.search(r'(\d+)\s*kbit/s', text, re.IGNORECASE)
        if match:
            kbps = int(match.group(1))
            return kbps * 1000  # Convert to bps
    except Exception as e:
        print(f"Error parsing speed '{text}': {e}")
    return None

def extract_dual_value(text):
    """Extract dual values like '9.9 / 26.8 dB' and return as (down, up)"""
    try:
        # Match patterns like "9.9 / 26.8" or "38.0 / 18.0"
        match = re.search(r'([\d.]+)\s*/\s*([\d.]+)', text)
        if match:
            down = float(match.group(1))
            up = float(match.group(2))
            return down, up
    except Exception as e:
        print(f"Error parsing dual value '{text}': {e}")
    return None, None

def extract_by_id(driver, element_id):
    """Extract text from a span element by its ID"""
    try:
        element = driver.find_element(By.ID, element_id)
        return element.text.strip()
    except Exception as e:
        print(f"Error extracting element with ID '{element_id}': {e}")
        return None

# Function to scrape metrics from the router
def scrape_metrics():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    # Start the browser
    driver = start_chrome(STATS_URL, headless=True, options=chrome_options)

    try:
        print(f"Navigating to public status page: {STATS_URL}")
        go_to(STATS_URL)
        
        # Wait for page to load
        time.sleep(3)
        
        print("Extracting metrics from status page using span IDs...")
        
        # Extract DSL speeds (values are in kBit/s)
        downstream_val = extract_by_id(driver, 'var_dsl_downstream')
        if downstream_val:
            try:
                kbps = int(downstream_val)
                metrics['dsl_downstream_bps'] = kbps * 1000  # Convert to bps
                print(f"DSL Downstream: {kbps} kbit/s -> {metrics['dsl_downstream_bps']} bps")
            except ValueError:
                print(f"Could not parse downstream value: {downstream_val}")
        
        upstream_val = extract_by_id(driver, 'var_dsl_upstream')
        if upstream_val:
            try:
                kbps = int(upstream_val)
                metrics['dsl_upstream_bps'] = kbps * 1000  # Convert to bps
                print(f"DSL Upstream: {kbps} kbit/s -> {metrics['dsl_upstream_bps']} bps")
            except ValueError:
                print(f"Could not parse upstream value: {upstream_val}")
        
        # Extract uptime (ID is 'var_uptime' on public status page)
        uptime_text = extract_by_id(driver, 'var_uptime')
        if uptime_text:
            metrics['uptime_seconds'] = parse_uptime(uptime_text)
            print(f"Uptime: {uptime_text} -> {metrics['uptime_seconds']} seconds")
        
        # Extract transmission mode
        transmission_mode = extract_by_id(driver, 'var_dsl_transmission_mode')
        if transmission_mode:
            metrics['transmission_mode'] = transmission_mode
            print(f"Transmission mode: {transmission_mode}")
        
        # Extract error counts
        crc_errors = extract_by_id(driver, 'var_dsl_crc_errors')
        if crc_errors:
            try:
                metrics['crc_errors'] = int(crc_errors)
                print(f"CRC errors: {crc_errors}")
            except ValueError:
                metrics['crc_errors'] = 0
        
        fec_errors = extract_by_id(driver, 'var_dsl_fec_errors')
        if fec_errors:
            try:
                metrics['fec_errors'] = int(fec_errors)
                print(f"FEC errors: {fec_errors}")
            except ValueError:
                metrics['fec_errors'] = 0
        
        # Extract SNR (format: "9.8 / 26.8")
        snr_text = extract_by_id(driver, 'var_dsl_snr')
        if snr_text:
            snr_down, snr_up = extract_dual_value(snr_text)
            if snr_down is not None:
                metrics['snr_downstream_db'] = snr_down
                metrics['snr_upstream_db'] = snr_up
                print(f"SNR: {snr_text} dB -> Down: {snr_down} dB, Up: {snr_up} dB")
        
        # Extract Attenuation (format: "38.0 / 18.0")
        attenuation_text = extract_by_id(driver, 'var_dsl_atnu')
        if attenuation_text:
            att_down, att_up = extract_dual_value(attenuation_text)
            if att_down is not None:
                metrics['attenuation_downstream_db'] = att_down
                metrics['attenuation_upstream_db'] = att_up
                print(f"Attenuation: {attenuation_text} dB -> Down: {att_down} dB, Up: {att_up} dB")
        
        # Extract firmware version
        firmware_version = extract_by_id(driver, 'var_firmware_version')
        if firmware_version:
            metrics['firmware_version'] = firmware_version
            print(f"Firmware: {firmware_version}")
        
        print("Metrics extracted successfully!")

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

# Tracking for staleness
last_scrape_time = 0
last_scrape_success = 0

# Function to run the HTTP server
class MetricsHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        if self.path == '/health' or self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/metrics' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; version=0.0.4')
            self.end_headers()
            
            # Output metrics in Prometheus format
            response = f"""# HELP dsl_downstream_bps DSL downstream speed in bits per second
# TYPE dsl_downstream_bps gauge
dsl_downstream_bps {metrics.get('dsl_downstream_bps', 0)}
# HELP dsl_upstream_bps DSL upstream speed in bits per second
# TYPE dsl_upstream_bps gauge
dsl_upstream_bps {metrics.get('dsl_upstream_bps', 0)}
# HELP uptime_seconds System uptime in seconds
# TYPE uptime_seconds counter
uptime_seconds {metrics.get('uptime_seconds', 0)}
# HELP crc_errors Total CRC errors
# TYPE crc_errors counter
crc_errors {metrics.get('crc_errors', 0)}
# HELP fec_errors Total FEC errors
# TYPE fec_errors counter
fec_errors {metrics.get('fec_errors', 0)}
# HELP snr_downstream_db Signal-to-noise ratio downstream in dB
# TYPE snr_downstream_db gauge
snr_downstream_db {metrics.get('snr_downstream_db', 0)}
# HELP snr_upstream_db Signal-to-noise ratio upstream in dB
# TYPE snr_upstream_db gauge
snr_upstream_db {metrics.get('snr_upstream_db', 0)}
# HELP attenuation_downstream_db Line attenuation downstream in dB
# TYPE attenuation_downstream_db gauge
attenuation_downstream_db {metrics.get('attenuation_downstream_db', 0)}
# HELP attenuation_upstream_db Line attenuation upstream in dB
# TYPE attenuation_upstream_db gauge
attenuation_upstream_db {metrics.get('attenuation_upstream_db', 0)}
# HELP router_info Router information
# TYPE router_info gauge
router_info{{transmission_mode="{metrics.get('transmission_mode', 'unknown')}",firmware="{metrics.get('firmware_version', 'unknown')}"}} 1
# HELP scrape_success Whether the last scrape was successful (1 = success, 0 = failure)
# TYPE scrape_success gauge
scrape_success {last_scrape_success}
# HELP scrape_timestamp_seconds Unix timestamp of last scrape attempt
# TYPE scrape_timestamp_seconds gauge
scrape_timestamp_seconds {last_scrape_time}
"""
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

# Function to periodically scrape metrics
def periodic_scrape(interval):
    global last_scrape_time, last_scrape_success
    
    # Wait a bit before first scrape to ensure everything is ready
    print("Waiting 10 seconds before first scrape...")
    time.sleep(10)
    
    while True:
        last_scrape_time = time.time()
        try:
            scrape_metrics()
            last_scrape_success = 1
            print("Scrape completed successfully!")
        except Exception as e:
            last_scrape_success = 0
            print(f"Scrape cycle failed: {e}")
        
        print(f"Sleeping for {interval} seconds until next scrape...")
        time.sleep(interval)

# Start the HTTP server in a separate thread
def run_server():
    httpd = HTTPServer(('0.0.0.0', 8000), MetricsHandler)
    print("HTTP server started on port 8000")
    httpd.serve_forever()

# Start the threads for the HTTP server and metric scraping
if __name__ == '__main__':
    SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '60'))
    print(f"Starting Sercom Speedport Plus metrics exporter...")
    print(f"Stats URL: {STATS_URL}")
    print(f"Scrape interval: {SCRAPE_INTERVAL} seconds")
    
    threading.Thread(target=run_server, daemon=True).start()  # Run HTTP server
    periodic_scrape(SCRAPE_INTERVAL)  # Scrape metrics
