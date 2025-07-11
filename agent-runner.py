# agent_runner.py

import os
import subprocess
from langchain.agents import initialize_agent, Tool
#from langchain_core.language_models import ChatModel
#from groq import Groq
from tools.cpu_tool import get_cpu_usage
from tools.disk_tool import check_disk
from tools.log_tool import fetch_and_analyze_logs
from tools.docker_tool import restart_container
from tools.slack_tool import notify_slack
from tools.memory_tool import check_memory
from tools.network_tool import check_network
#from langchain_community.chat_models import ChatGroq
from langchain_groq import ChatGroq
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-70b-8192"
)
webhook = os.getenv("SLACK_WEBHOOK")
#Thresholds
CPU_THRESHOLD = 50.0
DISK_THRESHOLD = 80.0
MEM_THRESHOLD = 85.0

#Set up Groq LLM wrapper
#llm = Groq(
#    api_key=os.getenv("GROQ_API_KEY"),
#    model="mixtral-8x7b-32768"
#    model="meta-llama/llama-4-scout-17b-16e-instruct"
#)

#Define tools for the agent
tools = [
    Tool(name="CheckCPU", func=get_cpu_usage, description="Check CPU usage."),
    Tool(name="CheckDisk", func=check_disk, description="Check disk usage."),
    Tool(name="CheckMemory", func=check_memory, description="Check memory usage."),
    Tool(name="CheckNetwork", func=check_network, description="Check network usage."),
    Tool(name="AnalyzeLogs", func=fetch_and_analyze_logs, description="Analyze logs using LLM."),
    Tool(name="RestartContainer", func=restart_container, description="Restart a container."),
    Tool(name="NotifySlack", func=notify_slack, description="Send Slack alert.")
]

#Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="chat-zero-shot-react-description",
    verbose=True
)

#Helper to extract percentage from output
def parse_percent(output):
    try:
        return float(output.split(":")[1].strip().split("%")[0])
    except:
        return 0.0

#Check current usage
cpu = get_cpu_usage()
disk_raw = check_disk()
mem_raw = check_memory()
#try:
#    cpu = float(cpu_raw) if isinstance(cpu_raw, (float, int)) else -1.0
#except:
#    cpu = -1.0
disk = parse_percent(check_disk())
mem = parse_percent(check_memory())
try:
    print(f" CPU: {cpu:.2f}%, Disk: {disk:.2f}%, Memory: {mem:.2f}%")
except Exception as e:
    print(f"❌ Error displaying metrics: {e}")
    print(f"Raw values — CPU: {cpu}, Disk: {disk_raw}, Memory: {mem_raw}")

if cpu > CPU_THRESHOLD or disk > DISK_THRESHOLD or mem > MEM_THRESHOLD:
    print(" Threshold breached — launching LLM agent...")
    response = agent.run(
        "Check CPU, memory, and disk usage. If something is high, analyze logs, recommend actions, and notify via Slack."
    )
    print("\n Agent Response:\n", response)
else:
    print(" All metrics within safe range. No action taken.")

