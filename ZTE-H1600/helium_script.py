import os
import time
import re
import threading
from helium import *
from http.server import BaseHTTPRequestHandler, HTTPServer
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
        print(f"Navigating to {URL}")
        go_to(URL)
        
        # Wait for page to load
        time.sleep(3)
        
        print("Attempting to log in...")
        try:
            # Try different possible field names/selectors
            try:
                write(USERNAME, into='Username')
            except:
                try:
                    write(USERNAME, into='username')
                except:
                    # Try finding input by name attribute
                    username_field = driver.find_element(By.NAME, 'Username')
                    username_field.send_keys(USERNAME)
            
            try:
                write(PASSWORD, into='Password')
            except:
                try:
                    write(PASSWORD, into='password')
                except:
                    # Try finding input by name attribute
                    password_field = driver.find_element(By.NAME, 'Password')
                    password_field.send_keys(PASSWORD)
            
            click('Login')
            print("Login submitted")
        except Exception as e:
            print(f"Login failed: {e}")
            print("Page source for debugging:")
            print(driver.page_source[:1000])  # Print first 1000 chars
            raise

        time.sleep(3)  # Increased wait time
        
        try:
            click('Internet')
            print("Clicked Internet tab")
        except Exception as e:
            print(f"Failed to click Internet: {e}")
            raise

        time.sleep(2)  # Wait for metrics to load

        # Extract rates and store them in the metrics dictionary
        print("Extracting metrics...")
        
        def to_bps(val):
            return val * 1000 if val is not None else 0

        up, down = extract_rates('crate\\:0')
        metrics['actual_upload'], metrics['actual_download'] = to_bps(up), to_bps(down)
        
        up, down = extract_rates('cmaxrate\\:0')
        metrics['attainable_upload'], metrics['attainable_download'] = to_bps(up), to_bps(down)
        
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
        print("Metrics extracted successfully")

    except Exception as e:
        print(f"Error during scraping: {e}")
        # Don't crash completely, just log the error
    finally:
        try:
            driver.quit()
        except:
            pass

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
"""
        self.wfile.write(response.encode())

# Function to periodically scrape metrics
def periodic_scrape(interval):
    # Wait a bit before first scrape to ensure everything is ready
    print("Waiting 10 seconds before first scrape...")
    time.sleep(10)
    
    while True:
        try:
            scrape_metrics()
            print("Done scraping !!!")
        except Exception as e:
            print(f"Scrape cycle failed: {e}")
        time.sleep(interval)

# Start the HTTP server in a separate thread
def run_server():
    httpd = HTTPServer(('0.0.0.0', 8000), MetricsHandler)
    httpd.serve_forever()

# Start the threads for the HTTP server and metric scraping
if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()  # Run HTTP server
    periodic_scrape(60)  # Scrape metrics every 60 seconds
