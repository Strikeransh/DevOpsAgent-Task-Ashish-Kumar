import util
def check_network():
    try:
        net_io = psutil.net_io_counters()
        sent_mb = net_io.bytes_sent / (1024*1024)
        recv_mb = net_io.bytes_recv / (1024*1024)
        return f"Network I/O = sent: {sent_mb:.2f} MB, Received: {recv_mb:.2f} MB"
    except Exception as e:
         return f"Error checking Network:" {e}"
