import numpy as np
import matplotlib.pyplot as plt
import time

# results is both marginal prices and total cost
nodes = range(4, 100, 10)
cost = [0 for n in range(0,100)]
for n in nodes:
## to open many accounts-> dont know. wait for response during your trip. Mientras ese, construir tu codigo
    # primero=> solo duration.
    # alternativo 2 => estimateGas() * n
    cost[n] = 50 + 2 * n
#### Plot la diferencia, y mostrar la marginal crecimiento.
node  = plt.figure(1)
cost = np.asarray(cost)
x = np.arange(4, 100, 10)
y = cost[x]
plt.xticks(np.arange(x.min(), x.max(), 10))
plt.plot(x, y, '-o')
node.show()
