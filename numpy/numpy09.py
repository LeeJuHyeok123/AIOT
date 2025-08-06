import matplotlib.pyplot as plt
import numpy as np

numbers = np.random.normal(size=1000)
plt.hist(numbers, bins=30, density=True, alpha=0.5, color='g', edgecolor='black')
plt.title('Normal Distribution Histogram')
plt.xlabel('Value')
plt.ylabel('Density')
plt.grid(True)
plt.show()
