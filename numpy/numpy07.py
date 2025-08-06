import numpy as np
import time 

rand1 = np.random.seed(int(time.time()))  # Set seed for reproducibility
randNumbers = np.random.randint(1, 100, size=10)
print("랜덤 숫자:", randNumbers)
randNumbersTwoDim = np.random.randint(1, 100, size=(3, 4))
print("랜덤 2차원 숫자:\n", randNumbersTwoDim)
randNumbersThreeDim = np.random.randint(1, 100, size=(2, 3, 4))
print("랜덤 3차원 숫자:\n", randNumbersThreeDim)
randNumbersNormal = np.random.normal(0, 1, size=10)
print("정규 분포 랜덤 숫자:", randNumbersNormal)
