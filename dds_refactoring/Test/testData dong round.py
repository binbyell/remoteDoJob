
import datetime
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import os.path
import tkinter as tk
import math
import numpy as np
import Public.Common as Common
import Test.testData as Mark_1
from DDS_GUI import gui_view_class

gu_dong: dict = {
    "기장군": ["용수리", "기장읍"],
    "금정구": ["청룡동", "부곡동", "회동동"],
    "해운대구": ["좌동", "재송동"],
    "북구": ["화명동", "덕천동"],
    "동래구": ["명장동", "온천동"],
    "연제구": ["연산동"],
    "수영구": ["광안동"],
    "강서구": ["녹산동", "대저동", "명지동", "부산신항"],
    "사상구": ["덕포동", "학장동"],
    "부산진구": ["개금동", "전포동"],
    "남구": ["대연동"],
    "동구": ["수정동", "부산북항", "초량동"],
    "사하구": ["당리동", "장림동"],
    "서구": ["대신동"],
    "중구": ["광복동"],
    "영도구": ["청학동", "태종대"]
}


def per_gu():
    root = "C:/aduck/미세먼지 - 에어코리아/data"
    for gu in gu_dong.keys():
        print(gu)
        DF_gu = pd.DataFrame()

        for dong in gu_dong[gu]:
            fileName = f"{root}/recent 3m f/busan_dust_{dong}_f.csv"
            DF_gu = pd.concat([DF_gu, pd.read_csv(fileName)], axis=0)

        dfMean = DF_gu.groupby(['dataTime']).mean()

        dfPM = dfMean[["PM10", "PM25"]].round(0)
        dfPM = dfPM.fillna(-1)
        dfPM = dfPM.astype(int)
        dfPM = dfPM.replace(-1, np.nan)

        dfSO2 = dfMean[["SO2"]].round(3)
        dfCO = dfMean[["CO"]].round(1)
        dfO3 = dfMean[["O3"]].round(3)
        dfNO2 = dfMean[["NO2"]].round(3)

        dfRound = pd.concat([dfPM, dfSO2, dfCO, dfO3, dfNO2], axis=1)

        guPath = f"{root}/구단위 평균 과거/{gu}_avr.csv"
        dfRound.to_csv(guPath)


def dust_return_round(df):
    dfPM = df[["PM10", "PM25"]].round(0)
    dfPM = dfPM.fillna(-1)
    dfPM = dfPM.astype(int)
    dfPM = dfPM.replace(-1, np.nan)
    dfSO2 = df[["SO2"]].round(3)
    dfCO = df[["CO"]].round(1)
    dfO3 = df[["O3"]].round(3)
    dfNO2 = df[["NO2"]].round(3)
    dfRound = pd.concat([dfPM, dfSO2, dfCO, dfO3, dfNO2], axis=1)

    return dfRound


def gu_avr(gu):
    root = "C:/aduck/미세먼지 - 에어코리아/data"
    print(gu)
    gu_df = pd.read_csv(f"C:/aduck/미세먼지 - 에어코리아/data/구단위 전체 최근/{gu}_recent.csv")

    start_data_time = gu_df['dataTime'].values[0]
    end_data_time = gu_df['dataTime'].values[-1]
    print(f"startDT = {start_data_time}\nendDT = {end_data_time}")

    totalKinds = ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]

    row_ = [
            "PM10 length", "PM10 total", "PM10 Max", "PM10 min",
            "PM25 length", "PM25 total", "PM25 Max", "PM25 min",
            "SO2 length", "SO2 total", "SO2 Max", "SO2 min",
            "CO length", "CO total", "CO Max", "CO min",
            "O3 length", "O3 total", "O3 Max", "O3 min",
            "NO2 length", "NO2 total", "NO2 Max", "NO2 min"]

    print("============")
    tempList = [str(value[0])[:6] for value in gu_df[["dataTime"]].values]
    dfOnlyMonth = pd.DataFrame({"dataTime": tempList})

    print("test count")
    print(gu_df[(2002040000 > gu_df["dataTime"]) & (gu_df["dataTime"] > 2002030000)]["PM10"].count())

    perMonth = pd.concat([dfOnlyMonth, gu_df[["PM10", "PM25", "SO2", "CO", "O3", "NO2"]]], axis=1)

    dfLength = perMonth.groupby(['dataTime']).count()
    dfLength = dust_return_round(dfLength)
    dfLength.columns = ["PM10 length", "PM25 length", "SO2 length", "CO length", "O3 length", "NO2 length"]

    dfTotal = perMonth.groupby(['dataTime']).sum()
    dfTotal = dust_return_round(dfTotal)
    dfTotal.columns = ["PM10 total", "PM25 total", "SO2 total", "CO total", "O3 total", "NO2 total"]

    dfMax = perMonth.groupby(['dataTime']).max()
    dfMax = dust_return_round(dfMax)
    dfMax.columns = ["PM10 Max", "PM25 Max", "SO2 Max", "CO Max", "O3 Max", "NO2 Max"]

    dfMin = perMonth.groupby(['dataTime']).min()
    dfMin = dust_return_round(dfMin)
    dfMin.columns = ["PM10 min", "PM25 min", "SO2 min", "CO min", "O3 min", "NO2 min"]

    guAvrDF = pd.concat([dfLength, dfTotal, dfMax, dfMin], axis=1)
    guAvrDF = guAvrDF[row_]

    guPath = f"{root}/구단위 평균 과거/{gu}_recent_avr.csv"
    guAvrDF.to_csv(guPath)


if __name__ == '__main__':
    for gu in gu_dong.keys():
        gu_avr(gu)
    ...
