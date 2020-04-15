import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('data/comments.csv', index_col=0, low_memory=False)
df = df[['Height (cm)', 'Weight (kg)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)']]
n = 1000
i = 0
new_df = pd.DataFrame(columns=df.columns.values)
j = -1
while i < n:
    j += 1
    try:
        tmp = df.iloc[j].apply(lambda x: int(x))
        new_df = new_df.append(tmp, ignore_index = True)
    except:
        continue
    i += 1

# extract each element
height = new_df.loc[:n,'Height (cm)']
weight = new_df.loc[:n,'Weight (kg)']
bust = new_df.loc[:n, 'Bust (cm)']
waist = new_df.loc[:n, 'Waist (cm)']
hip = new_df.loc[:n, 'Hips (cm)']

# mean normalization
m = n + 1
height = (height - np.sum(height) / m) / np.std(height)
weight = (weight - np.sum(weight) / m) / np.std(weight)
bust = (bust - np.sum(bust) / m) / np.std(bust)
waist = (waist - np.sum(waist) / m) / np.std(waist)
hip = (hip - np.sum(hip) / m) / np.std(hip)

height = height.astype(np.float64)
weight = weight.astype(np.float64)
bust = bust.astype(np.float64)
waist = waist.astype(np.float64)
hip = hip.astype(np.float64)

# svd
x = np.array([height, weight, bust, waist, hip]).transpose()
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

#p2: clustering
#p2: distribution of star ratings
#p2: correlation of different features w/ star rating
#p3: try sentiment analysis on the reviews
#p4: how many items each member reviews (so we can normalize by their baseline rating)

