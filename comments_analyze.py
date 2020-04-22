import pandas as pd
import numpy as np
import re
import random
import matplotlib.pyplot as plt

def parse_bra(bra):
    bra_dict = {"AA": 0, "A": 1, "B": 2, "C": 3, "D": 4,"DD": 5, "E": 5, "DDD": 6, "F": 6, "DDDD": 7, "G": 7, "H": 8, "I": 9, "J": 10, "K": 11}
    bra_sizes = re.findall(r"[^\W\d_]+|\d+",bra)
    band_size = int(bra_sizes[0])
    if bra_sizes[1] in bra_dict:
        return band_size, bra_dict[bra_sizes[1]]
    elif band_size > 50:
        return None, None
    else:
        return None, None

df = pd.read_csv('data/comments.csv', index_col=0, low_memory=False)
print(df.columns)
df = df[['Height (cm)', 'Weight (kg)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)', 'Bra']]
n = 1000
i = 0
j = -1
new_df = pd.DataFrame(columns=df.columns.values)

while i < n:
    j += 1
    try:
        tmp = df.iloc[j][['Height (cm)', 'Weight (kg)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)']].apply(lambda x: int(x))
        band_size, cup_size = parse_bra(df.iloc[j]['Bra'])
        if band_size is None:
            raise Exception('bra size is bad')
        tmp['Cup Size'] = cup_size
        tmp['Band Size'] = band_size
        new_df = new_df.append(tmp, ignore_index = True)
    except:
        continue
    i += 1

###### PCA ######
# extract each element
height = new_df.loc[:n,'Height (cm)']
weight = new_df.loc[:n,'Weight (kg)']
bust = new_df.loc[:n, 'Bust (cm)']
waist = new_df.loc[:n, 'Waist (cm)']
hip = new_df.loc[:n, 'Hips (cm)']
band_size = new_df.loc[:n, 'Band Size']
cup_size = new_df.loc[:n, 'Cup Size']

# mean normalization
m = n + 1
height = (height - np.sum(height) / m) / np.std(height)
weight = (weight - np.sum(weight) / m) / np.std(weight)
bust = (bust - np.sum(bust) / m) / np.std(bust)
waist = (waist - np.sum(waist) / m) / np.std(waist)
hip = (hip - np.sum(hip) / m) / np.std(hip)
band_size = (band_size - np.sum(band_size) / m) / np.std(band_size)
cup_size = (cup_size - np.sum(cup_size) / m) / np.std(cup_size)

height = height.astype(np.float64)
weight = weight.astype(np.float64)
bust = bust.astype(np.float64)
waist = waist.astype(np.float64)
hip = hip.astype(np.float64)
band_size = band_size.astype(np.float64)
cup_size = cup_size.astype(np.float64)

# svd
x = np.array([height, weight, bust, waist, hip, band_size, cup_size]).transpose()
sigma = np.dot(x.T,x)
u, s, vh = np.linalg.svd(sigma, full_matrices=True)
u1 = u[:,:2]
z = np.dot(x,u1)
x_approx = np.dot(u1, z.T).T
z1 = z[:,0]
z2 = z[:,1]

plt.plot(z1, z2, 'ro')
plt.show()

u2 = u[:,:3]
z = np.dot(x, u2)
x_approx_2 = np.dot(u2, z.T).T
z1 = z[:,0]
z2 = z[:,1]
z3 = z[:,2]

ax = plt.axes(projection='3d')
ax.plot3D(z1, z2, z3, 'bo')
plt.show()

num = 0
num_2 = 0
denom = 0
for i in range(n):
    num += np.linalg.norm(x[i] - x_approx[i]) ** 2
    num_2 += np.linalg.norm(x[i] - x_approx_2[i]) ** 2
    denom += np.linalg.norm(x[i]) ** 2
variance = num/denom
percent = 100*(1 - variance)
percent_2 = 100*(1 - num_2/denom)
print("{}% variance retained for k = 2".format(percent))
print("{}% variance retained for k = 3".format(percent_2))
# PCA seems to not be the best in this situation since variance retained for k = 2 is around 61% and k = 3 is around 73%

###### Clustering ######
def find_nearest(clusters, ex):
    min = np.linalg.norm(clusters - ex, axis = 1)
    ind = np.where(min == min.min())
    if len(ind[0]) == 1:
        return ind[0] + 1
    # some clusters initially start at the same value so this splits between two equally
    return random.choice(ind[0]) + 1

x = pd.DataFrame(data=x, columns=['Height (cm)', 'Weight (kg)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)', 'Band Size', 'Cup Size'])
k_error = []
for k in range(1, x.shape[1] + 1):
    clusters = x.sample(n = k)
    clusters = clusters.reset_index(drop=True)
    error = 0
    while(True):
        c = np.zeros(x.shape[0], dtype=int)
        inner_sum = 0
        for i in range(x.shape[0]):
            c[i] = find_nearest(clusters, x.iloc[i])
            inner_sum += np.linalg.norm(x.iloc[i] - clusters.iloc[c[i] - 1]) ** 2
        for i in range(k):
            clusters.loc[i] = np.mean(x[c == i+1])
        m = x.shape[0]
        j = 1/m * inner_sum
        if np.abs(j - error) > 0.01:
            error = j
        else:
            error = j
            break
    k_error.append(error)

# plot clustering error
print("error for k from 1 - 7", k_error)
x_k = np.linspace(1, len(k_error), len(k_error))
plt.plot(x_k, k_error)
plt.show()

#p2: clustering
#p2: distribution of star ratings
#p2: correlation of different features w/ star rating
#p3: try sentiment analysis on the reviews
#p4: how many items each member reviews (so we can normalize by their baseline rating)
