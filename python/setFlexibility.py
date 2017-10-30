def setFlexibility(int deviation):

    # Set availableFlex randomly
    # I want that 10 % of the houses do not have any available flexibility at all times, because of cars.
    float upAvailableFlex = 0.41   #=>Up means that it is surplus in the market, and that the battery must buy. up is hence how much it can take in.
    float downAvailableFlex = 0.41

    if deviation < 0: #When dev<0, the house have used to little energy. The battery must hence take in some more=>up
        if (deviation - downAvailableFlex) < 0:
            downAvailableFlex = downAvailableFlex - deviation
            deviation = 0
        else
            deviation = deviation - downAvailableFlex
            downAvailableFlex = 0
    if else deviation > 0:
            upAvailableFlex = upAvailableFlex - deviation
            deviation = 0
        else
            deviation = deviation - upAvailableFlex
            upAvailableFlex = 0

return (deviation, upAvailability)
