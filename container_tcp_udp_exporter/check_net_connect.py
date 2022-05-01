import os
from prometheus_client import Gauge

g_tcp = Gauge("tcp_number", 'get tcp connect numbers', ['instance', 'namespace', 'pod_name', 'container_name'])
g_dup = Gauge("udp_number", "get udp connect numbers", ["instance", "namespace", "pod_name", "container_name"])

if os.system("systemctl status docker") == 0:
    print("docker is running!")
elif os.system("system status containerd") == 0:
    print("containerd is running!")
else:
    print("docker or containerd process dose not running...")
