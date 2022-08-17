import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def read_xlsx():
    root_path = "C:/aduck/고장진단"
    data_name = "test_20-09-10_1208"

    data_path = f"{root_path}/{data_name}.xlsx"

    a = pd.read_excel(io=data_path, engine='openpyxl', sheet_name='제목없음')
    print(a)
    b = a[["Time", "메인벨브현재값PV(bar)"]]
    b.columns = ["Time", "Value"]

    print(b)

    data_name_b = f"{data_name}_b.csv"
    path_b = f"{root_path}/{data_name_b}"
    b.to_csv(path_b, index=False)


def read_csv():
    root_path = "C:/aduck/고장진단"
    data_name_b = "test_20-09-10_1108_b"
    path_b = f"{root_path}/{data_name_b}.csv"

    a = pd.read_csv(path_b)
    print(a)

    timeList = []
    pin = 0
    print(f"pin : {pin}")

    for index in range(len(a["Time"].values)):
        timeList.append(pin)
        pin += 1

    valueList = a["Value"].values

    delConstant = [v - 300 for v in valueList]
    telConstant = [v/100 for v in timeList]

    n = 100000
    tL = telConstant[n:n+1000]
    vL = delConstant[n:n+1000]
    # valueList[n:n+1000]

    fft = np.fft.fft(vL) / len(vL)

    fft_magnitude = abs(fft)
    print(f"fft_magnitude:\n{fft_magnitude}")

    plt.subplot(2, 1, 1)
    plt.plot(tL, vL)
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.stem(fft_magnitude)
    # plt.ylim(0, 2.5)
    plt.grid()
    plt.show()
    ...


if __name__ == '__main__':
    read_csv()

    # fs = 100
    # t = np.arange(0, 3, 1 / fs)
    # f1 = 35
    # f2 = 10
    # signal = 0.6 * np.sin(2 * np.pi * f1 * t) + 3 * np.cos(2 * np.pi * f2 * t + np.pi / 2)
    #
    # # print(t)
    # # print(signal)
    #
    # fft = np.fft.fft(signal) / len(signal)
    #
    # print(f"t:\n{t}")
    # fft_magnitude = abs(fft)
    # print(fft_magnitude)
    #
    # plt.subplot(2, 1, 1)
    # plt.plot(t, signal)
    # plt.grid()
    #
    # plt.subplot(2, 1, 2)
    # plt.stem(fft_magnitude)
    # plt.ylim(0, 2.5)
    # plt.grid()
    # plt.show()
    ...
