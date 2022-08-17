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
import Public.Common as pb
import collect.collect_dust as collect_dust
import urllib.request
import urllib.parse


initDict: pb.InitDict


# return jsonStringList
def get_data_list(station_name, pageNo=1):
    global initDict
    # 한글 인코딩
    encode = urllib.parse.quote_plus(station_name)
    numOfRows = 48

    # (1일: DAILY, 1개월: MONTH, 3개월: 3MONTH)
    url = f'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?serviceKey={pb.api_key}&'\
          f'numOfRows={numOfRows}&pageNo={pageNo}&stationName={encode}&dataTerm=MONTH&ver=1.3&returnType=json'

    dataListList: list = []

    print(f"get data list url:\n{url}")
    # try:
    responseText = pb.url_to_response_text(url)
    dustJsonList = collect_dust.get_item(responseText)
    for dustJson in dustJsonList:
        temp = collect_dust.json_to_list(dustJson)
        dataListList.append(temp)
    #     ...
    # except Exception as e:
    #     ...
    # dataListList : [['dataTime', 'so2Value', 'coValue', 'o3Value', 'no2Value', 'pm10Value', 'pm25Value'] x n]
    dataListList.reverse()

    if initDict.NumberOfCollect * 24 > pageNo * numOfRows:
        time.sleep(4)
        print(f"{station_name} - {pageNo}")
        return get_data_list(station_name, pageNo+1) + dataListList

    return dataListList


# 입력 dongName, returnDict
# dongName 해당 data csv 저장, returnDict[dongName]에 저장
def merge_data(dong, return_dict: dict):
    global initDict

    startTime = datetime.datetime.now()

    listDataList = get_data_list(dong)
    dataFrameData = pb.list_data_list_to_df(listDataList, collect_dust.Columns)
    path = pb.make_csv_path(pb.Tag.encoding, dong, initDict, False)
    pb.update_csv(path, dataFrameData, need_recent=False)

    endTime = datetime.datetime.now()
    print(f"path: {path}")
    print(f"delay dong : {endTime - startTime}")
    key = collect_dust.DongNumList[collect_dust.dustInfoDongList.index(dong)]
    return_dict[key] = dataFrameData


class MergeThread(threading.Thread):
    def __init__(self, dong, return_dict):
        threading.Thread.__init__(self)
        self.nxny = dong
        self.return_dict = return_dict

    def run(self):
        merge_data(self.nxny, self.return_dict)


def get_dust_1st():
    global initDict
    initDict = pb.InitDict(pb.Tag.dust)
    # 시간 채크
    startTime = datetime.datetime.now()

    dongNameList = collect_dust.dustInfoDongList

    # returnDict 내용물 : DataFrame
    returnDict = dict()
    threadList = []

    # thread mode
    for dong in dongNameList:
        print(f"\n-----{dong}-----")
        time.sleep(1)
        mt = MergeThread(dong, returnDict)
        threadList.append(mt)
        mt.start()

    while sum([threadItem.is_alive() for threadItem in threadList]):
        time.sleep(1)
        print("not yet")
    # thread mode end

    # # loop mode
    # for dong in dongNameList:
    #     print(f"\n-----{dong}-----")
    #     merge_data(dong, returnDict)
    # # loop mode end

    # merge_data("수정동", returnDict)

    endTime = datetime.datetime.now()
    print(f"delay total: {endTime - startTime}")

    # # Pretreatment
    # pretreatmentDataFrameList = [pd.DataFrame() for index in collect_dust.Columns[1:]]
    # for key in returnDict.keys():
    #     print(f"key : {key}")
    #     for tempIndex in range(len(collect_dust.Columns[1:])):
    #         ColumnIndex = tempIndex + 1
    #         columnName = collect_dust.Columns[ColumnIndex]
    #         tempDF = returnDict[key]
    #
    #         concatPara: pd.DataFrame = tempDF[[f"{columnName}"]]
    #         concatPara.rename(columns={columnName: key}, inplace=True)
    #
    #         # pretreatmentDataFrameList index 0 시작 : ColumnIndex - 1
    #         pretreatmentDataFrameList[ColumnIndex - 1] = pd.concat([pretreatmentDataFrameList[ColumnIndex - 1], concatPara], axis=1)
    #
    # for columnIndex in range(len(collect_dust.Columns[1:])):
    #     path = pb.make_csv_path(pb.Tag.encoding, collect_dust.Columns[columnIndex+1], initDict, True)
    #     pb.update_csv(path, pretreatmentDataFrameList[columnIndex], need_recent=False)
    # # Pretreatment End


if __name__ == '__main__':
    get_dust_1st()
