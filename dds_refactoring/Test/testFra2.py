import scipy.fft
import matplotlib.pyplot as plt
import numpy as np


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

    y_f = scipy.fft.fft(vL)
    x_f = tL

    plt.plot(x_f, 2.0 / N * np.abs(y_f[:N // 2]))
    plt.show()
    ...


if __name__ == '__main__':
    read_csv()
    # N = 500
    # T = 1.0 / 600.0
    # x = np.linspace(0.0, N*T, N)
    # print(f"x:{x}")
    # y = np.sin(60.0 * 2.0*np.pi*x) + 0.5*np.sin(90.0 * 2.0*np.pi*x)
    # print(f"y:{y}")
    # y_f = scipy.fft.fft(y)
    # x_f = np.linspace(0.0, 1.0/(2.0*T), N//2)
    #
    # print(f"y_f : {y_f}")
    # print(f"x_f : {x_f}")
    #
    # plt.plot(x_f, 2.0/N * np.abs(y_f[:N//2]))
    # plt.show()
