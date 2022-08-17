import urllib.request
import urllib.parse
import requests
import json
import datetime
import os.path
import csv
import pandas as pd
import Public.Common as pb
import sys
import os
from DDS_GUI import gui_view_class

# 부산신항, 초량
api_key = 'mBC9%2FHjJoI52LSesUKliiF4nYyM7PKByjnnyEL3wcYIZlJdH2yWxogBR9%2FHYt2UxbkR2rRPyZ2F%2FAn70tbYlXA%3D%3D'
dustInfoDongList = ['태종대', '연산동', '장림동', '광복동', '덕천동', '부산신항', '청학동', '좌동', '당리동', '용수리',
                    '초량동', '대신동', '온천동', '덕포동', '전포동', '녹산동', '학장동', '대연동', '기장읍', '광안동',
                    '재송동', '화명동', '부곡동', '개금동', '명장동', '청룡동', '대저동', '부산북항', '수정동', '회동동',
                    '명지동', '백령도']
DongNumList = \
    ['2104066', '2113056', '2110060', '2101057', '2108058', '2112058', '2104063', '2109066', '2110055', '2131013',
     '2103053', '2102056', '2106056', '2115056', '2105083', '2112056', '2115063', '2107070', '2131011', '2114057',
     '2109064', '2108063', '2111058', '2105076', '2106063', '2111067', '2112051', '2103068', '2103056', '2111073',
     '2112059', '2332033']
# dustInfoList = ['dataTime', 'so2Value', 'coValue', 'o3Value', 'no2Value', 'pm10Value', 'pm10Value24', 'pm25Value',
#                 'pm25Value24', 'khaiValue', 'khaiGrade', 'so2Grade', 'coGrade', 'o3Grade', 'no2Grade', 'pm10Grade',
#                 'pm25Grade', 'pm10Grade1h', 'pm25Grade1h']

Columns = ['dataTime', 'so2Value', 'coValue', 'o3Value', 'no2Value', 'pm10Value', 'pm25Value']

initDict: pb.InitDict


def get_url(station_name, num_of_rows=1):
    # 시간단위 데이터 몇개 가져올지
    numOfRows = num_of_rows
    # 한글 인코딩
    encode = urllib.parse.quote_plus(station_name)

    url = f'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?serviceKey={api_key}&' \
          f'numOfRows={numOfRows}&pageNo=1&stationName={encode}&dataTerm=MONTH&ver=1.3&returnType=json'
    print(url)
    return url


def get_item(json_data_str):
    json_data = json.loads(json_data_str)
    return json_data["response"]["body"]["items"]


# 한시간치 데이터 List로 return
def json_to_list(json_list):
    itemList = ['' for _ in range(len(Columns))]
    for i in range(len(itemList)):
        # dustInfoList : json key list
        json_item = json_list[Columns[i]]
        if Columns[i] == 'dataTime':
            json_item = f"{json_item[:4]}{json_item[5:7]}{json_item[8:10]}{json_item[11:13]}"
        itemList[i] = json_item
    # "-" 수정
    for index in range(len(itemList)):
        if itemList[index] == '-' or itemList[index] == "-":
            itemList[index] = ''
    # print(f"dust_info itemList:\n{itemList}")
    # ex) dust_info itemList : ['2021120613', '0.006', '0.3', '0.028', '0.024', '27', '10']
    return itemList


# 1. list_index, dong을 받음
# 2. 해당 list_index, dong의 데이터를 csv로 저장.
# 3. 전처리를 위한 DataFrameList를 return
def call_dust_url(list_index, dong):
    global initDict
    dong_name = dustInfoDongList[list_index]

    # path
    dust_path = pb.make_csv_path(pb.Tag.encoding, dong, initDict, False)

    # call csv last index
    csv_last_index = pb.call_csv_last_index(dust_path, delta_time="hours")
    csv_last_index_datetime = pb.change_YMDH_to_datetime(csv_last_index)
    datetimeNow = datetime.datetime.now()
    timeNow = int(datetimeNow.strftime('%Y%m%d%H'))
    print(f"datetimeNow:{datetimeNow}")
    print(f"csv_last_index_datetime:{csv_last_index_datetime}")
    if int(datetimeNow.strftime('%M')) < 15:
        timeNow -= 1
        datetimeNow -= datetime.timedelta(hours=1)

    try:
        if datetimeNow > csv_last_index_datetime:
            print(f"(datetimeNow - csv_last_index_datetime) : {datetimeNow - csv_last_index_datetime}")
            print(f"(datetimeNow - csv_last_index_datetime).seconds : {(datetimeNow - csv_last_index_datetime).seconds}")
            url_num_of_rows = int((datetimeNow - csv_last_index_datetime).seconds / (60 * 60))
        else:
            url_num_of_rows = 0
    except TypeError:
        url_num_of_rows = 1
    print(f"url_num_of_rows : {url_num_of_rows}")

    if url_num_of_rows < 1:
        print("you don't need to get dust data. It has been less than an hour since the last dust data collection.")
        return dust_path

    url = get_url(dong_name, url_num_of_rows)

    responseText = pb.url_to_response_text(url)
    # response.status_code != 200
    if type(responseText) == int:
        print(f"response.status_code:{responseText}")
    dust_json = get_item(responseText)

    dustHourList = json_to_list(dust_json[0])

    dustHoursList = [json_to_list(result_json) for result_json in dust_json]
    print(f"dust_hours_list:\n{dustHoursList}")

    dustHoursDF = pd.DataFrame()
    # list_index, dong의 데이터를 csv로 저장.
    for dustHourList in dustHoursList:
        dustHourDF = pb.list_data_to_data_frame_data(dustHourList, Columns)
        dustHoursDF = pd.concat([dustHourDF, dustHoursDF], axis=0)
    print(f"dustHourDF:\n{dustHoursDF}")

    print(f"dust_path:{dust_path}")
    pb.update_csv(dust_path, dustHoursDF)

    return dust_path


def get_dust():
    global initDict
    initDict = pb.InitDict(pb.Tag.dust)

    # 빈 리스트 생성
    dustInfoDataFrameList = [pd.DataFrame() for _ in range(len(Columns) - 1)]
    csvPathList = []
    for index_list in range(1):#range(len(dustInfoDongList))
        # url 호출은 동 이름으로
        dong = dustInfoDongList[index_list]
        try:
            # call_dust_url:
            # 1. list_index, dong을 받음
            # 2. 해당 list_index, dong의 데이터를 csv로 저장.
            # 3. 저장된 csv의 path를 return
            csvPath = call_dust_url(list_index=index_list, dong=dong)
            csvPathList.append(csvPath)

        # 예외 로그 txt로 저장
        except Exception as e:
            # 시간
            now = datetime.datetime.now()
            this_month = now.strftime('%Y%m')
            this_day = now.strftime('%Y%m%d')
            path = initDict.FolderPath
            path_log = f"{path}/log/{this_month}"
            path_log_txt = f"{path_log}/{this_day}_{dong}.txt"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            pb.care_exception(e, path_log, path_log_txt)

    print(csvPathList)
    # for column in Columns[1:]:
    #     for csv_path in csvPathList:
    #         tempDF = pd.read_csv(csv_path, header=0, index_col=0)
    #         # print(f"{column} : \n{tempDF[column]}")

    # treatmentPathList = [pb.make_csv_path(encoding=pb.Tag.encoding, item=item, init_dict=initDict, is_pretreatment=True)
    #                      for item in Columns[1:]]
    # for csv_path in :
    #     tempDF = pd.read_csv(csvPathList[0], header=0, index_col=0)
    #     for treatmentPath in treatmentPathList:


if __name__ == '__main__':
    get_dust()
