import requests
import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import urllib3
import glob

from pandas import DataFrame
from time import sleep


def call_weather_api(start_date, end_date):
    # API 키는 공개하기 힘든 점 양해 바랍니다.
    # api_key = open("./raw_data/weather_api").readlines()[0].strip()
    api_key = 'Ae9m5RKSiv7oQTVPmqKWH5BdM8aVGt6yGRwIV1Wh34zFQJF5R/NkR92v2Z0DQixg'
    url_format = 'https://data.kma.go.kr/apiData/getData?type=json&dataCd=ASOS&dateCd=HR&startDt={date}&startHh=00&endDt={date}&endHh=23&stnIds={snt_id}&schListCnt=100&pageIndex=1&apiKey={api_key}'

    headers = {'content-type': 'application/json;charset=utf-8'}
    urllib3.disable_warnings()

    for date in pd.date_range(start_date, end_date).strftime("%Y%m%d"):
        print("%s Weather" % date)
        url = url_format.format(api_key=api_key, date=date, snt_id="159")
        print(f"url : {url}")
        response = requests.get(url, headers=headers, verify=False)

        # 200 (정상)의 경우에만 파일 생성
        print(response.status_code)
        if response.status_code == 200:
            result = pd.DataFrame(response.json()[-1]["info"])
            print(result.head())

            folderPath = r'./busan_weather_dataset/2021'
            if not os.path.isdir(folderPath):
                os.makedirs(folderPath)

            print("group by TM")

            print(result.set_index('TM'))

            result.to_csv("./busan_weather_dataset/2021/weather_%s.csv" % date, index=False, encoding="utf-8-sig")
            # result.to_csv("./busan_weather_dataset/weather_%s.csv" % date,
            #              columns=['TM','STN_ID','TS','DC10_LMCS_CA','DC10_TCA','PS','PA','TD','PV','HM','WD','WS','TA'],
            #              index=False, encoding="utf-8-sig")
            # result.to_csv("./busan_weather_dataset/weather_%s.csv" % date, index=False, encoding="utf-8")

            # API 부하 관리를 위해 0.5초 정도 쉬어 줍시다 (찡긋)
            sleep(1.5)

    # csv 파일 합치기
    # input_file = r'C:\Users\MK\Anaconda3\envs\tensorflow\busan_weather_dataset\2018'
    # output_file = r'C:\Users\MK\Anaconda3\envs\tensorflow\busan_weather_dataset\csv_concat\busan_weather_dataset_2018.csv'

    # allFile_list = glob.glob(os.path.join(input_file, 'weather_*'))
    # print(allFile_list)
    # allData = []
    # for file in allFile_list:
    #    df = pd.read_csv(file)
    #    allData.append(df)

    # dataCombine = pd.concat(allData, axis=0, ignore_index=True)
    # dataCombine.to_csv(output_file, index=False, encoding="utf-8-sig")


def concate_data_csv():
    # csv 파일 합치기
    input_file = r'C:\Users\MK\Anaconda3\envs\tensorflow\busan_weather_dataset\2021'
    output_file = r'C:\Users\MK\Anaconda3\envs\tensorflow\busan_weather_dataset\csv_concat\busan_weather_dataset_202107.csv'

    allFile_list = glob.glob(os.path.join(input_file, 'weather_*'))
    print(allFile_list)
    allData = []
    for file in allFile_list:
        df = pd.read_csv(file)
        allData.append(df)

    dataCombine = pd.concat(allData, axis=0, ignore_index=True)
    dataCombine.to_csv(output_file, index=False, encoding="utf-8-sig")


if __name__ == '__main__':
    #     call_api("getAirQualityInfoClassifiedByStation", "2021-05-12", "2021-05-13", "gijang")
    #     busan_call_api("getAirQualityInfoClassifiedByStation", "2021-05-12", "2021-05-13", "gijang")
    #     busan_call_api("getAirQualityInfoClassifiedByStation", "2021-06-20", "2021-06-23", "busan_dust_dataset")
    call_weather_api("2022-06-25", "2022-06-30")
#     call_wind_api("getWindInfo", "20200623")
#     concat_data()
#     concate_data_csv()
# describe_dust_data()
