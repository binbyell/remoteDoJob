
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
from DDS_GUI import gui_view_class

# year = 2003
# quarter = 4

# ~ 2013년 2.5 x 분기 o
# 14년~ 2.5 o
# 14, 15, 16년 csv
# 17년 월
# 18년 분기
# 19년 월
# 20년 월

dustInfoDongList = ['태종대', '연산동', '장림동', '광복동', '덕천동', '부산신항', '청학동', '좌동', '당리동', '용수리',
                    '초량동', '대신동', '온천동', '덕포동', '전포동', '녹산동', '학장동', '대연동', '기장읍', '광안동',
                    '재송동', '화명동', '부곡동', '개금동', '명장동', '청룡동', '대저동', '부산북항', '수정동', '회동동',
                    '명지동', '백령도']


def read_xlsx(year, quarter):

    root_path = "C:/aduck/미세먼지 - 에어코리아"
    local_path = f"/{year}"
    # 2001년01분기
    data_name = f"/{year}년0{quarter}분기.xlsx"
    file_path = root_path + local_path + data_name

    print(f"check time 1 : {datetime.datetime.now()}")
    a = pd.read_excel(io=file_path, engine='openpyxl') # , sheet_name='Data'
    print(f"check time 2 : {datetime.datetime.now()}")
    df_busan = a.loc[a['측정소명'].isin(dustInfoDongList)]

    print(df_busan)

    busan_result = df_busan[["측정일시", "측정소명", "PM10", "SO2", "CO", "O3", "NO2"]]
    make_csv(f"{year}_quarter_{quarter}_25x", busan_result, root_path)

    print(f"check time 3 : {datetime.datetime.now()}")


def read_4_4():
    year_4 = 2004
    quarter_4 = 4

    root_path = "C:/aduck/미세먼지 - 에어코리아"
    local_path = f"/{year_4}"
    # 2001년01분기
    data_name = f"/{year_4}년0{quarter_4}분기.xlsx"
    file_path = root_path + local_path + data_name

    print(f"check time 1 : {datetime.datetime.now()}")
    a = pd.read_excel(io=file_path, engine='openpyxl') # , sheet_name='Data'
    print(f"check time 2 : {datetime.datetime.now()}")
    df_busan = a.loc[a['측정소명'].isin(dustInfoDongList)]

    print(df_busan)

    busan_result = df_busan[["DATA_TINE", "측정소명", "PM10", "SO2", "CO", "O3", "NO2"]]
    make_csv(f"{year_4}_quarter_{quarter_4}_25x", busan_result, root_path)

    print(f"check time 3 : {datetime.datetime.now()}")


def make_csv(name, data: pd.DataFrame, root_path):
    folder = "/data"
    path = f"{root_path}{folder}/{name}.csv"
    print(f"path:{path}")
    data.to_csv(path, index=False, encoding='euc-kr')


def merge_quarter():
    root_path = "C:/aduck/미세먼지 - 에어코리아"
    local_path = f"/data"
    temp = pd.DataFrame()
    month_year_list = [2018]
    for year in month_year_list:
        for quarter in range(1, 4+1):
            print(f"{year} - {quarter}")
            data_name = f"/{year}_quarter_{quarter}_25x.csv"
            file_path = root_path + local_path + data_name

            # 병합
            readPathDF = pd.read_csv(file_path, index_col=0, encoding='euc-kr')
            temp = pd.concat([temp, readPathDF], axis=0)

            # 정렬
            temp = temp.sort_index()

            # 저장
            merge_path = f"{root_path}{local_path}/merge/{year}_merge.csv"
            temp.to_csv(merge_path, index_label='dataTime', encoding='euc-kr')
        temp = pd.DataFrame()
    ...


def split_dong():
    for year in range(2001, 2022):
        path = f"C:/aduck/미세먼지 - 에어코리아/data/merge/{year}_merge.csv"
        rootDF = pd.read_csv(path, index_col=0, encoding='euc-kr')

        # 폴더 없으면 생성
        folderPath = f"C:/aduck/미세먼지 - 에어코리아/data/dong"
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        for dong in dustInfoDongList:
            print(f"{year} - {dong}")
            try:
                df_dong = rootDF.loc[rootDF['측정소명'] == dong]
                if year < 2014:
                    df_dong_without = df_dong[["PM10", "SO2", "CO", "O3", "NO2"]]
                else:
                    df_dong_without = df_dong[["PM10", "PM25", "SO2", "CO", "O3", "NO2"]]
                dong_path = f"{folderPath}/busan_dust_weather_{dong}_{year}.csv"
                df_dong_without.to_csv(dong_path, index_label='dataTime')
            except Exception as e:
                print(e)
                print(f"{dong} is not here")
                continue


def merge_year():
    folderPath = f"C:/aduck/미세먼지 - 에어코리아/data/dong_m"
    if not os.path.isdir(folderPath):
        os.makedirs(folderPath)
    for dong in dustInfoDongList:
        tempDF = pd.DataFrame()

        for year in range(2001, 2022):
            print(f"{dong} - {year}")
            filePath = f"C:/aduck/미세먼지 - 에어코리아/data/dong/busan_dust_weather_{dong}_{year}.csv"
            readDF = pd.read_csv(filePath, index_col=0)
            tempDF = pd.concat([tempDF, readDF], axis=0)

            mergePath = f"{folderPath}/busan_dust_{dong}.csv"

            if year == 2021:
                tempDF = tempDF[["PM10", "PM25", "SO2", "CO", "O3", "NO2"]]
                tempDF.to_csv(mergePath, index_label='dataTime')


def refactored():
    for dong in dustInfoDongList:
        file_path = f"C:/aduck/미세먼지 - 에어코리아/data/dong_m/busan_dust_{dong}.csv"
        path_DF = pd.read_csv(file_path)

        print(dong)

        dataTimeToChange = []
        for index in path_DF['dataTime']:
            if type(index) is int:
                dataTimeToChange.append(index)
                continue

            try:
                int(index)
                dataTimeToChange.append(int(index))
                # print("change to int")

            except Exception as e:
                # print(e)
                temp_index = index.strip()
                index_split = temp_index.split()
                temp_index = f"{index_split[0]}{index_split[1]}"
                index_split = temp_index.split('-')
                temp_index = f"{index_split[0]}{index_split[1]}{index_split[2]}"
                # print(f"dong : {dong}, index : {temp_index}")
                dataTimeToChange.append(int(temp_index))

        path_DF['dataTime'] = dataTimeToChange

        if not os.path.isdir("C:/aduck/미세먼지 - 에어코리아/data/dong_c"):
            os.makedirs("C:/aduck/미세먼지 - 에어코리아/data/dong_c")

        index_changed_path = f"C:/aduck/미세먼지 - 에어코리아/data/dong_c/busan_dust_{dong}.csv"
        path_DF.to_csv(index_changed_path, index=False)
        # print("saved")
    ...


def month_to_str(month_: int):
    if month_ < 10:
        return f"0{month_}"
    else:
        return f"{month_}"


def length_total_max_min(dong):
    df = pd.read_csv(f"C:/aduck/미세먼지 - 에어코리아/data/dong_c/busan_dust_{dong}.csv")
    # df.columns = ['dataTime', 'SO2', 'CO', 'O3', 'NO2', 'PM10', 'PM25']
    # df = df[["dataTime", "PM10", "PM25", "SO2", "CO", "O3", "NO2"]]
    # recent_change_path = f"C:/aduck/미세먼지 - 에어코리아/data/recent 3m c/busan_dust_{dong}_202204.csv"
    # df.to_csv(f"{recent_change_path}", index=False)
    start_data_time = df['dataTime'].values[0]
    end_data_time = df['dataTime'].values[-1]
    print(f"startDT = {start_data_time}\nendDT = {end_data_time}")

    totalKinds = ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]

    row_ = ["dataTime",
            "PM10 length", "PM10 total", "PM10 Max", "PM10 min",
            "PM25 length", "PM25 total", "PM25 Max", "PM25 min",
            "SO2 length", "SO2 total", "SO2 Max", "SO2 min",
            "CO length", "CO total", "CO Max", "CO min",
            "O3 length", "O3 total", "O3 Max", "O3 min",
            "NO2 length", "NO2 total", "NO2 Max", "NO2 min"]

    month_count = 0

    piece_year = int(str(start_data_time)[:4])
    piece_month = int(str(start_data_time)[4:6])
    piece_ym = int(f"{piece_year}{month_to_str(piece_month)}0000")

    while end_data_time > piece_ym:

        print(f"piece_ym : {piece_ym}")

        text = f"{piece_year}{month_to_str(piece_month)}0000"
        textP = f"{piece_year}{month_to_str(piece_month + 1)}0000"

        temp: pd.DataFrame = df.loc[(df['dataTime'] >= int(text)) & (df['dataTime'] <= int(textP))]
        print(f"temp:\n{temp}")

        aa = pd.DataFrame(columns=row_)
        print(f"aa:\n{aa}")

        dataRow = [int(f"{piece_year}{month_to_str(piece_month)}")]

        for kinds in totalKinds:
            length = 0
            total = 0
            Max = 0
            min = 9000
            for value in temp[kinds].values:
                # 걸러내기
                if not value or math.isnan(value):
                    continue
                if value < -90:
                    continue

                if value > Max:
                    Max = value
                if value < min:
                    min = value
                length += 1
                total += value

            if Max == 0:
                Max = None
            if min == 9000:
                min = None
            if length == 0:
                length = None
            if total == 0:
                total = None
            dataRow.extend([length, total, Max, min])

        aa.loc[month_count] = dataRow
        folderPath = f"C:/aduck/미세먼지 - 에어코리아/data/ltmm"
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        try:
            pinDF = pd.read_csv(f"{folderPath}/{dong}.csv")
            DF = pd.concat([pinDF, aa], axis=0)
            DF.to_csv(f"{folderPath}/{dong}.csv", index=False)
            print(f"DF:\n{DF}")
        except FileNotFoundError:
            aa.to_csv(f"{folderPath}/{dong}.csv", index=False)

        # 초기화
        month_count += 1
        piece_month += 1

        if piece_month == 13:
            piece_year += 1
            piece_month = 1

        piece_ym = int(f"{piece_year}{month_to_str(piece_month)}0000")


def to_find_date_start_and_end():
    sortList = ['개금동', '광복동', '광안동', '기장읍', '녹산동', '당리동', '대신동', '대연동', '대저동', '덕천동',
                '덕포동', '명장동', '명지동', '백령도', '부곡동', '부산북항', '부산신항', '수정동', '연산동', '온천동',
                '용수리', '장림동', '재송동', '전포동', '좌동', '청룡동', '청학동', '초량동', '태종대', '학장동',
                '화명동', '회동동']

    for dong in sortList:
        df = pd.read_csv(f"C:/aduck/미세먼지 - 에어코리아/data/dong_c/busan_dust_{dong}.csv")
        start_data_time = df['dataTime'].values[0]
        end_data_time = df['dataTime'].values[-1]

        print(f"{dong}\nstart:{start_data_time}\nend:{end_data_time}")


def null_filter():
    sortList = ['개금동', '광복동', '광안동', '기장읍', '녹산동', '당리동', '대신동', '대연동', '대저동', '덕천동',
                '덕포동', '명장동', '명지동', '부곡동', '부산북항', '부산신항', '수정동', '연산동', '온천동', '용수리',
                '장림동', '재송동', '전포동', '좌동', '청룡동', '청학동', '초량동', '태종대', '학장동', '화명동',
                '회동동', '백령도']
    totalKinds = ["dataTime", "PM10", "PM25", "SO2", "CO", "O3", "NO2"]

    for dong_ in sortList:
        print(dong_)
        dongPath = f"C:/aduck/미세먼지 - 에어코리아/data/recent 3m c/busan_dust_{dong_}_202204.csv"
        temp = pd.read_csv(dongPath)

        dongDF = pd.DataFrame()
        for kinds in totalKinds:
            kindsValueList = []
            for value in temp[kinds].values:
                # 걸러내기
                if not value or math.isnan(value):
                    kindsValueList.append(None)
                    continue
                if value < -90:
                    kindsValueList.append(None)
                    continue
                kindsValueList.append(value)
            kindsDF = pd.DataFrame({kinds: kindsValueList})
            dongDF = pd.concat([dongDF, kindsDF], axis=1)
            # print(f"dong:{dong_}, kinds:{kinds}\nkindsDF:\n{kindsDF}")
        print(f"dong:{dong_}\ndongDF:\n{dongDF}")

        folderPath = f"C:/aduck/미세먼지 - 에어코리아/data/recent 3m f"
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        filePath = f"{folderPath}/busan_dust_{dong_}_f.csv"
        dongDF.to_csv(filePath, index=False)


def busan_mean():
    sortList = ['개금동', '광복동', '광안동', '기장읍', '녹산동', '당리동', '대신동', '대연동', '대저동', '덕천동',
                '덕포동', '명장동', '명지동', '부곡동', '부산북항', '부산신항', '수정동', '연산동', '온천동', '용수리',
                '장림동', '재송동', '전포동', '좌동', '청룡동', '청학동', '초량동', '태종대', '학장동', '화명동',
                '회동동']
    busanDF = pd.DataFrame()
    for dong_ in sortList:
        fileName = f"C:/aduck/미세먼지 - 에어코리아/data/recent 3m c/busan_dust_{dong_}_202204.csv"
        print(fileName)
        fileDF = pd.read_csv(fileName)
        busanDF = pd.concat([busanDF, fileDF], axis=0)
    busanDF = busanDF.groupby(['dataTime']).mean()

    folderPath = f"C:/aduck/미세먼지 - 에어코리아/data/busan_recent_c"
    if not os.path.isdir(folderPath):
        os.makedirs(folderPath)

    busanPath = f"C:/aduck/미세먼지 - 에어코리아/data/busan_recent_c/busan.csv"
    busanDF.to_csv(busanPath)
    ...


def busan_length_total_max_min():
    rootPath = "C:/aduck/미세먼지 - 에어코리아/data/busan_recent_c"
    df = pd.read_csv(f"{rootPath}/busan.csv")

    start_data_time = df['dataTime'].values[0]
    end_data_time = df['dataTime'].values[-1]
    print(f"startDT = {start_data_time}\nendDT = {end_data_time}")

    totalKinds = ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]

    row_ = ["dataTime",
            "PM10 length", "PM10 total", "PM10 Max", "PM10 min",
            "PM25 length", "PM25 total", "PM25 Max", "PM25 min",
            "SO2 length", "SO2 total", "SO2 Max", "SO2 min",
            "CO length", "CO total", "CO Max", "CO min",
            "O3 length", "O3 total", "O3 Max", "O3 min",
            "NO2 length", "NO2 total", "NO2 Max", "NO2 min"]

    month_count = 0

    piece_year = int(str(start_data_time)[:4])
    piece_month = int(str(start_data_time)[4:6])
    piece_ym = int(f"{piece_year}{month_to_str(piece_month)}0000")

    while end_data_time > piece_ym:

        print(f"piece_ym : {piece_ym}")

        text = f"{piece_year}{month_to_str(piece_month)}0000"
        textP = f"{piece_year}{month_to_str(piece_month + 1)}0000"

        temp: pd.DataFrame = df.loc[(df['dataTime'] >= int(text)) & (df['dataTime'] <= int(textP))]
        print(f"temp:\n{temp}")

        aa = pd.DataFrame(columns=row_)
        print(f"aa:\n{aa}")

        dataRow = [int(f"{piece_year}{month_to_str(piece_month)}")]

        for kinds in totalKinds:
            length = 0
            total = 0
            Max = 0
            min = 9000
            for value in temp[kinds].values:
                # 걸러내기
                if not value or math.isnan(value):
                    continue
                if value < -90:
                    continue

                if value > Max:
                    Max = value
                if value < min:
                    min = value
                length += 1
                total += value

            if Max == 0:
                Max = None
            if min == 9000:
                min = None
            if length == 0:
                length = None
            if total == 0:
                total = None
            dataRow.extend([length, total, Max, min])

        aa.loc[month_count] = dataRow
        folderPath = f"{rootPath}/ltmm"
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)

        try:
            pinDF = pd.read_csv(f"{folderPath}/busan_ltmm.csv")
            DF = pd.concat([pinDF, aa], axis=0)
            DF.to_csv(f"{folderPath}/busan_ltmm.csv", index=False)
            print(f"DF:\n{DF}")
        except FileNotFoundError:
            aa.to_csv(f"{folderPath}/busan_ltmm.csv", index=False)

        # 초기화
        month_count += 1
        piece_month += 1

        if piece_month == 13:
            piece_year += 1
            piece_month = 1

        piece_ym = int(f"{piece_year}{month_to_str(piece_month)}0000")


def get_round():
    rootPath = "C:/aduck/미세먼지 - 에어코리아/data/busan_recent_c"
    df = pd.read_csv(f"{rootPath}/busan_recent.csv")
    col_list = ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]

    dfDT = df[["dataTime"]]

    dfPM = df[["PM10", "PM25"]].round(0)
    dfPM = dfPM.fillna(-1)
    dfPM = dfPM.astype(int)
    dfPM = dfPM.replace(-1, np.nan)

    dfSO2 = df[["SO2"]].round(3)
    dfCO = df[["CO"]].round(1)
    dfO3 = df[["O3"]].round(3)
    dfNO2 = df[["NO2"]].round(3)

    dfRound = pd.concat([dfDT, dfPM, dfSO2, dfCO, dfO3, dfNO2], axis=1)
    print(dfRound)
    dfRound.to_csv(f"{rootPath}/busan_recent_round.csv", index=False)


def csv_data_round():
    sortList = ['개금동', '광복동', '광안동', '기장읍', '녹산동', '당리동', '대신동', '대연동', '대저동', '덕천동',
                '덕포동', '명장동', '명지동', '부곡동', '부산북항', '부산신항', '수정동', '연산동', '온천동', '용수리',
                '장림동', '재송동', '전포동', '좌동', '청룡동', '청학동', '초량동', '태종대', '학장동', '화명동',
                '회동동', '백령도']
    rootPath = "C:/aduck/미세먼지 - 에어코리아/data/recent 3m f"
    for dong in sortList:
        print(dong)
        fileName = f"busan_dust_{dong}_f.csv"
        filePath = f"{rootPath}/{fileName}"

        df = pd.read_csv(filePath)

        dfDT = df[["dataTime"]].astype(int)

        dfPM = df[["PM10", "PM25"]].round(0)
        dfPM = dfPM.fillna(-1)
        dfPM = dfPM.astype(int)
        dfPM = dfPM.replace(-1, np.nan)

        dfSO2 = df[["SO2"]].round(3)
        dfCO = df[["CO"]].round(1)
        dfO3 = df[["O3"]].round(3)
        dfNO2 = df[["NO2"]].round(3)

        dfRound = pd.concat([dfDT, dfPM, dfSO2, dfCO, dfO3, dfNO2], axis=1)
        dfRound.to_csv(f"{rootPath}/busan_recent_round.csv", index=False)

        folderPath = "C:/aduck/미세먼지 - 에어코리아/data/dong_f_newly_round"
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)
        fileName = f"busan_dust_{dong}_all_newly.csv"
        roundFilePath = f"{folderPath}/{fileName}"

        dfRound.to_csv(roundFilePath, index=False)


def csv_ltmm_data_round(dong: str = "개금동"):
    sortList = ['개금동', '광복동', '광안동', '기장읍', '녹산동', '당리동', '대신동', '대연동', '대저동', '덕천동',
                '덕포동', '명장동', '명지동', '부곡동', '부산북항', '부산신항', '수정동', '연산동', '온천동', '용수리',
                '장림동', '재송동', '전포동', '좌동', '청룡동', '청학동', '초량동', '태종대', '학장동', '화명동',
                '회동동', '백령도']
    rootPath = "C:/aduck/미세먼지 - 에어코리아/data/busan_c/ltmm"

    print(dong)
    fileName = f"busan_ltmm.csv"
    filePath = f"{rootPath}/{fileName}"

    df = pd.read_csv(filePath)

    dfDT = df[["dataTime"]].astype(int)

    dfPM = df[["PM10 length", "PM10 total", "PM10 Max", "PM10 min",
               "PM25 length", "PM25 total", "PM25 Max", "PM25 min"]].round(0)
    dfPM = dfPM.fillna(-1)
    dfPM = dfPM.astype(int)
    dfPM = dfPM.replace(-1, np.nan)

    dfSO2 = df[["SO2 length", "SO2 total", "SO2 Max", "SO2 min"]].round(3)
    dfCO = df[["CO length", "CO total", "CO Max", "CO min"]].round(1)
    dfO3 = df[["O3 length", "O3 total", "O3 Max", "O3 min"]].round(3)
    dfNO2 = df[["NO2 length", "NO2 total", "NO2 Max", "NO2 min"]].round(3)

    dfRound = pd.concat([dfDT, dfPM, dfSO2, dfCO, dfO3, dfNO2], axis=1)

    folderPath = "C:/aduck/미세먼지 - 에어코리아/data/busan_round"
    if not os.path.isdir(folderPath):
        os.makedirs(folderPath)
    fileName = f"busan_dust_avr.csv"
    roundFilePath = f"{folderPath}/{fileName}"

    dfRound.to_csv(roundFilePath, index=False)


if __name__ == '__main__':
    csv_ltmm_data_round()
    ...
