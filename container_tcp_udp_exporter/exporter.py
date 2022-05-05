
import imp
import json
import logger
import socket
from prometheus_client import Gauge
import subprocess
from prometheus_client import CollectorRegistry


log = logger.Logger("debug")


class Exporter:

    def __init__(self):
        self.__REGISTRY = CollectorRegistry(auto_describe=False)
        self.g_tcp = Gauge('container_tcp_num', 'get container tcp connect number', [
            'instance', 'namespace', 'container_name', 'pod_name', 'container_id'], registry=self.__REGISTRY)
        self.g_udp = Gauge("udp_number", "get udp connect numbers", [
            "instance", "namespace", "container_name", "pod_name", "continaer_id"], registry=self.__REGISTRY)

        if subprocess.call(["systemctl", "status", "docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            log.info("docker is running!")
            self.cri = "docker"
        elif subprocess.call(["systemctl", "status", "containerd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            log.info("containerd is running!")
            self.cri = "containerd"
        else:
            log.info("docker or containerd process dose not running...")
            self.cri = ""
        self.get_container_id_cmd = ""
        self.get_container_pid_cmd = ""
        self.get_container_name_cmd=""

    def get_container_tcp_number(self, container_pid):
        try:
            get_tcp_info_cmd = "sudo nsenter -t %s -n netstat -tna |egrep -v '0.0.0.0|127.0.0.1|:::' |wc -l" % (
                container_pid)
            exec_command = subprocess.run(
                get_tcp_info_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" % get_tcp_info_cmd)
            else:
                tcp_number = exec_command.stdout.strip()
                return tcp_number
        except Exception as e:
            log.error(e)

    def get_container_id(self):
        if self.cri == "docker":
            # get_container_name_cmd = "docker ps | awk 'NR==1 {next} {print $NF}' | grep 'k8s' |grep -v 'POD'"
            self.get_container_id_cmd = "docker ps | awk 'NR==1 {next} {print $1}' |grep -v 'POD'"
        elif self.cri == "containerd":
            self.get_container_id_cmd = "crictl ps |awk 'NR==1 {next} {print $1}'"
        try:
            exec_command = subprocess.run(
                self.get_container_id_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" %
                          self.get_container_id_cmd)
            else:
                return exec_command.stdout.split()
        except Exception as e:
            log.error(e)

    def get_container_pid(self, container_id):
        if self.cri == "docker":
            self.get_container_pid_cmd = "docker inspect -f '{{.State.Pid}}' %s " % (
                container_id)
        elif self.cri == "containerd":
            self.get_container_pid_cmd = "crictl inspect %s" % (container_id)
        try:
            exec_command = subprocess.run(
                self.get_container_pid_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" % self.get_container_pid_cmd)
            else:
                if self.cri== "docker":
                    return exec_command.stdout.strip()
                elif self.cri=="containerd":
                    container_pid = json.loads(exec_command.stdout)["info"]["pid"]
                    return container_pid
        except Exception as e:
            log.error(e)

    def get_container_lable(self, container_id):
        if self.cri == "docker":
            self.get_container_name_cmd = "docker inspect -f %s " % (
                container_id)
        elif self.cri == "containerd":
            self.get_container_name_cmd = "crictl inspect %s" % (container_id)
        try:
            exec_command = subprocess.run(
                self.get_container_name_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" % self.get_container_name_cmd)
            else:
                tmp_dict={}
                hostname=socket.gethostname()
                tmp_dict["instance"]=socket.gethostbyname(hostname)
                pid = self.get_container_pid(container_id)
                if self.cri=="docker":
                    container_inspect=json.loads(exec_command.stdout)
                    tmp_dict["container_id"]=container_id
                    tmp_dict["namespace"]=container_inspect["Config"]["Labels"]["io.kubernetes.pod.namespace"]
                    tmp_dict["pod_name"]=container_inspect["Config"]["Labels"]["io.kubernetes.pod.name"]
                    tmp_dict["container_name"]=container_inspect["Config"]["Labels"]["io.kubernetes.container.name"]
                    tmp_dict["tcp_number"]=self.get_container_tcp_number(pid)
                    log.info("get container labels: %s" % tmp_dict)
                    return tmp_dict
                elif self.cri=="containerd":
                    container_inspect=json.loads(exec_command.stdout)
                    tmp_dict["container_id"]=container_id
                    tmp_dict["namespace"]=container_inspect["info"]["config"]["labels"]["io.kubernetes.pod.namespace"]
                    tmp_dict["pod_name"]=container_inspect["info"]["config"]["labels"]["io.kubernetes.pod.name"]
                    tmp_dict["container_name"]=container_inspect["status"]["metadata"]["name"]
                    tmp_dict["tcp_number"]=self.get_container_tcp_number(pid)
                    log.info("get container labels: %s" % tmp_dict)
                    return tmp_dict
        except Exception as e:
            log.error(e)

    def generate_container_info(self):
        container_info = {}
        containers_id = self.get_container_id()
        if containers_id != None:
            container_info={}
            for id in containers_id:
                container_labels=self.get_container_lable(id)     
                container_info[id]=container_labels
            return container_info
        else:
            log.warn("containers_id(%s) is None" % containers_id)
            return None
