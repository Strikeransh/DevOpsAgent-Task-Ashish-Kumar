# tools/log_tool.py
import subprocess
import os
import requests

def fetch_and_analyze_logs():
    try:
        output = subprocess.check_output(["tail", "-n", "50", "/var/log/syslog"]).decode("utf-8")
        print("📄 Fetched last 50 lines from syslog")

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return "GROQ_API_KEY not set."

        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "user", "content": f"Analyze these logs and explain anomalies or issues:\n{output}"}
            ]
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content'] if 'choices' in result else result

    except Exception as e:
        return f"Error analyzing logs: {e}"
