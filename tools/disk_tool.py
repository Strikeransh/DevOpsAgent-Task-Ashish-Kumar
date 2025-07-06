import psutil
def check_disk()
    try:
        usage = shutil.disk_usage('/')
        percent = (usage.used / usage.total)*100
        return f"Disk usage: {percent:.2f}% (used (usage.used //(1024**3)}GB of {usage.total // (1024**3)}GB)"
    except Exception as e:
        return f"Error checking disk: {e}"
