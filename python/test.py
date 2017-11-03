


demandPrices = "34,23,54,123,543,54233,"

dp = ['' for i in range(0,6)]
ip = [0 for i in range(0,6)]
i = 0

for t in range(0,6):
    while (demandPrices[i] != ','):
        dp[t] =  dp[t] + demandPrices[i]
        i = i + 1
    i = i + 1
    ip[t] = int(dp[t])
print(ip)
