import threading
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import time
from time import sleep
import datetime
import queue
from dateutil.relativedelta import relativedelta
import os.path

from collect import collect_wind
from collect import collect_wind_first
from collect import collect_vssl
from collect import collect_dust_ver0718 as collect_dust
from collect import collect_dust_first
from collect import collect_traffic
from collect import collect_weather
from tcp import SocketServerVer220714 as SocketServer
from tcp import SocketMsg
import Public.Common as Common

collection_delay = 1
check_min = 50
quit_value = 1
filename = ""

"""
프로그램 실행시 바로 수집 시작.
메인 : Application 실행
ThreadTest : 보조 스레드, csv파일 수집.

수집
- 첫실행
- 매일 12시(정오, 자정)

global collection_delay
3600 = 1시간
60 = 1분
"""


def check_file(file_path: str):
    return os.path.isfile(file_path)


def dds_collect_wind():
    init = Common.InitDict(Common.Tag.wind)
    path = init.FolderPath

    print(f"wind_data_start  =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    if os.path.isdir(path):
        print("os.path.isdir(path)")
        collect_wind.get_wind()
    else:
        collect_wind_first.get_wind_1st()
        ...
    print(f"wind_data_end    =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")


def dds_collect_dust():
    init = Common.InitDict(Common.Tag.dust)
    path = init.FolderPath

    print(f"dust_data_start  =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    if os.path.isdir(path):
        collect_dust.get_dust()
    else:
        collect_dust_first.get_dust_1st()
    print(f"dust_data_end    =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")


def dds_collect_vssl():
    print(f"vssl_data_start  =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    collect_vssl.get_vssl_with_check_1st()
    print(f"vssl_data_end    =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")


def dds_collect_traffic():
    print(f"traffic_data_start  =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    collect_traffic.get_traffic()
    print(f"traffic_data_end    =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    ...


def dds_collect_weather():
    print(f"weather_data_start  =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    collect_weather.call_weather_api()
    print(f"weather_data_end    =======  {datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")


def test_time_check():
    startT = datetime.datetime.now()
    while True:
        if startT + datetime.timedelta(seconds=5) < datetime.datetime.now():
            startT += datetime.timedelta(seconds=5)
            print("5sec")


def dds_collect(tesk: SocketServer.ServerMain = None):
    try:
        configTxt_path = '../path.txt'
        configTxt = open(configTxt_path, 'r')
    except FileNotFoundError:
        configTxt_path = './path.txt'
        configTxt = open(configTxt_path, 'r')
    lines = configTxt.readlines()
    configTxt.close()
    CollectIndex = lines.index('Collect\n')

    print("----------start----------\n")
    if lines[CollectIndex + 1].strip().split(':')[-1] == 'T':
        dds_collect_wind()
    else:
        print("If you want to collect wind data, set Collect-CollectWind to T")
    if lines[CollectIndex + 2].strip().split(':')[-1] == 'T':
        dds_collect_dust()
    else:
        print("If you want to collect dust data, set Collect-CollectDust to T")
    if lines[CollectIndex + 3].strip().split(':')[-1] == 'T':
        dds_collect_vssl()
    else:
        print("If you want to collect vssl data, set Collect-CollectVssl to T")
    if lines[CollectIndex + 4].strip().split(':')[-1] == 'T':
        dds_collect_traffic()
    else:
        print("If you want to collect traffic data, set Collect-CollectTraffic to T")
    if lines[CollectIndex + 5].strip().split(':')[-1] == 'T':
        dds_collect_weather()
    else:
        print("If you want to collect weather data, set Collect-CollectWeather to T")
    print("----------end----------\n")

    if tesk is not None:
        tesk.room.send_all_clients(SocketMsg.collection_complete)


if __name__ == '__main__':

    try:
        configTxt_path = '../path.txt'
        configTxt = open(configTxt_path, 'r')
    except FileNotFoundError:
        configTxt_path = './path.txt'
        configTxt = open(configTxt_path, 'r')
    lines = configTxt.readlines()
    configTxt.close()
    CollectIndex = lines.index('Tcp\n')
    ip = str(lines[CollectIndex + 1].strip().split(':')[-1])
    port = int(lines[CollectIndex + 2].strip().split(':')[-1])

    t1 = SocketServer.ServerMain(ip=ip, port=port)
    t1.daemon = True
    t1.start()

    pinT_ = datetime.datetime.now()

    dds_collect(t1)

    while True:
        if datetime.datetime.now().strftime('%M:%S') == "50:10":
            pinT_ = datetime.datetime.now()
            dds_collect(t1)
            break

    while True:
        if pinT_ + datetime.timedelta(hours=1) < datetime.datetime.now():
            pinT_ += datetime.timedelta(hours=1)

            dds_collect(t1)
