import os
import time
import re
import threading
from helium import *
from http.server import BaseHTTPRequestHandler, HTTPServer
from selenium.webdriver.chrome.options import Options

# Load environment variables
URL = os.getenv('ROUTER_URL')
USERNAME = os.getenv('ROUTER_USERNAME')
PASSWORD = os.getenv('ROUTER_PASSWORD')

# Initialize a dictionary to hold metrics
metrics = {}

# Function to extract upload and download rates from span elements
def extract_rates(span_id):
    rates_text = find_all(S(f'#{span_id}'))
    if rates_text:
        rates_text = [rate.web_element.text for rate in rates_text]
        rates_text = rates_text[0]
        match = re.search(r'(\d+)/(\d+)', rates_text)
        if match:
            rate_1, rate_2 = match.groups()
            return int(rate_1), int(rate_2)
    return None, None

def extract_single_value(span_id):
    value = find_all(S(f'#{span_id}'))
    if value:
        value = [rate.web_element.text for rate in value]
        value = value[0]
        return value
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
    driver = start_chrome(URL, headless=True, options=chrome_options)
    # driver = start_firefox()

    try:
        go_to(URL)
        write(USERNAME, into='Username')
        write(PASSWORD, into='Password')
        click('Login')

        time.sleep(1)
        click('Internet')

        time.sleep(1)

        # Extract rates and store them in the metrics dictionary
        metrics['actual_upload'], metrics['actual_download'] = extract_rates('crate\\:0')
        metrics['attainable_upload'], metrics['attainable_download'] = extract_rates('cmaxrate\\:0')
        metrics['noise_margin_upload'], metrics['noise_margin_download'] = extract_rates('cmargin\\:0')
        metrics['attenuation_upload'], metrics['attenuation_download'] = extract_rates('cattenuation\\:0')
        metrics['power_upload'], metrics['power_download'] = extract_rates('cpower\\:0')
        metrics['depth_upload'], metrics['depth_download'] = extract_rates('cdepth\\:0')
        metrics['delay_upload'], metrics['delay_download'] = extract_rates('cdelay\\:0')
        metrics['inp_upload'], metrics['inp_download'] = extract_rates('cinp\\:0')
        metrics['crc_upload'], metrics['crc_download'] = extract_rates('ccrc\\:0')
        metrics['fec_upload'], metrics['fec_download'] = extract_rates('cfec\\:0')
        metrics['uptime'] = extract_single_value('cststart\\:0')
        metrics['link_status'] = extract_single_value('cStatus\\:0')
        metrics['modulation_type'] = extract_single_value('cModule_type\\:0')
        metrics['profile'] = extract_single_value('cprofile\\:0')
        metrics['link_encap'] = extract_single_value('clinkencap\\:0')

    finally:
        driver.quit()

# Function to run the HTTP server
class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # Output metrics in Prometheus format
        response = f"""# HELP actual_upload Actual upload rate
# TYPE actual_upload gauge
actual_upload {metrics.get('actual_upload', 0)}
# HELP actual_download Actual download rate
# TYPE actual_download gauge
actual_download {metrics.get('actual_download', 0)}
# HELP attainable_upload Attainable upload rate
# TYPE attainable_upload gauge
attainable_upload {metrics.get('attainable_upload', 0)}
# HELP attainable_download Attainable download rate
# TYPE attainable_download gauge
attainable_download {metrics.get('attainable_download', 0)}
# HELP noise_margin_upload Noise margin upload
# TYPE noise_margin_upload gauge
noise_margin_upload {metrics.get('noise_margin_upload', 0)}
# HELP noise_margin_download Noise margin download
# TYPE noise_margin_download gauge
noise_margin_download {metrics.get('noise_margin_download', 0)}
# HELP attenuation_upload Line attenuation upload
# TYPE attenuation_upload gauge
attenuation_upload {metrics.get('attenuation_upload', 0)}
# HELP attenuation_download Line attenuation download
# TYPE attenuation_download gauge
attenuation_download {metrics.get('attenuation_download', 0)}
# HELP power_upload Output power upload
# TYPE power_upload gauge
power_upload {metrics.get('power_upload', 0)}
# HELP power_download Output power download
# TYPE power_download gauge
power_download {metrics.get('power_download', 0)}
# HELP depth_upload Interleave depth upload
# TYPE depth_upload gauge
depth_upload {metrics.get('depth_upload', 0)}
# HELP depth_download Interleave depth download
# TYPE depth_download gauge
depth_download {metrics.get('depth_download', 0)}
# HELP delay_upload Interleave delay upload
# TYPE delay_upload gauge
delay_upload {metrics.get('delay_upload', 0)}
# HELP delay_download Interleave delay download
# TYPE delay_download gauge
delay_download {metrics.get('delay_download', 0)}
# HELP inp_upload INP upload
# TYPE inp_upload gauge
inp_upload {metrics.get('inp_upload', 0)}
# HELP inp_download INP download
# TYPE inp_download gauge
inp_download {metrics.get('inp_download', 0)}
# HELP crc_upload CRC errors upload
# TYPE crc_upload gauge
crc_upload {metrics.get('crc_upload', 0)}
# HELP crc_download CRC errors download
# TYPE crc_download gauge
crc_download {metrics.get('crc_download', 0)}
# HELP fec_upload FEC errors upload
# TYPE fec_upload gauge
fec_upload {metrics.get('fec_upload', 0)}
# HELP fec_download FEC errors download
# TYPE fec_download gauge
fec_download {metrics.get('fec_download', 0)}
# HELP uptime xDSL connection
# TYPE uptime gauge
uptime {metrics.get('uptime', 0)}
# HELP link status connection
# TYPE link_status gauge
link_status {metrics.get('link_status', 0)}
# HELP modulation type xDSL connection
# TYPE modulation_type gauge
modulation_type {metrics.get('modulation_type', 0)}
# HELP profile xDSL connection
# TYPE profile gauge
profile {metrics.get('profile', 0)}
# HELP link_encap xDSL connection
# TYPE link_encap gauge
link_encap {metrics.get('link_encap', 0)}
"""
        self.wfile.write(response.encode())

# Function to periodically scrape metrics
def periodic_scrape(interval):
    while True:
        scrape_metrics()
        print("Done scraping !!!")
        time.sleep(interval)

# Start the HTTP server in a separate thread
def run_server():
    httpd = HTTPServer(('0.0.0.0', 8000), MetricsHandler)
    httpd.serve_forever()

# Start the threads for the HTTP server and metric scraping
if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()  # Run HTTP server
    periodic_scrape(60)  # Scrape metrics every 60 seconds
