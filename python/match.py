

def matching(flexFlag, transactions, demand, supply):
    i = 0
    j = 0
    # If demand is smallest -> transfer all, set to 0, and go to next down node.
    while (len(demand[0]) > i and len(supply[0]) > j and flexFlag != 2):

        if (demand[1][i] == 0): i = i + 1
        elif (supply[1][j] == 0): j = j + 1

        elif (demand[1][i] <= supply[1][j]):  # If down node is smaller, transfer all
            transactions[0].append(supply[0][j])
            transactions[1].append(demand[0][i])
            transactions[2].append(demand[1][i])
            supply[1][j] = supply[1][j] - demand[1][i]
            demand[1][i] = 0
            i = i + 1

        # If supply is smallest -> transfer all, set to 0, and go to next up node.
        else:
            transactions[0].append(supply[0][j])
            transactions[1].append(demand[0][i])
            transactions[2].append(supply[1][j])
            demand[1][i] = demand[1][i] - supply[1][j]
            supply[1][j] = 0
            j = j + 1
    # The restEnergy must be traded with flexibility options
    # The restEnergy must now be shortened. From i or j, to end of counter.

    matchingResult = [[] for y in range(2)]
    if (len(demand[0]) == i):  #If supply is bigger than demand=>flexflag=UP
        flexFlag = 0
        for j in range(j, len(supply[0])):
            matchingResult[0].append(supply[0][j])
            matchingResult[1].append(supply[1][j])

    elif (len(supply[0]) == j):
        flexFlag = 1
        for i in range(i, len(demand[0])):
            matchingResult[0].append(demand[0][i])
            matchingResult[1].append(demand[1][i])

    return flexFlag, transactions, matchingResult
