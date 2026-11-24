# CloudWatchtower – Infrastructure Monitoring Dashboard

A Python Flask application that displays live CPU, memory, disk, host and uptime information for the machine running the application. It stores metric snapshots in SQLite and exposes simple health and metrics APIs.

## Features

- Flask dashboard with responsive UI
- CPU, RAM and disk usage using `psutil`
- Hostname, operating system and system uptime
- `/health` application health endpoint
- `/api/metrics` JSON metrics endpoint
- `/api/history` recent SQLite metric snapshots
- Gunicorn-ready for deployment

## Requirements

- Python 3.10+
- pip
- Git (optional, for version control)

## Run locally (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open http://127.0.0.1:5000

If PowerShell blocks virtual-environment activation, use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Run locally (Linux / macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## API endpoints

| Endpoint | Purpose |
|---|---|
| `/` | Web dashboard |
| `/health` | Application health response |
| `/api/metrics` | Current host metrics (JSON) |
| `/api/history` | Latest 20 stored snapshots |

## Production note

The metrics endpoints are intended for development and a controlled demo. Before exposing this application publicly, put it behind an appropriate access-control layer and restrict access to operational endpoints. Do not expose host metrics or administrative endpoints to the public internet without authentication and network controls. Use a strong `SECRET_KEY`, disable Flask debug mode, and run behind Nginx with Gunicorn.

## Planned project phases

1. Local Flask application
2. GitHub repository and documentation
3. AWS VPC and EC2 deployment
4. CloudWatch alarms and SNS notifications
5. Python Lambda recovery automation
6. Prometheus and Grafana integration
7. Failure simulation, verification and screenshots

## Cost and security

AWS resources may incur charges. Create a billing budget/alerts before provisioning resources, use the smallest suitable instance, and stop or delete resources when finished. Never commit AWS credentials, private keys, `.env` files, or database files to GitHub.
