import csv
from collections import defaultdict
import pandas as pd
import os.path
import datetime
import requests
import json
import sys
import time
import threading
import Public.Common as Common
import collect.collect_wind as collect_wind

api_key = 'mBC9%2FHjJoI52LSesUKliiF4nYyM7PKByjnnyEL3wcYIZlJdH2yWxogBR9%2FHYt2UxbkR2rRPyZ2F%2FAn70tbYlXA%3D%3D'

initDict: Common.InitDict


# return jsonStringList
def get_data_list(nxny, urlTime, count):
    global initDict
    dayTime = urlTime.strftime('%Y%m%d')
    hourTime = urlTime.strftime("%H%M")

    dayUrl = dayTime
    hourUrl = f"{hourTime[:2]}00"

    url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?serviceKey={collect_wind.api_key}&pageNo=1&numOfRows=120" \
          f"&base_date={dayUrl}&base_time={hourUrl}&nx={nxny[0]}&ny={nxny[1]}&dataType=JSON"
    # print(f"url:\n{url}")
    try:
        # get_url_start = datetime.datetime.now()
        jsonText = Common.url_to_response_text(url)
        get_item_wind = collect_wind.get_item(jsonText)
        if not get_item_wind:
            print(url)
            print(f"recall count : {count+1}")
            time.sleep(1)
            if count >= 2:
                time.sleep(5)
            return get_data_list(nxny, urlTime, count+1)

        # dataList[0] = TIME
        # change hour 01~24
        dataList = collect_wind.get_data_list_from_json(get_item_wind, init_dict=initDict)
        if urlTime.strftime('%H') == '00':
            _time = urlTime - datetime.timedelta(hours=1)
            _timeString = _time.strftime("%Y%m%d") + str(int(_time.strftime("%H")) + 1)
            dataList[0] = _timeString

        # get_url_end = datetime.datetime.now()
        # print(f"url delay: {get_url_end - get_url_start}")
        return dataList
    except Exception as e:
        print(f"exception:\n{e}")
        print(url)
        sys.exit()


# 수정 요
def merge_data(nxny, hourTime, return_dict):
    global initDict
    collectCount = 20
    # (initDict.NumberOfCollect * 24) - 1
    dataForDay = []
    pinTime = hourTime - datetime.timedelta(hours=collectCount)
    moveTime = pinTime
    startTime = datetime.datetime.now()
    while moveTime <= hourTime:
        # 수정 요
        dataForHour = get_data_list(nxny, moveTime, 0)
        dataForDay.append(dataForHour)
        moveTime += datetime.timedelta(hours=1)
    endTime = datetime.datetime.now()
    print(nxny)
    print(f"delay 1day : {endTime - startTime}")
    print(f"merge_data dataForDay : {dataForDay}")

    dayDataDF = Common.list_data_list_to_df(dataForDay, collect_wind.columns)
    print(f"merge_check : \n{dayDataDF}")
    key = f"{nxny[0]}_{nxny[1]}"
    path = Common.make_csv_path('utf-8', key, initDict, False)
    Common.update_csv(path, dayDataDF)
    return_dict[key] = dayDataDF


class MergeThread(threading.Thread):
    def __init__(self, nxny, hourTime, return_dict):
        threading.Thread.__init__(self)
        self.nxny = nxny
        self.hourTime = hourTime
        self.return_dict = return_dict

    def run(self):
        merge_data(self.nxny, self.hourTime, self.return_dict)


def get_wind_1st():
    global initDict
    initDict = Common.InitDict(Common.Tag.wind)
    # 시간 채크
    startTime = datetime.datetime.now()
    # 시간 통일
    mainTime = datetime.datetime.now()
    # check 50min
    if int(mainTime.strftime("%M")) < 40:
        mainTime = mainTime + datetime.timedelta(hours=-1)

    # 초단기 nx, ny
    nxnyList = []

    # 원본 List
    for x in range(93, 102 + 1):
        for y in range(71, 80 + 1):
            nxnyList.append(list([x, y]))

    # # 테스트 위한 축약형
    # for x in range(93, 97 + 1):
    #     for y in range(71, 74 + 1):
    #         nxnyList.append(list([x, y]))

    # # pool 제거 이전
    # # multiprocessing test
    # pool = Pool(processes=8)
    # returnDict = dict()
    # for nxny in nxnyList:
    #     returnDict[f"{nxny[0]}_{nxny[1]}"] = []
    # pool.starmap(merge_data, zip(nxnyList, repeat(mainTime), repeat(returnDict)))
    # # print(returnDict)
    # print(len(returnDict))

    # # pool 제거 임
    # returnDict = dict()
    # for nxny in nxnyList:
    #     returnDict[f"{nxny[0]}_{nxny[1]}"] = []
    # for nxny in nxnyList:
    #     merge_data(nxny, mainTime, returnDict)

    # Thread 사용버전
    threadStart = datetime.datetime.now()
    returnDict = dict()
    threadList = []
    for nxny in nxnyList:
        time.sleep(1)
        mt = MergeThread(nxny, mainTime, returnDict)
        threadList.append(mt)
        mt.start()

    while sum([threadItem.is_alive() for threadItem in threadList]):
        time.sleep(1)
        print("not yet")

    threadEnd = datetime.datetime.now()
    print(f"소요시간 with thread : {threadEnd - threadStart}")

    # # 전처리
    # pretreatmentDataFrameList = [pd.DataFrame() for index in collect_wind.columns[1:-2]]
    # for key in returnDict.keys():
    #     print(f"key:{key}")
    #     for tempIndex in range(len(collect_wind.columns[1:-2])):
    #         ColumnIndex = tempIndex + 1
    #         columnName = collect_wind.columns[ColumnIndex]
    #         tempDF = returnDict[key]
    #
    #         concatPara: pd.DataFrame = tempDF[[f"{columnName}"]]
    #         concatPara.rename(columns={columnName: key}, inplace=True)
    #
    #         # pretreatmentDataFrameList index 0 시작 : ColumnIndex - 1
    #         pretreatmentDataFrameList[ColumnIndex - 1] = pd.concat(
    #             [pretreatmentDataFrameList[ColumnIndex - 1], concatPara], axis=1)
    #
    # for columnIndex in range(len(collect_wind.columns[1:-2])):
    #     path = Common.make_csv_path('utf-8', collect_wind.columns[columnIndex + 1], initDict, True)
    #     Common.update_csv(path, pretreatmentDataFrameList[columnIndex])

    endTime = datetime.datetime.now()
    print(f"delay total: {endTime - startTime}")


if __name__ == '__main__':
    get_wind_1st()
