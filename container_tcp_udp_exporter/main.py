
import json
from prometheus_client import Gauge
from flask import Response, Flask
from exporter import Exporter
import prometheus_client

exporter = Exporter()

app = Flask(__name__)

# define route


@app.route("/metrics")
def ApiResponse():
    container_info = exporter.generate_container_info()
    if container_info==None:
        pass
    else:
        for key, value in container_info.items():
            # g.lable(instance="127.0.0.1",namespace=container_info["namespace"],container_name=container_info["container_name"],pod_name=container_info["pod_name"])
            exporter.g_tcp.labels(instance=value["instance"], namespace=value["namespace"],
                    container_name=value["container_name"], pod_name=value["pod_name"], container_id=value["container_id"]).set(value=value["tcp_number"])

    return Response(prometheus_client.generate_latest(exporter.g_tcp), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
