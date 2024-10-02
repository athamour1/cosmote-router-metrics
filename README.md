# Cosmote Router Metrics Exporter

This project creates a custom metrics exporter for your router, designed to scrape performance metrics and expose them for Prometheus. It uses Selenium with the Helium library to extract data from the router's web interface, serving it via a simple HTTP server. Additionally, Grafana is included to visualize the metrics.

## Table of Contents

- [Cosmote Router Metrics Exporter](#cosmote-router-metrics-exporter)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Running the Application](#running-the-application)
  - [Prometheus Configuration](#prometheus-configuration)
  - [License](#license)

## Features
- ZTE-H1600
  - Scrapes various metrics from your router, including:
    - Actual upload/download rates
    - Attainable upload/download rates
    - Noise margins
    - Line attenuation
    - Output power
    - Interleave depth and delay
    - INP, CRC, and FEC errors
  - Exposes metrics in a format suitable for Prometheus scraping
  - Provides a Grafana dashboard for visualization
  - Runs as a Docker container

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/athamour1/cosmote-router-metrics.git
   cd router-metrics-exporter
   ```

2. Create a `prometheus.yml` configuration file in the project root directory with the following content:

   ```yaml
   global:
     scrape_interval: 1m

   scrape_configs:
     - job_name: 'router_metrics'
       static_configs:
         - targets: ['router_metrics:8000']
   ```

3. Update the environment variables in `docker-compose.yml` to match your router's credentials and URL:
   ```yaml
   environment:
     - ROUTER_URL=http://192.168.1.1  # Adjust this URL as needed
     - ROUTER_USERNAME=admin
     - ROUTER_PASSWORD=<pass>
   ```

## Running the Application

1. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. Access Grafana by navigating to `http://localhost:3000` in your browser. The default login is:
   - **Username:** admin
   - **Password:** admin

3. Add Prometheus as a data source in Grafana using the following URL:
   ```
   http://prometheus:9090
   ```

4. Import the Grafana dashboard JSON file provided in this repository to visualize your router metrics.

## Prometheus Configuration

Make sure Prometheus is set to scrape metrics from the exporter. The provided `prometheus.yml` configuration is set to scrape every minute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.