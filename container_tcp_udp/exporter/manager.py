from flask import Response, Flask
from exporter import Exporter
import prometheus_client

container = Exporter()

app = Flask(__name__)


# define route


@app.route("/metrics/tcp")
def api_tcp_response():
    container_info = container.generate_container_tcp_info()
    if container_info is None:
        pass
    else:
        for key, value in container_info.items():
            for status, number in value["status"].items():
                container.g_tcp.labels(
                    instance=value["instance"], namespace=value["namespace"], status=status,
                    container_name=value["container_name"], pod_name=value["pod_name"],
                    container_id=value["container_id"]).set(value=number)

    return Response(prometheus_client.generate_latest(container.g_tcp), mimetype="text/plain")


@app.route("/metrics/udp")
def api_udp_response():
    container_info = container.generate_container_udp_info()
    if container_info is None:
        pass
    else:
        for key, value in container_info.items():
            container.g_udp.labels(
                instance=value["instance"], namespace=value["namespace"],
                container_name=value["container_name"],
                pod_name=value["pod_name"], container_id=value["container_id"]).set(
                value=value["udp"])

    return Response(prometheus_client.generate_latest(container.g_udp), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
