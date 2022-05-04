
import os
import json
from typing import Container
import logger
from prometheus_client import Gauge
import subprocess


log = logger.Logger("debug")


class Exporter:

    def __init__(self):
        self.__g_tcp = Gauge("tcp_number", 'get tcp connect numbers', [
            'instance', 'namespace', 'pod_name', 'container_name'])
        self.__g_dup = Gauge("udp_number", "get udp connect numbers", [
            "instance", "namespace", "pod_name", "container_name"])

        if subprocess.call(["systemctl", "status", "docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            log.info("docker is running!")
            self.cri = "docker"
        elif subprocess.call(["systemctl", "status", "containerd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            log.info("containerd is running!")
            self.cri = "containerd"
        else:
            log.info("docker or containerd process dose not running...")
            self.cri = ""

    def get_container_tcp_number(self,container_pid):
        try:
            get_tcp_info_cmd = "sudo nsenter -t %s -n netstat -tna |egrep -v '0.0.0.0|127.0.0.1|:::' |wc -l" % (
                container_pid)
            exec_command = subprocess.run(
                get_tcp_info_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" % get_tcp_info_cmd)
            else:
                tcp_number = exec_command.stdout.replace("\n", "")
                return tcp_number
        except Exception as e:
            log.error(e)

    def get_container_id(self):
        if self.cri == "dcoker":
            # get_container_name_cmd = "docker ps | awk 'NR==1 {next} {print $NF}' | grep 'k8s' |grep -v 'POD'"
            get_container_id_cmd = "docker ps | awk 'NR==1 {next} {print $NF}' |grep -v 'POD'"
        elif self.cri == "containerd":
            get_container_id_cmd = "crictl ps |awk 'NR==1 {next} {print $1}'"
        try:
            exec_command = subprocess.run(
                get_container_id_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" % get_container_id_cmd)
            else:
                log.info("get container id: \n%s" % exec_command.stdout)
                return exec_command.stdout.split()
        except Exception as e:
            log.error(e)

    def get_container_pid(self, container_id):
        if self.cri == "dcoker":
            get_container_pid_cmd = "docker inspect -f '{{.State.Pid}}' %s " % (
                container_id)
        elif self.cri == "containerd":
            get_container_pid_cmd = "crictl inspect %s" % (container_id)
        try:
            exec_command = subprocess.run(
                get_container_pid_cmd, stdin=None, input=None, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, timeout=None, check=False, universal_newlines=True)
            if exec_command.returncode != 0:
                log.error("exec command errror: %s" % get_container_pid_cmd)
            else:
                container_pid = json.loads(exec_command.stdout)["info"]["pid"]
                return container_pid
        except Exception as e:
            log.error(e)

    def command_generate(self):
        containers_id=self.get_container_id()
        if containers_id!=None:
            for id in containers_id:
                pid=self.get_container_pid(container_id=id)
                if pid!="":
                    tcp_number=self.get_container_tcp_number(container_pid=pid)
                    log.info("get container(id: %s) tcp number is: %s" % (id,tcp_number))
                else:
                    log.warn("container_id(%s) is None" % id)
        else:
            log.warn("container_id(%s) is None" %containers_id)


exporter = Exporter()
exporter.command_generate()
