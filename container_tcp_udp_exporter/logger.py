
from cgitb import handler
import logging
import os
from select import select
import sys
import time
from singleton import Singleton


@Singleton
class Logger:
    def __init__(self, set_level="INFO",
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[0],
                 log_name=time.strftime("%Y-%m-%d.log", time.localtime()),
                 log_path=os.path.join(os.path.dirname(
                     os.path.abspath(__file__)), "log"),
                 use_console=True) -> None:
        """
        :param set_level: 日志级别["NOTSET"|"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"],默认为INFO
        :param name: 日志中打印的name,默认为运行程序的name
        :param log_name: 日志文件的名字，默认为当前时间（年-月-日.log)
        :param log_path: 日志文件夹的路径,默认为logger.py同级目录中的log文件夹
        :param use_console: 是否在控制台打印,默认为True
        """

        if not set_level:
            set_level = self._exec_type()
        self.__logger = logging.getLogger(name)

        self.setLevel(getattr(logging, set_level.upper())) if hasattr(
            logging, set_level.upper()) else logging.INFO
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        formatter = logging.Formatter(
            "%(asctime)s %(pathname)s %(funcName)s %(lineno)d %(process)d %(levelname)s %(message)s")
        handler_list = list()
        handler_list.append(logging.FileHandler(
            os.path.join(log_path, log_name), encoding="utf-8"))
        if use_console:
            handler_list.append(logging.StreamHandler())
        for handler in handler_list:
            handler.setFormatter(formatter)
            self.addHandler(handler)

    def __getattr__(self, item):
        return getattr(self.logger, item)

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, func):
        self.__logger = func

    def _exec_type(self):
        return "DEBUG" if os.environ.get("IPYTHONENABLE") else "INFO"