# threshold_monitor.py
from tools.cpu_tool import get_cpu_usage
from tools.memory_tool import check_memory
from tools.disk_tool import check_disk
import os
import subprocess

CPU_THRESHOLD = 50.0
DISK_THRESHOLD = 80.0
MEM_THRESHOLD = 85.0

def parse_percent(output):
    return float(output.split(":")[1].strip().split("%")[0])

def run_agent():
    print("🚀 Threshold breached — launching LLM agent...")
    subprocess.run(["python3", "agent_runner.py"])

def main():
    cpu = get_cpu_usage()
    disk_output = check_disk()
    mem_output = check_memory()

    disk = parse_percent(disk_output)
    mem = parse_percent(mem_output)

    print(f"📊 CPU: {cpu:.2f}%, Disk: {disk:.2f}%, Memory: {mem:.2f}%")

    if cpu > CPU_THRESHOLD or disk > DISK_THRESHOLD or mem > MEM_THRESHOLD:
        run_agent()
    else:
        print("✅ All metrics within safe range.")

if __name__ == "__main__":
    main()
