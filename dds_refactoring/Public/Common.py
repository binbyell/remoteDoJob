import csv
from collections import defaultdict
import pandas as pd
import os.path
import datetime
import requests
import json
import sys
from multiprocessing import Pool, Manager
from itertools import repeat
import time
import threading
import random
from DDS_GUI import gui_view_class

api_key = 'mBC9%2FHjJoI52LSesUKliiF4nYyM7PKByjnnyEL3wcYIZlJdH2yWxogBR9%2FHYt2UxbkR2rRPyZ2F%2FAn70tbYlXA%3D%3D'

# RootPath = './data'
# Attach = 'wind'
# AttachPath = f'{RootPath}/{Attach}'
# CollectType = 'wind'
# NumberOfCollect = 24


class Tag:
    wind: str = 'Wind'
    dust: str = 'Dust'
    traffic: str = 'Traffic'
    vssl: str = 'Vssl'
    weather: str = 'Weather'
    encoding: str = 'utf-8'


class InitDict:
    # rootIndex + 1 = RootPath
    # index + 1 = Attach
    # index + 2 = collectType

    # RootPath: str
    # Attach: str
    # AttachPath: str
    # CollectType: str
    # NumberOfCollect: int
    # frame_form: gui_view_class.FrameForm
    # Now: datetime.datetime
    """
    folder path : AttachPath
    file path : AttachPath / **{CollectType}**
    """

    def __init__(self, collect_type: str, now: datetime.datetime = datetime.datetime.now()):
        try:
            configTxt_path = '../path.txt'
            configTxt = open(configTxt_path, 'r')
        except FileNotFoundError:
            configTxt_path = './path.txt'
            configTxt = open(configTxt_path, 'r')
        lines = configTxt.readlines()

        collect_type_list = ['Wind', 'Dust', 'Traffic', 'Vssl', 'Weather']
        if not (collect_type in collect_type_list):
            collect_type = 'Wind'

        rootIndex = lines.index('RootPath\n')
        Index = lines.index(f'{collect_type}\n')

        self.RootPath = lines[rootIndex + 1].strip().split(':')[-1]
        self.RootPath = self.RootPath.replace('\\', '/')
        self.Attach = lines[Index + 1][:-1].strip().split(':')[-1]
        self.CollectType = lines[Index + 2][:-1].strip().split(':')[-1]

        # number of collect 상한 지정
        number_of_collect = int(lines[Index + 3][:-1].strip().split(':')[-1])
        # if collect_type != 'Vssl' and number_of_collect >= 24:
        #     number_of_collect = 24
        # if collect_type == 'Vssl' and number_of_collect >= 4:
        #     number_of_collect = 4

        if collect_type.lower() == Tag.wind.lower() and number_of_collect >= 24:
            number_of_collect = 24

        self.FolderPath = f'{self.RootPath}/{self.Attach}'

        if collect_type.lower() == Tag.vssl.lower():
            self.MB = float(lines[Index + 4][:-1].strip().split(':')[-1])
            self.MK = float(lines[Index + 5][:-1].strip().split(':')[-1])
            self.MS = float(lines[Index + 6][:-1].strip().split(':')[-1])
        else:
            # self.MB = 0.5196178778573866
            # self.MK = 0.1741157739110656
            # self.MS = 0.3062663482315478
            self.MB = 0
            self.MK = 0
            self.MS = 0

        self.NumberOfCollect = number_of_collect
        self.Now = now
        ...


def url_to_response_text(url):
    headers = {'content-type': 'application/json;charset=utf-8'}
    response = requests.get(url, headers)
    if response.status_code != 200:
        return int(response.status_code)
    responseText = response.text
    return responseText


def make_csv_path(encoding, item, init_dict: InitDict, is_pretreatment=False):
    attachPath = init_dict.FolderPath
    collectType = init_dict.CollectType
    month = init_dict.Now.strftime('%Y%m')
    if is_pretreatment:
        csvPath = f"{attachPath}/{collectType}_{encoding}_Pretreatment_{item}_{month}.csv"
    else:
        csvPath = f"{attachPath}/{collectType}_{encoding}_{item}_{month}.csv"
    return csvPath


def is_path(path: str):
    if os.path.isfile(path):
        return True
    else:
        return False


def call_csv_last_index(csv_path: str, delta_time: str, need_first_bool: bool = False):
    delta: datetime.timedelta
    if delta_time == "days":
        delta = datetime.timedelta(days=1)
    elif delta_time == "hours":
        delta = datetime.timedelta(hours=1)
    else:
        delta = datetime.timedelta(hours=1)
    try:
        csvData: pd.DataFrame
        csvData = pd.read_csv(csv_path, index_col=0)
        csvLastIndex = csvData.index[-1]
        return csvLastIndex
    except Exception as e:
        now = datetime.datetime.now()
        an_hour_ago = now - datetime.timedelta(hours=2)
        if need_first_bool:
            return (now - datetime.timedelta(days=14)).strftime("%Y%m%d%H")
        return an_hour_ago.strftime("%Y%m%d%H")


def change_hour_1_to_24(date_time: datetime.datetime, check_type: str = "all") -> str:
    """
    change_hour_1_to_24

    check minute:
      because of api upload time, check minute to change hour.
      if minute under 40, change hour [n] to [n-1]

    check hour:
      change hour data [00<=hour_data<=23] to [01<=hour_data<=24]
    """
    check_minute_bool: bool = True if (check_type == "all" or check_type == "minute") else False
    check_hour_bool: bool = True if (check_type == "all" or check_type == "hour") else False
    # check minute
    if int(date_time.strftime('%M')) < 40 and check_minute_bool:
        minute_checked = date_time + datetime.timedelta(hours=-1)
    else:
        minute_checked = date_time
    # check hour 1~24
    if minute_checked.strftime('%H') == '00' and check_hour_bool:
        _time = minute_checked - datetime.timedelta(hours=1)
        result = _time.strftime("%Y%m%d") + str(int(_time.strftime("%H")) + 1)
    else:
        result = minute_checked.strftime('%Y%m%d%H')
    return result


def change_YMDH_to_datetime(YMDH: str) -> datetime.datetime:
    YMDH = str(YMDH)
    if int(f"{YMDH[8:]}") == 24:
        YMDH = f"{YMDH[:8]}23"

        result = datetime.datetime(year=int(f"{YMDH[:4]}"), month=int(f"{YMDH[4:6]}"),
                                   day=int(f"{YMDH[6:8]}"), hour=int(f"{YMDH[8:]}"))

        return result + datetime.timedelta(hours=1)
    else:
        datetime.datetime(year=int(f"{YMDH[:4]}"), month=int(f"{YMDH[4:6]}"),
                          day=int(f"{YMDH[6:8]}"), hour=int(f"{YMDH[8:]}"))


def list_data_to_data_frame_data(type_list_data: list, columns: list):
    # It must to be
    # len(type_list_data) == len(columns)
    temp = dict()
    for index in range(len(type_list_data)):
        temp.setdefault(columns[index], [])
        temp[columns[index]].append(type_list_data[index])
    testDF = pd.DataFrame(temp)
    if len(type_list_data) != 0:
        testDF.set_index('dataTime', inplace=True)
    # print(f"pb testDF : \n{testDF}")
    return testDF


def list_data_list_to_df(_data_list: list, _data_columns: list):
    tempDF = pd.DataFrame()
    count = 0
    for list_data in _data_list:
        singleData = list_data_to_data_frame_data(list_data, _data_columns)
        if tempDF.size == 0:
            tempDF = singleData
        else:
            tempDF = pd.concat([tempDF, singleData], axis=0)
        count += 1
    return tempDF


def update_csv(csv_path: str, data: pd.DataFrame, need_recent: bool = True):

    data.index = [int(index) for index in data.index]

    recentN = 14*24

    # 입력 DataFrame
    # path = csv path
    # DataFrame return
    result: pd.DataFrame

    # folderPath 추출
    splitPathList = csv_path.split('/')

    folderPath = splitPathList[0]
    fileName = splitPathList[-1]
    for eachPath in splitPathList[1:-1]:
        folderPath = f"{folderPath}/{eachPath}"
    # folderPath ex) ./220707/dust

    # csv파일 있는지 확인. 있으면 업데이트
    if os.path.isfile(csv_path):
        csvData = pd.read_csv(csv_path, index_col=0)
        # check csv is null
        if csvData.index.size == 0:
            result = pd.concat([csvData, data], axis=0)
            result = result.sort_index()
            result.to_csv(csv_path, index_label='dataTime')
            print(f"public. csvData.index.size == 0 \n{result}")
        else:
            csvLastIndex = csvData.index[-1]
            print(f"to check type\ncsvLastIndex:{type(csvLastIndex)}\ncsvData.index[-1]:{type(csvData.index[-1])}")
            print(f"Common test data.index {data.index}")
            print(f"Common test csvLastIndex {csvLastIndex}")
            if csvLastIndex not in [int(index) for index in data.index]:
                result = pd.concat([csvData, data], axis=0)
                result = result.sort_index()
                result.to_csv(csv_path, index_label='dataTime')
                print('updated')
                # print(f"public. csvLastIndex != data.index[0] \n{result}")
            else:
                csvData = csvData.sort_index()
                csvData.to_csv(csv_path, index_label='dataTime')
                result = csvData
                print('data was in csv')
                # print(f"public. csvLastIndex == data.index[0] \n{result}")
    else:
        # folder 없으면 생성
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        # csv 생성
        result = data
        result = result.sort_index()
        result.to_csv(csv_path, index_label='dataTime')
        # print(f"public. not os.path.isfile(csv_path) \n{result}")

    # test recent 14day
    if need_recent:
        # recent Path
        fileNameSplit = fileName.split('.')
        csv_path_recent_14 = f"{folderPath}/{fileNameSplit[-2][:-6]}recent.{fileNameSplit[-1]}"

        recent_df = result

        print(f"csv_path_recent_14 : {csv_path_recent_14}")
        if len(recent_df) < recentN:
            recent_df = recent_df.sort_index()
            recent_df.to_csv(csv_path_recent_14, index_label='dataTime')
        else:
            pin = recent_df.index[len(recent_df) - recentN]
            # print(f"Common test before sort index :\n{recent_df}")
            # print(f"Common test after sort index :\n{recent_df.sort_index}")
            # print(f"Common test after sort index :\n{recent_df}")
            recent_df = recent_df.sort_index()
            recent_df.truncate(before=pin, axis=0).to_csv(csv_path_recent_14, index_label='dataTime')
    return result


def care_exception(e, folder_path, file_path):
    now = datetime.datetime.now()
    path_log = folder_path
    path_log_txt = file_path
    if not (os.path.isdir(path_log)):
        os.makedirs(os.path.join(path_log))
    if not (os.path.isfile(path_log_txt)):
        f = open(path_log_txt, 'w', encoding='utf-8')
        content = f"\nerror: {now.strftime('%Y%m%d  %H:%M')}\n\t- {e} -"
        f.write(content)
        f.close()
    else:
        f = open(path_log_txt, 'a', encoding='utf-8')
        content = f"\nerror: {now.strftime('%Y%m%d  %H:%M')}\n\t- {e} -"
        f.write(content)
        f.close()
    print(f"error care_exception: {e}")
    ...


# app: dds_gui.Application
def text_insert(app, txt: str):
    app.text.insert(txt)
