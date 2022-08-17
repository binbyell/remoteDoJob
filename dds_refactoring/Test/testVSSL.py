
import datetime
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import os.path
import tkinter as tk

import Public.Common as pb
from DDS_GUI import gui_view_class

api_key = 'mBC9%2FHjJoI52LSesUKliiF4nYyM7PKByjnnyEL3wcYIZlJdH2yWxogBR9%2FHYt2UxbkR2rRPyZ2F%2FAn70tbYlXA%3D%3D'
params = '&pageNo=1&numOfRows=29'

# RootPath = './data'
# Attach = 'vssl'
# AttachPath = f'{RootPath}/{Attach}'
# CollectType = 'vssl'
# NumberOfCollectDay = 2
# MB = 0.5196178778573866
# MK = 0.1741157739110656
# MS = 0.3062663482315478
initDict: pb.InitDict


def make_csv_path(encording, item, month, isPretreatment:bool):
    global AttachPath
    global CollectType
    if isPretreatment:
        csvPath = f"{AttachPath}/{CollectType}_{encording}_Pretreatment_{item}_{month}.csv"
    else:
        csvPath = f"{AttachPath}/{CollectType}_{encording}_{item}_{month}.csv"
    return csvPath


def geturl(day_string: str, num_of_rows=50, page_number=1, prt_ag_cd='020'):
    url = f'http://apis.data.go.kr/1192000/CntlVssl2/Info?serviceKey={api_key}&pageNo={page_number}&' \
          f'numOfRows={num_of_rows}&prtAgCd={prt_ag_cd}&sde={day_string}&ede={day_string}&clsgn=&'
    print(url)
    return url


def day_zero(now_string):
    tempList = [int(now_string)*100 + 1+a for a in range(24)]
    vList = [0 for _ in range(len(tempList))]
    k = pd.DataFrame({'cntrlOpertDt': tempList, 'total': vList, 'MB_t': vList, 'MK_t': vList, 'MS_t': vList,
                      'MB_c': vList, 'MK_c': vList, 'MS_c': vList})
    return k


def get_data_frame(now_string: str, count=0):
    global initDict

    _numOfRows = 50
    _pageNumber = 1 + count
    _prtAgCd = '020'

    url = geturl(now_string, _numOfRows, _pageNumber, _prtAgCd)

    headers = {'content-type': 'application/json;charset=utf-8'}
    response = requests.get(url, headers=headers, verify=False)
    root = ET.fromstring(response.text)
    totalCount = [j.text for j in root.iter('totalCount')]
    # print(f"totalCount: \n{totalCount}")
    initDict.write_text(f"totalCount: \n{totalCount}")

    prtAgCd = [j.text for j in root.iter('prtAgCd')]  # 항구청 코드
    prtAgNm = [j.text for j in root.iter('prtAgNm')]  # 항만명
    vsslGrtg = [j.text for j in root.iter('vsslGrtg')]  # 선박총톤수
    cntrlOpertDt = [j.text for j in root.iter('cntrlOpertDt')]  # 기항지입항일시
    details = [j for j in root.iter('details')]  # details
    fcltyCd = [j.text for j in root.iter('fcltyCd')]  # 입항위치

    cntrlNm = [j.text for j in root.iter('cntrlNm')]

    tails = [[a for a in j.findall('detail')] for j in root.iter('details')]
    detail = [j for j in root.iter('detail')]  # detail

    prtAgCd.reverse()
    prtAgNm.reverse()
    vsslGrtg.reverse()
    cntrlOpertDt.reverse()
    details.reverse()
    fcltyCd.reverse()
    print(f"vsslGrtg : {[str(value) for value in vsslGrtg]}")
    print(f"fcltyCd : {[str(value) for value in fcltyCd]}")
    print(f"details : {details}")
    print(f"ajiaji : {[value.findall('detail') for value in details]}")
    # print(f"details : {[[v.find('fcltyCd').text[:2] for v in value.findall('detail')] for value in details]}")
    # details_test = [[v.find('fcltyCd').text[:2] for v in value.findall('detail')] for value in details]

    details_test = []
    for v in fcltyCd:
        if v:
            details_test.append(v[:2])
    print(f"details_test : {details_test}")
    # details_test = [value[:2] for value in fcltyCd]

    print(f"tails : {tails}")
    print(f"detail : {detail}")

    tail_ton = []
    for index in range(len(tails)):
        for n in range(len(tails[index])):
            tail_ton.append(vsslGrtg[index])
    print(f"tail_ton : {tail_ton}")
    print(f"len\ntails:{len(tails)}\ndetail:{len(detail)}\ntail_ton:{len(tail_ton)}")

    for index in range(len(cntrlOpertDt)):
        dayAndHour = cntrlOpertDt[index].split('T')
        day = dayAndHour[0].split('-')
        hour = dayAndHour[1].split('+')[0].split(':')
        hour[0] = str(int(hour[0]))
        if int(hour[0]) < 23:
            temp = datetime.datetime(int(day[0]), int(day[1]), int(day[2]), int(hour[0]) + 1)
            cntrlOpertDt[index] = f"{temp.strftime('%Y%m%d%H')}"
        else:
            temp = datetime.datetime(int(day[0]), int(day[1]), int(day[2]), int(hour[0]))
            cntrlOpertDt[index] = f"{int(temp.strftime('%Y%m%d%H'))+1}"

    totalList = []
    MB_T_List = [0.0 for _ in cntrlOpertDt]
    MB_C_List = [0 for _ in cntrlOpertDt]
    MK_T_List = [0.0 for _ in cntrlOpertDt]
    MK_C_List = [0 for _ in cntrlOpertDt]
    MS_T_List = [0.0 for _ in cntrlOpertDt]
    MS_C_List = [0 for _ in cntrlOpertDt]
    for index in range(len(cntrlOpertDt)):
        at_same_time = 0
        if '출항' == cntrlNm[index]:
            # print(cntrlNm[index])
            continue
        if 'MB' == details_test[index]:
            MB_T_List[index] = MB_T_List[index] + float(tail_ton[index])
            MB_C_List[index] += 1
            at_same_time += 1

        if 'MK' == details_test[index]:
            MK_T_List[index] = MK_T_List[index] + float(tail_ton[index])
            MK_C_List[index] += 1
            at_same_time += 1

        if 'MS' == details_test[index]:
            MS_T_List[index] = MS_T_List[index] + float(tail_ton[index])
            MS_C_List[index] += 1
            at_same_time += 1
        if at_same_time >= 2:
            print(f"at_same_time : {at_same_time}")
            print(f"same time index : {index}")

    # # 입항위치 정리
    # for index in range(len(details)):
    #     details[index] = [j.text for j in details[index].iter('fcltyCd')][0]

    result = pd.concat([pd.DataFrame({'cntrlOpertDt': cntrlOpertDt}),
                        pd.DataFrame({'total': tail_ton}),
                        pd.DataFrame({'MB_t': MB_T_List}),
                        pd.DataFrame({'MK_t': MK_T_List}),
                        pd.DataFrame({'MS_t': MS_T_List}),
                        pd.DataFrame({'MB_c': MB_C_List}),
                        pd.DataFrame({'MK_c': MK_C_List}),
                        pd.DataFrame({'MS_c': MS_C_List}),
                        ], axis=1)

    dayZero = day_zero(now_string)
    result = pd.concat([result, dayZero], axis=0)

    time.sleep(1)

    if int(totalCount[0]) > 50+(count*50):
        # print(f"count:{count+1}")
        print(f"count:{count+1}")
        return pd.concat((result, get_data_frame(now_string, count + 1)), axis=0)
    return result
    # for i in range(int(totalCount[0]) // _numOfRows):
    #     print(i)


def create_folder(path):
    if not (os.path.isdir(path)):
        os.makedirs(os.path.join(path))
        # print(f"path created \n{path}")
        initDict.write_text(f"path created \n{path}")
    else:
        # print(f"path exist\n{path}")
        initDict.write_text(f"path exist\n{path}")


def get_vssl(collect_day: datetime.datetime):
    global initDict
    # +datetime.timedelta(days=-1)
    nowString = collect_day.strftime('%Y%m%d')
    encoding = pb.Tag.encoding
    pathFolder = initDict.FolderPath
    pathFile = f'{pathFolder}/vssl_temp.csv'
    pathThisDay = f'{pathFolder}/{initDict.CollectType}_thisDay.csv'
    pathMonth = pb.make_csv_path(encoding=encoding, item='', init_dict=initDict, is_pretreatment=False)

    ####
    df = get_data_frame(nowString)

    create_folder(pathFolder)

    df.to_csv(pathFile, index=False, encoding=encoding, index_label="dataTime")

    df = pd.read_csv(pathFile, header=0, index_col=0, encoding=encoding)

    # print(countingDict)
    thisDayDf = df.groupby(['cntrlOpertDt']).sum()
    # thisDayDf = thisDayDf.drop(['prtAgCd'], axis=1)
    thisDayDf.index.name = 'dataTime'

    # print(f"test:{thisDayDf}")
    print(f"test:{thisDayDf}")

    if os.path.isfile(pathThisDay):
        yesterDayDf = pd.read_csv(pathThisDay, header=0, index_col=0, encoding=encoding)
        if yesterDayDf.index[0] != thisDayDf.index[0]:
            # 월 data에 병합 후 update
            pb.update_csv(pathMonth, yesterDayDf)
            # if os.path.isfile(pathMonth):
            #     monthData = pd.read_csv(pathMonth, header=0, index_col=0, encoding=encoding)
            #     monthData = pd.concat([monthData, yesterDayDf], axis=0)
            #     monthData.to_csv(pathMonth, encoding=encoding, index_label="dataTime")
            # else:
            #     yesterDayDf.to_csv(pathMonth, encoding=encoding, index_label="dataTime")
    thisDayDf.to_csv(f"{pathThisDay}", encoding=encoding, index_label="dataTime")
    # pb.update_csv(pathThisDay, thisDayDf)
    # print(pathFile)
    print(pathFile)


def get_vssl_with_check_1st(frame_form: gui_view_class.FrameForm = None):
    global initDict
    initDict = pb.InitDict(pb.Tag.vssl, frame_form)

    dateEnd = pb.change_YMDH_to_datetime("2016042700")
    dateStart = pb.change_YMDH_to_datetime("2016010100")

    # print(f"check : {initDict.Attach}")
    # frame_form.thisText.insert(tk.END, f"check : {initDict.Attach}")
    initDict.write_text(f"check : {initDict.Attach}")
    # print(f"checkRoot : {initDict.RootPath}")
    encoding = pb.Tag.encoding
    pathMonth = pb.make_csv_path(encoding=encoding, item='', init_dict=initDict, is_pretreatment=False)

    file_exist = os.path.isfile(pathMonth)
    if not file_exist:
        for deltaDay in range(initDict.NumberOfCollect):
            get_vssl(dateEnd + datetime.timedelta(days=-(initDict.NumberOfCollect - deltaDay)))
    get_vssl(dateEnd)


if __name__ == '__main__':
    # get_vssl(datetime.datetime.now())
    get_vssl_with_check_1st()
