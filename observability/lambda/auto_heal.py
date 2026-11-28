"""
Auto-heal Lambda: reboots an EC2 instance when a CloudWatch alarm
(delivered through SNS) goes into ALARM state.

Safety checks:
  - only acts on state change to ALARM
  - only for alarms whose name contains ALARM_NAME_FILTER (default: status-check)
  - only reboots instances tagged AutoHeal=true
  - only reboots instances that are in the 'running' state
"""
import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")
TAG_KEY = os.environ.get("TAG_KEY", "AutoHeal")
TAG_VALUE = os.environ.get("TAG_VALUE", "true")
# Only alarms whose name contains this text may trigger a reboot
ALARM_NAME_FILTER = os.environ.get("ALARM_NAME_FILTER", "status-check")


def _instance_id(alarm):
    for dim in alarm.get("Trigger", {}).get("Dimensions", []):
        name = dim.get("name") or dim.get("Name")
        if name == "InstanceId":
            return dim.get("value") or dim.get("Value")
    return None


def lambda_handler(event, context):
    results = []
    for record in event.get("Records", []):
        alarm = json.loads(record["Sns"]["Message"])
        name = alarm.get("AlarmName")

        if alarm.get("NewStateValue") != "ALARM":
            logger.info("Alarm %s not in ALARM state, skipping", name)
            continue
        if ALARM_NAME_FILTER not in (name or ""):
            logger.info("Alarm %s is alert-only, not rebooting", name)
            continue

        instance_id = _instance_id(alarm)
        if not instance_id:
            logger.warning("Alarm %s has no InstanceId dimension", name)
            continue

        reservations = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"]
        instance = reservations[0]["Instances"][0]
        tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
        state = instance["State"]["Name"]

        if tags.get(TAG_KEY) != TAG_VALUE:
            logger.info("%s missing tag %s=%s, skipping", instance_id, TAG_KEY, TAG_VALUE)
            continue
        if state != "running":
            logger.info("%s is %s, skipping", instance_id, state)
            continue

        logger.info("Rebooting %s because of alarm %s", instance_id, name)
        ec2.reboot_instances(InstanceIds=[instance_id])
        results.append(instance_id)

    return {"statusCode": 200, "rebooted": results}
