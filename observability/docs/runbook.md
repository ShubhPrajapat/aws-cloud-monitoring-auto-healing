# Troubleshooting Runbook

## 1. EC2 instance status check failed
**Symptom:** `StatusCheckFailed` alarm fires, instance unreachable.
1. EC2 console > Status checks: system check (AWS side) or instance check (OS side)?
2. Instance check failed: reboot (auto-heal does this), then review `/var/log/syslog` and the console screenshot.
3. System check failed: stop and start the instance so it moves to new hardware.
4. Still failing: check EBS volume status and recent changes (fstab, kernel updates).

## 2. High CPU (alarm above 80%)
1. `top` or `htop`: find the process.
2. `ps aux --sort=-%cpu | head`.
3. Runaway process: investigate before killing. Legitimate load: consider a larger instance type or Auto Scaling.
4. Check the Grafana CPU panel for when it started and correlate with deployments.

## 3. Disk full
1. `df -h` then `sudo du -xh / --max-depth=1 | sort -h | tail`.
2. Check `/var/log` and Docker (`docker system df`).
3. Clean up, then set up log rotation. Consider enlarging the EBS volume.

## 4. Cannot SSH to instance
1. Security group: port 22 allowed from your current IP?
2. NACL: inbound 22 and outbound ephemeral ports 1024-65535 allowed?
3. Route table has a route to the Internet Gateway (public subnet)? Public IP assigned?
4. Key permissions `chmod 400 key.pem`, correct username (`ubuntu`)?
5. Instance status checks passing?

## 5. Prometheus target DOWN
1. `curl http://<private-ip>:9100/metrics` from the monitoring server.
2. `sudo systemctl status node_exporter` on the target.
3. Security group on the target allows 9100 from the monitoring server's SG.
