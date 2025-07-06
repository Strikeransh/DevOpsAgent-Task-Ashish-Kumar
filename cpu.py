#!/usr/bin/env python3
# cpu_spike_monitor.py

import time
import subprocess
import re
import requests
import os

# === CONFIGURATION ===
CPU_THRESHOLD = 50.0  # %
CHECK_INTERVAL = 10   # seconds
TAIL_LINES = 50       # log lines to collect
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key-here")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")

# === UTILITY FUNCTIONS ===
def get_cpu_usage():
    try:
        output = subprocess.check_output(["top", "-bn1"]).decode("utf-8")
        for line in output.split("\n"):
            if "Cpu(s):" in line:
                usage = float(line.split("%us")[0].split()[-1])
                return usage
    except Exception as e:
        print(f"❌ CPU check error: {e}")
    return 0.0

def fetch_syslog(tail=TAIL_LINES):
    try:
        output = subprocess.check_output(["tail", f"-n{tail}", "/var/log/syslog"])
        return output.decode("utf-8")
    except Exception as e:
        return f"Error fetching logs: {e}"

def analyze_with_groq(log_text):
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not set."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "user", "content": f"Analyze the following logs for CPU spike causes and remediation suggestions:\n{log_text}"}
        ]
    }
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"❌ Groq response error: {result.get('error', 'No choices in response')}"
    except Exception as e:
        return f"❌ Groq API error: {e}"

def extract_container_ids(text):
    return re.findall(r'\b[a-f0-9]{64}\b', text.lower())

def get_existing_containers():
    try:
        output = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.ID}} {{.Names}}"])
        return dict(line.split() for line in output.decode("utf-8").splitlines())
    except Exception:
        return {}

def restart_valid_containers(container_ids):
    existing = get_existing_containers()
    restarted = []
    for cid in container_ids:
        if cid in existing:
            print(f"✅ Restarting container: {existing[cid]} ({cid})")
            subprocess.run(["docker", "restart", cid])
            restarted.append(existing[cid])
    return restarted

def notify_slack(message):
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message})
    except Exception as e:
        print(f"❌ Slack error: {e}")

# === MAIN LOOP ===
print("🧠 Starting CPU spike monitor...")

while True:
    cpu = get_cpu_usage()
    print(f"📊 CPU usage: {cpu}%")

    if cpu > CPU_THRESHOLD:
        print(f"🚨 ALERT: CPU spike detected! ({cpu}%)")

        logs = fetch_syslog()
        print("📄 Collected recent logs.")

        analysis = analyze_with_groq(logs)
        print("🧠 AI Analysis:\n", analysis)

        targets = extract_container_ids(analysis)
        restarted = restart_valid_containers(targets)

        # Notify + log
        if restarted:
            msg = f"🔁 Restarted containers due to CPU spike: {restarted}"
        else:
            msg = "✅ AI found no valid containers to restart."

        print(msg)
        notify_slack(f"🚨 CPU Alert ({cpu}%)\n" + msg)

        with open("remediation.log", "a") as f:
            f.write(f"\n[{time.ctime()}] CPU Spike: {cpu}%\n")
            f.write("AI Analysis:\n" + analysis + "\n")
            f.write(msg + "\n")

    time.sleep(CHECK_INTERVAL)
