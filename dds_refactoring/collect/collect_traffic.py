import csv
from collections import defaultdict
import pandas as pd
import os.path
import datetime
import requests
import json
import time
import Public.Common as Common
import xml.etree.ElementTree as ET


initDict: Common.InitDict


dict_id_to_name = {
    "ECE2000E14": "busanUlsanHighway",
    "HRS0100E14": "Hwangnyeong", "HRE0100E14": "Hwangnyeong", "DSS0631E16": "Hwangnyeong", "DSE0161E16": "Hwangnyeong",
    "ECE2200E14": "Hwangnyeong", "ECE2100E14": "Hwangnyeong",
    "DSS0401B14": "Gaegeum", "DSE0400B14": "Gaegeum",
    "BYS0300B14": "Suyeong", "BYE0200B14": "Suyeong",
    "KBS0100B14": "Guseo",
    "DSE0700B14": "Gamjeon", "DSE0801O14": "Gamjeon", "DSS0201I14": "Gamjeon",
    "BYS0100B14": "Oryun", "BYE0100B18": "Oryun", "BYE0101B14": "Oryun", "BYE0101B18": "Oryun", "BYS0101B14": "Oryun",
    "JAS0100E14": "Namsan", "JAE0100E14": "Namsan",
    "DSS0100B14": "Nakdong",
    "BYE0100B14": "Munhyeon", "BYS0400B14": "Munhyeon", "BYS0401O14": "Munhyeon", "DSS0661O16": "Munhyeon",
    "BYE0101I14": "Munhyeon", "DSE0131I16": "Munhyeon",
    "DSS0700B14": "Uam", "DSE0100B14": "Uam",
    "BYE0100I20": "Hoedong", "BYE0120I20": "Hoedong", "BYE0110I20": "Hoedong",
    "ECE0600E14": "Buwon",
    "DSS0501O14": "Jinyang", "DSE0301I14": "Jinyang",
    "BYE0200O18": "Mangmi",
    "DSS0301I14": "Hakjang", "DSE0601O14": "Hakjang",
    "DSS0351I16": "Jurye", "DSE0501O14": "Jurye",
    "ECE1900E14": "Bukbugeumsok",
    "ECE1200E14": "Gadeok", "ECS1200E14": "Gadeok",
    "ECE1000E14": "Songjeong",
    "ECE1700E14": "Jangan", "ECE1800E14": "Jangan",
    "ECE2300E14": "Daejeo", "ECE2400E14": "Daejeo",
    "ECE1400E14": "Myeongnye",
    "BYE0300O18": "Geumsa",
    "DSE0201I14": "Beomnaegol", "DSS0601O14": "Beomnaegol",
    "ECE1500E14": "Wolgwang", "ECE1600E14": "Wolgwang",
    "ECE1300E14": "Myeongji", "ECS0900I14": "Myeongji",
    "ECS0500E14": "Daedong", "ECE0500E14": "Daedong"
}

dict_name_to_xy = {
    "busanUlsanHighway": [129.180735, 35.179118],
    "Hwangnyeong": [129.07951, 35.150036],
    "Gaegeum": [129.0291, 35.15793],
    "Suyeong": [129.1099, 35.17259],
    "Guseo": [129.095482, 35.248905],
    "Gamjeon": [128.986214, 35.150109],
    "Oryun": [129.1093, 35.240931],
    "Namsan": [129.092657, 35.268323],
    "Nakdong": [128.973857, 35.152096],
    "Munhyeon": [129.067699, 35.135848],
    "Uam": [129.072071, 35.123417],
    "Hoedong": [129.123083, 35.234554],
    "Buwon": [128.889653, 35.212284],
    "Jinyang": [129.044095, 35.162405],
    "Mangmi": [129.112611, 35.177552],
    "Hakjang": [128.992571, 35.149613],
    "Jurye": [129.009533, 35.152817],
    "Bukbugeumsok": [129.1199, 35.157121],
    "Gadeok": [128.839336, 35.084874],
    "Songjeong": [128.822713, 35.097605],
    "Jangan": [129.237694, 35.320201],
    "Daejeo": [128.984508, 35.210228],
    "Myeongnye": [129.261393, 35.376089],
    "Geumsa": [129.130834, 35.236671],
    "Beomnaegol": [129.061517, 35.150596],
    "Wolgwang": [129.24037, 35.309111],
    "Myeongji": [128.932231, 35.11054],
    "Daedong": [128.993505, 35.231032]
}

toEn = ["황령", "구 개금요금소", "수영터널", "구서IC", "감전IC", "오륜터널", "남산역", "낙동IC", "문현", "우암부두", "회동분기점",
        "부원교차로", "진양IC", "망미램프", "학장IC", "주례IC", "북부금속초소", "가덕대교", "송정공원", "장안고교", "대저수문", "명례리",
        "금사램프", "범내골", "월광휴게소", "명지교차로", "대동수문", "부산울산간고속도로"]


def get_url_response(page_no=1, num_of_rows=400):
    global initDict

    url = f"http://apis.data.go.kr/6260000/TrafficVolumeService/getHourTrafficVolumeList?serviceKey={Common.api_key}" \
          f"&pageNo={page_no}&numOfRows={num_of_rows}&resultType=json&CALTIME={initDict.Now.strftime('%Y%m%d000000')}" \
          f"&CTRID=BYE0100B18"
    print(url)
    response = Common.url_to_response_text(url=url)

    return response


# use with collect first
def get_item(page_no=1, num_of_rows=400):
    global initDict
    json_data_str = get_url_response(page_no=page_no, num_of_rows=num_of_rows)

    # response.status_code != 200  서버에서 정상값 출력 못받음
    if type(json_data_str) == int:
        return json_data_str
    try:
        json_data = json.loads(json_data_str)
    except:
        print(f"except: {json_data_str}")
        return json_data_str
    result = json_data["getHourTrafficVolumeList"]["item"]

    return result


# use json list Return DataFrame
def get_data_frame_from_json_list(is_first: bool = False):
    global initDict
    # DataFrame 생성
    indexList = [(datetime.datetime.now() - datetime.timedelta(hours=a)).strftime('%Y%m%d%H')
                 for a in range(initDict.NumberOfCollect * 24)]
    # print(f"indexList : {indexList}")
    # print(f"len() : {len(indexList)}")
    print(f"before 14days : {datetime.datetime.now() - datetime.timedelta(days=14)}")
    baseDF = pd.DataFrame(columns=[key for key in dict_name_to_xy.keys()], index=indexList).fillna(0)
    pageNo = 1
    numOfRows = 400
    searchCALTIME = initDict.Now
    while searchCALTIME > initDict.Now - datetime.timedelta(days=initDict.NumberOfCollect): # days=initDict.NumberOfCollect
        print(f"pageNo : {pageNo}")
        # baseDF에 넣을 데이터 수집을 위한 api 호출
        json_list = get_item(page_no=pageNo, num_of_rows=numOfRows)

        # response.status_code != 200  서버에서 정상값 출력 못받음
        if type(json_list) == int:
            return json_list

        if len(json_list) == 0:
            print("break")
            break

        # 다음 루프를 위한 초기화
        searchCALTIME = Common.change_YMDH_to_datetime(json_list[-1]['CALTIME'][:-4])
        print(f"changed Time : {searchCALTIME}")
        pageNo += 1

        for json_data in json_list:
            '''
                    json_data EX
                    {'CTRID': 'BYE0200B14', 'CTRNAME': '수영터널(본선_원동방면)', 'CALTIME': '20220324080000', 
                    'Y': 35.172567, 'X': 129.109974, 'SUM_VOLUME': 2729}
            '''
            try:
                baseDF[dict_id_to_name[json_data['CTRID']]][json_data['CALTIME'][:-4]] = baseDF[dict_id_to_name[json_data['CTRID']]][json_data['CALTIME'][:-4]] + json_data['SUM_VOLUME']
            except KeyError:
                print("not in here.")
                break

        # do while
        if not is_first:
            baseDF = baseDF[:1]
            print(f"is_first {is_first}")
            break

    # print(f"baseDF : {baseDF}")
    return baseDF[::-1]


def get_traffic():
    global initDict
    initDict = Common.InitDict(Common.Tag.traffic)
    print(f"Number of Collect : {initDict.NumberOfCollect}")

    csv_path = Common.make_csv_path(Common.Tag.encoding, "", initDict, False)
    print(f"collectTraffic csv_path : {csv_path}")
    is_first = not Common.is_path(csv_path)
    print(f"collectTraffic is_first : {is_first}")
    df = get_data_frame_from_json_list(is_first=is_first)
    if type(df) == int:
        print(df)
    else:
        Common.update_csv(csv_path=csv_path, data=df)
    ...


if __name__ == '__main__':
    get_traffic()
    ...
