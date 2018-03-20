import numpy as np
import matplotlib.pyplot as plt
import random

# This script is used to plot interesting results of the real time trading
def realTimePlot(flexCoinBalance, battery, price, deviation, marketPrice):
    # Show development of costs, deviations, battery and marketprice. Use 4 random nodes -> First one graph with two non battery, and then two with

    ###### FlexCoinBalance of node 2 and 4 #########
    flex = plt.figure(1)
    FlexCoinBalance2 = np.asarray([i[2] for i in flexCoinBalance])
    FlexCoinBalance8 = np.asarray([i[6] for i in flexCoinBalance])
    x = np.arange(0, 20, 1)
    y1 = FlexCoinBalance2[x]
    y2 = FlexCoinBalance8[x]
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.xlabel("Time step")
    plt.ylabel("FlexCoinBalance")
    plt.plot(x, y1, x, y2, 'o-')
    flex.show()

    ###### BatteryBalance of node 2 and 8 #########
    p = plt.figure(2)
    battery2 = np.asarray([i[2] for i in battery])
    battery8 = np.asarray([i[6] for i in battery])
    x = np.arange(0, 20, 1)
    y1 = battery2[x]
    y2 = battery8[x]
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.xlabel("Time step")
    plt.ylabel("Battery level")
    plt.plot(x, y1, x, y2, 'o-')
    p.show()

    ###### marketPrice development #########
    price = plt.figure(3)
    marketPrice = np.asarray(marketPrice)
    x = np.arange(0, 20, 1)
    y = marketPrice[x]
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.xlabel("Time step")
    plt.ylabel("Market price")
    plt.plot(x, y, 'o-')
    price.show()

    ###### Accumulated profit of node 2 and 8 #########
    ### Profit = diff flexCoinBalance + diff battery * wholesalePrice
    profitFig = plt.figure(4)
    profit2 = [0 for x in range(len(flexCoinBalance))]
    profit8 = [0 for x in range(len(flexCoinBalance))]
    accProfit2 = [0 for x in range(len(flexCoinBalance))]
    accProfit8 = [0 for x in range(len(flexCoinBalance))]
    for i in range(1, len(flexCoinBalance)):
        profit2[i] = np.array(flexCoinBalance[i][2]) - np.array(flexCoinBalance[i - 1][2]) + (470 * (np.array(battery[i][2]) - np.array(battery[i - 1][2])))
        accProfit2[i] = profit2[i] + accProfit2[i - 1]
        profit8[i] = np.array(flexCoinBalance[i][6]) - np.array(flexCoinBalance[i - 1][6]) + (470 * (np.array(battery[i][6]) - np.array(battery[i - 1][6])))
        accProfit8[i] = profit8[i] + accProfit8[i - 1]
    profit2 = np.asarray(profit2)
    profit8 = np.asarray(profit8)
    x = np.arange(0, 20, 1)
    y1 = profit2[x]
    y2 = profit8[x]
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.xlabel("Time step")
    plt.ylabel("Profit")
    plt.plot(x, y1, x, y2, 'o-')
    profitFig.show()

    accProfitFig = plt.figure(5)
    accProfit2 = np.asarray(accProfit2)
    accProfit8 = np.asarray(accProfit8)
    x = np.arange(0, 20, 1)
    y1 = accProfit2[x]
    y2 = accProfit8[x]
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.xlabel("Time step")
    plt.ylabel("Accumulated Profit")
    plt.plot(x, y1, x, y2, 'o-')
    accProfitFig.show()
