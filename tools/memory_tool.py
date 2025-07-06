import psutil
def check_memory():
    try:
         mem = psutil.virtual_memory()
         return f"Memory Usage: {mem.percent:.2f}% (used {mem.used // (1024**2)} MB of {mem.total // (1024**2)}MB)"
    except Exception as e:
        return f"Error checking memory: {e}"
