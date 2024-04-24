import pandas as pd
import numpy as np
data = pd.read_csv('data_cleaned_1 (2).csv')

print(data['category'].unique())
print('\n')
print(data['sub_category'].unique())

prod = np.array(data['category'].unique())
print('\n')
print(prod[[[0]]])

print('\n')
print('\n')

print()

for box in prod:
    print(box)