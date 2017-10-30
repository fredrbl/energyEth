
import main
import match
import random


# 10 minute trading
# 7000 wh pr day on average -> dev on 2000 wh +- -> 2000/24*6 = 14! YESS
# 13500 wh in battery -> 13500/2 = 6700
# 5000-7000 w

# price is 47 cent/kwh =>0,047 cent/wh => 47 millicent/wh
# calculamos en millicent/wh

def day():

    battery = [6700, 0, 6700, 0, 6700, 0] #starting at 50 SOC. given we have 6 batteries

    for i in range(5): #144

        ### Setting the deviations to the houses with batteries
        ## We assume that the batteries always can fix it here
        battery[0] = battery[0] + random.randint(-50, 50)
        battery[2] = battery[2] + random.randint(-1000, 50)
        battery[4] = battery[4] + random.randint(-50, 1000)

        ### Now, we must set the price based on the battery status
        price = setPrice(battery)

        ### Set the available flexibility in each battery
        availableFlex = setFlexibility(battery)

        ### The trading happens, and the batteries are corrected for the trading
        battery = main.trading(price, battery, availableFlex)


    return True

def setPrice(battery):
    # One battery have randomised price, the two others have a somewhat smart algorithm
    price = [[0 for x in range(6)] for y in range(2)]
    price[0][0] = random.randint(48, 59)
    price[1][0] = random.randint(35, 46)
    for i in range(2, 6, 2): # could show graph over the logic of the pricing
        if (battery[i] <= 6700):
            price[0][i] = int(round(48 + battery[i] * 0.00164))
            price[1][i] = int(round(46 - battery[i] * 0.00164))
        else:
            price[0][i] = int(round(70 - battery[i] * 0.00164))
            price[1][i] = int(round(24 + battery[i] * 0.00164))
    return price

def setFlexibility(battery):
    # 5000 w in one hour = 5000 wh => 833 w max in 10 minutes
    availableFlex = [[0 for x in range(6)] for y in range(2)]
    for i in range(0,6,2):
        if (battery[i] > 840 and battery[i] < 12500):
            availableFlex[0][i] = 700
            availableFlex[1][i] = 700
        elif (battery[i] <= 840):
            availableFlex[0][i] = 0
            availableFlex[1][i] = 700
        elif (battery[i] >= 12500):
            availableFlex[0][i] = 700
            availableFlex[1][i] = 0
    return availableFlex
