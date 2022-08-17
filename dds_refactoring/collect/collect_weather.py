import requests
import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import urllib3
import glob

from pandas import DataFrame
from time import sleep
from Public import Common
import datetime


def call_weather_api_first(pass_time_check: bool = False):
    _initDict = Common.InitDict('Weather')
    # API 키는 공개하기 힘든 점 양해 바랍니다.
    # api_key = open("./raw_data/weather_api").readlines()[0].strip()
    api_key = 'Ae9m5RKSiv7oQTVPmqKWH5BdM8aVGt6yGRwIV1Wh34zFQJF5R/NkR92v2Z0DQixg'

    headers = {'content-type': 'application/json;charset=utf-8'}
    urllib3.disable_warnings()

    endDate = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    startDate = (datetime.datetime.now() - datetime.timedelta(days=_initDict.NumberOfCollect)).strftime('%Y%m%d')
    hourNow = int(datetime.datetime.now().strftime('%H'))
    print(f"hourNow : {hourNow}")
    startHh = '00'
    endHh = '23'
    snt_id = "159"

    url = f"https://data.kma.go.kr/apiData/getData?type=json&dataCd=ASOS&dateCd=HR&startDt={startDate}" \
          f"&startHh={startHh}&endDt={endDate}&endHh={endHh}&stnIds={snt_id}&schListCnt={_initDict.NumberOfCollect * 24}&pageIndex=1&apiKey={api_key}"

    print(f"url : {url}")
    response = requests.get(url, headers=headers, verify=False)

    # 200 (정상)의 경우에만 파일 생성
    print(response.status_code)

    if response.status_code == 200:
        result = pd.DataFrame(response.json()[-1]["info"])
        print(result.head())

        if not os.path.isdir(_initDict.FolderPath):
            os.makedirs(_initDict.FolderPath)

        print(f"path weather :\n{_initDict.FolderPath}/weather_{endDate}.csv")
        # result.to_csv(f"{_initDict.FolderPath}/weather_{endDate}.csv", index=False, encoding="utf-8-sig")

        result_change_col = result[['TM', 'TA', 'WD', 'WS', 'HM', 'PV', 'TD', 'PA', 'PS', 'ICSR', 'VS', 'TS',
                                    'M0_05_TE', 'M0_1_TE', 'M0_2_TE', 'M0_3_TE']]

        result_change_col.columns = ['dataTime', 'ta', 'wd', 'ws', 'hm', 'pv', 'td', 'pa', 'ps', 'icsr', 'vs', 'ts',
                                    'm005Te', 'm01Te', 'm02Te', 'm03Te']
        result_change_col.set_index()
        print(f"result_change_col : \n{result_change_col}")

        # API 부하 관리를 위해 0.5초 정도 쉬어 줍시다 (찡긋)
        sleep(1.5)

        return True
    return False


def call_weather_api(pass_time_check: bool = False):
    _initDict = Common.InitDict('Weather')
    # API 키는 공개하기 힘든 점 양해 바랍니다.
    # api_key = open("./raw_data/weather_api").readlines()[0].strip()
    api_key = 'Ae9m5RKSiv7oQTVPmqKWH5BdM8aVGt6yGRwIV1Wh34zFQJF5R/NkR92v2Z0DQixg'

    headers = {'content-type': 'application/json;charset=utf-8'}
    urllib3.disable_warnings()

    date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    hourNow = int(datetime.datetime.now().strftime('%H'))
    print(f"hourNow : {hourNow}")
    if not (pass_time_check or hourNow == 1 or hourNow == 13):
        print(f"hourNow : {hourNow}, hourNow need to be 01 or 13")
        print("This is not time to get weather data")
        return False
    startHh = '00'
    endHh = '23'
    snt_id = "159"

    url = f"https://data.kma.go.kr/apiData/getData?type=json&dataCd=ASOS&dateCd=HR&startDt={date}" \
          f"&startHh={startHh}&endDt={date}&endHh={endHh}&stnIds={snt_id}&schListCnt=100&pageIndex=1&apiKey={api_key}"

    print(f"url : {url}")
    response = requests.get(url, headers=headers, verify=False)

    # 200 (정상)의 경우에만 파일 생성
    print(response.status_code)

    if response.status_code == 200:
        result = pd.DataFrame(response.json()[-1]["info"])
        print(result.head())

        if not os.path.isdir(_initDict.FolderPath):
            os.makedirs(_initDict.FolderPath)

        print(f"path weather :\n{_initDict.FolderPath}/weather_{date}.csv")
        result.to_csv(f"{_initDict.FolderPath}/weather_{date}.csv", index=False, encoding="utf-8-sig")

        # API 부하 관리를 위해 0.5초 정도 쉬어 줍시다 (찡긋)
        sleep(1.5)

        return True
    return False


if __name__ == '__main__':
    call_weather_api_first()
    # call_weather_api()
