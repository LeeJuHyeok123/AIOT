import numpy as np

ftemp = [63, 73, 80, 86, 84, 78, 72, 68, 65, 62]

F = np.array(ftemp)
print(F)
C = (F - 32) * 5 / 9
print(C)

import matplotlib.pyplot as plt
plt.plot(F, marker='o')
plt.show()