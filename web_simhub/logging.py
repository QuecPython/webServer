# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import utime
import usys

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4
DESC = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
}


def log(obj, level, *message, local_only=False, return_only=False, timeout=None):
    if level < obj._level:
        return
    name = obj.name
    level = DESC[level]
    if hasattr(utime, "strftime"):
        print("[{}]".format(utime.strftime("%Y-%m-%d %H:%M:%S")), "[{}]".format(name),
              "[{}]".format(level), *message)
    else:
        t = utime.localtime()
        print("[{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}]".format(*t), "[{}]".format(name),
              "[{}]".format(level), *message)
    if return_only:
        return


class Logger:
    def __init__(self, name):
        self.name = name
        self._level = DEBUG

    def set_level(self, level):
        if level > CRITICAL or level < DEBUG:
            raise Exception("日志级别错误")
        self._level = level

    def critical(self, *message, local_only=True):
        log(self, CRITICAL, *message, local_only=local_only, timeout=None)

    def error(self, *message, exc=None, local_only=True):
        log(self, ERROR, *message, local_only=local_only, timeout=None)
        if exc is not None and isinstance(exc, Exception):
            usys.print_exception(exc)

    def warn(self, *message, local_only=True):
        log(self, WARNING, *message, local_only=local_only, timeout=None)

    def info(self, *message, local_only=True):
        log(self, INFO, *message, local_only=local_only, timeout=20)

    def debug(self, *message, local_only=True):
        log(self, DEBUG, *message, local_only=local_only, timeout=5)

    def asyncLog(self, level, *message, timeout=True):
        pass



def get_logger(name):
    return Logger(name)
