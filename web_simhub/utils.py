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
from misc import Power
whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace


class CPower(object):
    observer = list()

    @staticmethod
    def restart():
        try:
            for cb in CPower.observer:
                cb()
        finally:
            Power.powerRestart()

    @staticmethod
    def attach(cb):
        CPower.observer.append(cb)


def isdigit(dig_str):
    for _ in dig_str:
        if _ not in digits:
            return False
    return True


def net_status(delay=10 * 60):
    import modem
    import checkNet
    PROJECT_NAME = modem.getDevModel()
    PROJECT_VERSION = modem.getDevFwVersion()
    checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
    stagecode, subcode = checknet.wait_network_connected(delay)
    if stagecode == 3 and subcode == 1:
        return True
    return False


def hex2bytes(hex):
    str_len = len(hex)
    if str_len % 2 != 0:
        raise Exception("不是合法的十六进制字符串")
    bytes = bytearray()
    for i in range(0, str_len, 2):
        bytes.append(int(hex[i:i + 2], 16))
    return bytes


def bytes2hex(bytes):
    hex_str = ""
    for item in bytes:
        hex_str = hex_str + '%02X' % item
    return hex_str



def int2ip(int_ip):
    if not isinstance(int_ip, (int, bytes)):
        raise Exception("只支持整数和字节到IP的转换")
    if isinstance(int_ip, bytes):
        int_ip = int.from_bytes(
            int_ip, "big"
        )
    return str((int_ip >> 24) & 0xff) + "." + str((int_ip >> 16) & 0xff) + "." + str(
        (int_ip >> 8) & 0xff) + "." + str(int_ip & 0xff)


def ip2int(ip):
    ip_array = ip.split(".")
    if len(ip_array) != 4:
        raise Exception("ip地址错误")
    ba = bytearray()
    ba.append(int(ip_array[0]) & 0xff)
    ba.append(int(ip_array[1]) & 0xff)
    ba.append(int(ip_array[2]) & 0xff)
    ba.append(int(ip_array[3]) & 0xff)
    return int.from_bytes(
        ba, "big"
    )





import ujson
import ubinascii
import usys

_QPY_DATA_FILENAME = '/usr/qpy_data'

_QPY_MAX_FILE_SIZE = 12 * 2014  # 数据文件最多能存储12K数据


def save2file(data, file=None):
    '''
    保持数据到文件；
    例如 save_data_to_file({1:2,"hello":"world"})
    :param file :文件名
    :param data: 字典类型
    :return: True or False;True表示保持成功，False代表失败
    '''
    if not isinstance(data, dict):
        raise Exception("数据类型为字典，例如：{‘2’:2,'hello':‘world’}")
    try:
        bdata = ujson.dumps(data)
        if len(bdata) > _QPY_MAX_FILE_SIZE:
            raise Exception("数据超过了12K")
        data64 = ubinascii.b2a_base64(bdata)
        with open(file or _QPY_DATA_FILENAME, "wb") as f:
            f.write(data64)
        return True
    except:
        usys.print_exception()
        return False


import uos


def data_from_file(file=None):
    '''
    恢复保持的数据，返回字典类型：
    例如 {1:2,"hello":"world"}
    :param file:文件名
    :return:
    '''

    if file is None:
        file = _QPY_DATA_FILENAME
    else:
        filename = file.split("/")[-1]
        if filename not in uos.listdir("/usr"):
            return {}
    with open(file, "rb") as f:
        data64 = f.read()
    if not data64:
        return {}
    try:
        bdata = ubinascii.a2b_base64(data64)
        data = ujson.loads(bdata)
        return data
    except:
        usys.print_exception()
        uos.remove(_QPY_DATA_FILENAME)
        return {}


from machine import WDT

wdt = None


def _feed_dog():
    wdt.feed()


def start_wdt():
    '''
    开启看门狗
    '''
    from usr.sys import Task
    global wdt
    if wdt is not None:
        raise Exception("看门狗已经启动")
    wdt = WDT(60)
    Task(_feed_dog, seconds=30).start()


import utime
import machine
import pm


def enter_sleep(sleep_sec):
    def rtc_callback(*args):
        print(args)

    current_seconds = utime.time()
    wake_up_time = utime.localtime(current_seconds + sleep_sec)
    rtc = machine.RTC()
    rtc.register_callback(rtc_callback)
    wake_up_time = list(wake_up_time)
    wake_up_time.insert(3, (wake_up_time[-2] + 1) % 7)
    wake_up_time.pop()
    rtc.set_alarm(wake_up_time)
    re = rtc.enable_alarm(1)
    pm.autosleep(1)
