# tools/slack_tool.py
import os
import requests

def notify_slack(message):
    print(message)
    try:
        webhook = os.getenv("SLACK_WEBHOOK")
        if not webhook:
            return "SLACK_WEBHOOK is not set."

        payload = {"text": message}
        response = requests.post(webhook, json=payload)

        if response.status_code == 200:
            return "Slack notified successfully."
        else:
            return f"Slack error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Exception sending Slack notification: {e}"
