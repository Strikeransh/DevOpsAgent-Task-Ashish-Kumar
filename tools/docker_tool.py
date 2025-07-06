# tools/docker_tool.py
import subprocess

def restart_container(container_id_or_name="$(docker ps -q --no-trunc | head -n 1)"):
    try:
        output = subprocess.check_output(["bash", "-c", f"docker restart {container_id_or_name}"]).decode("utf-8").strip()
        return f"🔁 Restarted container: {output}"
    except subprocess.CalledProcessError as e:
        return f"Failed to restart container: {e.output.decode('utf-8')}"
    except Exception as e:
        return f"Error restarting container: {e}"
