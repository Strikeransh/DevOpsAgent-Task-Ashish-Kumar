# 🔹 1. IMPORTS (top of file)
from prometheus_api_client import PrometheusConnect
import time
import requests
import subprocess  # ✅ Add this for log reading
import os
import re
print(os.getenv("GROQ_API_KEY"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
# 🔹 2. CONFIG
prom = PrometheusConnect(url="http://localhost:9090", disable_ssl=True)
THRESHOLD = 50.0
QUERY = """
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[2m]))
"""

# 🔹 3. CPU USAGE FUNCTION
def get_cpu_usage():
    try:
        result = prom.custom_query(query=QUERY)
        #result = prom.get_current_metric_value(metric_name='node_cpu_seconds_total')
        if result:
            usage = float(result[0]['value'][1]) * 100
            return round(usage, 2)
    except Exception as e:
        print(f"❌ Error fetching CPU usage: {e}")
    return None

# 🔹 4. LOG FETCH FUNCTION (paste here)
def fetch_syslog(tail=20):
    try:
        output = subprocess.check_output(["tail", f"-n{tail}", "/var/log/syslog"])
        return output.decode("utf-8")
    except Exception as e:
        return f"Error fetching logs: {e}"

# 🔹 5. OLLAMA ANALYSIS FUNCTION (paste after fetch_syslog)
def analyze_with_ollama(log_text, model="llama3"):
    prompt = f"""
Analyze these logs to identify the possible cause of high CPU usage.
Provide a clear reason if identifiable.

Logs:
{log_text}
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        if response.status_code == 200:
            return response.json().get("response", "[No response]")
        else:
            return f"Ollama API error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling Ollama: {e}"


def analyze_with_groq(log_text):
    prompt = f"""
Analyze these logs to identify the possible cause of high CPU usage.
Provide a clear reason if identifiable.

Logs:
{log_text}
"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",  # or "mixtral-8x7b-32768"
        "messages": [
            {"role": "user", "content": f"{prompt}"}
        ]
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()  # ✅ parse JSON response
#    print(result)
    return result['choices'][0]['message']['content']
#    return result


def extract_container_ids(ai_response):
    return re.findall(r'\b[a-f0-9]{64}\b', ai_response.lower())

#def extract_container_names(ai_response):
#    return re.findall(r'container\s+([a-zA-Z0-9_\-]+)', ai_response.lower())

def restart_containers(container_ids_or_names):
    for cid in container_ids_or_names:
        print(f"🔍 Checking container: {cid}")
        inspect = subprocess.run(["docker", "inspect", cid], capture_output=True)
        if inspect.returncode == 0:
            print(f"🔁 Restarting container: {cid}")
            subprocess.run(["docker", "restart", cid])
            return (f"Container '{cid}' is restarted.")
        else:
            return (f"Container '{cid}' not found or already removed.")

#def restart_matching_containers(possible_names):
    # Get all running/stopped containers and their names
#    output = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.ID}} {{.Names}}"])
#    containers = output.decode("utf-8").strip().split("\n")

#    restarted = []
#    for name in possible_names:
#        for line in containers:
#            cid, cname = line.split(maxsplit=1)
#            if name in cid or name in cname:
#                print(f"✅ Found match: {cname} (ID: {cid}) — restarting...")
#                subprocess.run(["docker", "restart", cid])
#                restarted.append(cname)
#                break
#    if not restarted:
#        print("⚠️ No matching containers were found for restart.")


def notify_slack(message):
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message})
    except Exception as e:
        print(f"❌ Slack error: {e}")



# 🔹 6. MAIN LOOP
if __name__ == "__main__":
    print("🧠 Starting CPU spike monitor...")
    while True:
        cpu = get_cpu_usage()
        if cpu is not None:
            print(f"📊 CPU usage: {cpu}%")
            if cpu > THRESHOLD:
                print(f"🚨 ALERT: CPU spike detected! ({cpu}%)")
                
                logs = fetch_syslog(tail=20)
                print("📄 Collected recent logs.")
                
#                analysis = analyze_with_ollama(logs)
                analysis = analyze_with_groq(logs)
                print("🧠 Ollama Analysis:\n")
                print(analysis)
                container_ids = extract_container_ids(analysis)
#                container_names = extract_container_names(analysis)

# Combine both lists and remove duplicates
#                to_restart = list(set(container_ids + container_names))
                to_restart = container_ids
                if to_restart:
                    print("🔧 AI recommended container restart for:", to_restart)
                    msg = restart_containers(to_restart)
                else:
                    msg = "No Container need to be restarted"
                print(msg)
                notify_slack(f"CPU Alert ({cpu}%)\n" + msg)
        else:
            print("⚠️ No data from Prometheus.")
        
        time.sleep(15)

