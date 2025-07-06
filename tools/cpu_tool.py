# tools/cpu_tool.py
from prometheus_api_client import PrometheusConnect
import subprocess
prom = PrometheusConnect(url="http://localhost:9090", disable_ssl=True)
THRESHOLD = 50.0
QUERY = """
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[2m]))
"""
#3. CPU USAGE FUNCTION
def get_cpu_usage(_input=None):
    try:
        result = prom.custom_query(query=QUERY)
        #result = prom.get_current_metric_value(metric_name='node_cpu_seconds_total')
        if result:
            usage = float(result[0]['value'][1]) * 100
            return round(usage, 2)
    except Exception as e:
        print(f"Error fetching CPU usage: {e}")
    return None
