import datetime
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time
import os.path
import tkinter as tk


def geturl(page_no):
    link = "https://apis.data.go.kr/6260000/CrossTrafficVolumeService/getCrossTrafficVolumeList"
    key = "mBC9%2FHjJoI52LSesUKliiF4nYyM7PKByjnnyEL3wcYIZlJdH2yWxogBR9%2FHYt2UxbkR2rRPyZ2F%2FAn70tbYlXA%3D%3D"
    url = f"{link}?serviceKey={key}&pageNo={page_no}&numOfRows=1000&resultType=xml&CLCT_DT=201809051205"
    return url


def test():
    totalCount = 31697
    totalList = []
    pageNo = 1
    while pageNo*1000 < totalCount + 1000:
        print(pageNo)

        url = geturl(pageNo)
        headers = {'content-type': 'application/json;charset=utf-8'}
        response = requests.get(url, headers=headers, verify=False)
        root = ET.fromstring(response.text)
        tempList = [j.text for j in root.iter('IXR_NM')]  # 교차로
        printList = list(set(tempList))
        print(f"total : {totalList}")
        print(printList)
        totalList = totalList + printList
        totalList = list(set(totalList))

        pageNo += 1

    print(totalList)
    print("=====")
    print(list(set(totalList)))


if __name__ == '__main__':
    head_list = []

    test()
