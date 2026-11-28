#!/usr/bin/env bash
# Forces the alarm into ALARM state to test the full chain:
# CloudWatch alarm -> SNS -> email + Lambda -> EC2 reboot
# Usage: ./test_auto_heal.sh <alarm-name>
set -euo pipefail
aws cloudwatch set-alarm-state \
  --alarm-name "$1" \
  --state-value ALARM \
  --state-reason "Manual test of auto-heal pipeline"
echo "Alarm forced to ALARM at $(date -u +%T) UTC. Check email, Lambda logs and instance reboot time."
