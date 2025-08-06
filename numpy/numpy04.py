import numpy as np

heights = [150, 160, 170, 180, 175, 165, 155, 145, 140, 135]
weigths = [50, 60, 70, 80, 75, 65, 55, 45, 40, 35]  

np_heights = np.array(heights)
np_weights = np.array(weigths)

bmi = np_weights / (np_heights / 100) ** 2
print("Heights:", np_heights)
print("Weights:", np_weights)       
print("BMI:", bmi)
import matplotlib.pyplot as plt     
plt.scatter(np_heights, np_weights, c=bmi, cmap='viridis', s=100)
plt.colorbar(label='BMI')   
plt.title('Height vs Weight with BMI')
plt.xlabel('Height (cm)')       
plt.ylabel('Weight (kg)')
plt.grid(True)
plt.show()  
    

