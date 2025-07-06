import subprocess
def get_cpu_usage():
    try:
        output = subprocess.check_output(["top", "-bn1"]).decode("utf-8")
        for line in output.split("\n"):
            if "Cpu(s):" in line:
                usage = float(line.split("%us")[0].split()[-1])
                return usage
    except Exception as e:
        return f"Error checking CPU: {e}"

def check_cpu():
    try:
        usage = usage = get_cpu_usage()
        return f"CPU usage: {usage:.2f}%" if isinstance(usage, float) else usage
