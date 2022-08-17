
import datetime
import pandas as pd
import numpy as np


def read_xlsx(file_name):

    # MB : 북항
    # MK : 감천
    # MS : 신항

    tempList = ['MB', 'MK', 'MS']

    # read file
    folderPath = "C:/HGteck/dds/미세먼지 소스/선박/2016"
    file_path = f"{folderPath}/{file_name}"
    print(f"file_path:{file_path}")

    print(f"check time 1 : {datetime.datetime.now()}")
    b = pd.read_excel(
        io=file_path,
        usecols=[8,11, 12, 19],
        header=11,
        dtype={'항명': str,
               '호출부호': str},
    )

    inputTon = b[["입항일시", "계선장소", "총톤수"]]
    inputTon.columns = ['date', 'dock', 'ton']
    outputTon = b[["출항일시", "계선장소", "총톤수"]]
    outputTon.columns = ['date', 'dock', 'ton']

    df_busan = pd.concat([inputTon, outputTon], axis=0)
    del b, inputTon, outputTon
    print(f"df_busan:\n{df_busan}")

    # 시간 데이터 날리기
    df_busan['date'] = df_busan['date'].str.split(' ').str[0]

    # date convert YYYY-MM-DD to YYYYMMDD
    df_busan['date'] = df_busan['date'].str.replace('-', '')

    # drop other dock
    df_busan = df_busan.loc[df_busan['dock'].str[:2].isin(tempList)]

    # get data only in selected year
    df_busan = df_busan.loc[df_busan['date'].astype(int) >= 20160101]
    df_busan = df_busan.loc[df_busan['date'].astype(int) <= 20161231]

    # convert dock to read easy
    df_busan['dock'] = df_busan.loc[:, 'dock'].str[:2]

    tempDF = pd.DataFrame()
    for dock in tempList:
        # get only in MB - 감천항
        df_dock = df_busan.loc[df_busan['dock'] == dock][['date', 'ton']]
        df_dock["ton"] = df_dock["ton"].str.replace(',', '')

        # null 처리
        df_dock = df_dock.fillna(0)
        df_dock.columns = ['date', 'ton']

        df_dock['ton'] = df_dock['ton'].astype(int)
        print(f"df_dock : \n{df_dock}")

        df_dock_ton: pd.DataFrame = df_dock.groupby(['date']).sum()

        df_dock_count: pd.DataFrame = df_dock.groupby(['date']).count()
        df_dock_count.columns = ['count']

        temp = pd.concat([df_dock_ton, df_dock_count], axis=1)
        temp.columns = [f'ton_{dock}', f'count_{dock}']

        tempDF = pd.concat([tempDF, temp], axis=1)

    fileN = f"2016-1_csv.csv"
    fileP = f"{folderPath}/{fileN}"
    tempDF.to_csv(fileP)
    print(f"temp : \n{tempDF}")
    print(f"path : {fileP}")


if __name__ == '__main__':
    read_xlsx("2016-1.xls")
    ...
