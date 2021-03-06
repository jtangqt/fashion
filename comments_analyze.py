import pandas as pd
import numpy as np
import re
import random
import matplotlib.pyplot as plt


def parse_bra(bra):
    bra_dict = {"AA": 0, "A": 1, "B": 2, "C": 3, "D": 4, "DD": 5, "E": 5, "DDD": 6, "F": 6, "DDDD": 7, "G": 7, "H": 8,
                "I": 9, "J": 10, "K": 11}
    bra_sizes = re.findall(r"[^\W\d_]+|\d+", bra)
    band_size = int(bra_sizes[0])
    if bra_sizes[1] in bra_dict:
        return band_size, bra_dict[bra_sizes[1]]
    elif band_size > 50:
        return None, None
    else:
        return None, None


def get_fit(fit):
    # member overall fit = 1 : true to size, 2 : big, 3: small
    if fit is None:
        return None
    fit = int(fit)
    if fit == 1:
        return 0
    if fit == 2:
        return 1
    if fit == 3:
        return -1


def get_size(size):
    sizes = ["XXXS", "XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    return sizes.index(size)


def process_df(filename, n):
    df = pd.read_csv(filename, index_col=0, low_memory=False)
    print(df.head())
    j = -1
    i = 0
    new_df = pd.DataFrame(columns=df.columns.values)

    while i < n and j < df.shape[0]:
        j += 1
        try:
            tmp = df.iloc[j].copy(deep=True)
            tmp['Height (cm)'] = int(df.loc[j, "Height (cm)"])
            tmp['Weight (kg)'] = int(df.loc[j, "Weight (kg)"])
            tmp['Bust (cm)'] = int(df.loc[j, 'Bust (cm)'])
            tmp['Waist (cm)'] = int(df.loc[j, 'Waist (cm)'])
            tmp['Hips (cm)'] = int(df.loc[j, 'Hips (cm)'])
            band_size, cup_size = parse_bra(df.loc[j, 'Bra'])
            if band_size is None:
                raise Exception('bra size is bad')
            tmp['Cup Size'] = cup_size
            tmp['Band Size'] = band_size
            tmp['Fit'] = get_fit(df.loc[j, 'Fit'])
            if tmp['Fit'] is None:
                raise Exception('fit is bad')
            tmp["Size"] = get_size(df.loc[j, "Size"])
            new_df = new_df.append(tmp, ignore_index=True)
        except:
            continue
        i += 1
        if not i % 500:
            print("On row: {} out of {} in process_df".format(i, n))
    return new_df


def find_nearest(clusters, ex):
    min = np.linalg.norm(clusters - ex, axis=1)
    ind = np.where(min == min.min())
    if len(ind[0]) == 1:
        return ind[0] + 1
    # some clusters initially start at the same value so this splits between two equally
    return random.choice(ind[0]) + 1


if __name__ == "__main__":

    new_df = process_df('data/comments.csv', 1000)
    n = new_df.shape[0]
    m = n + 1

    ###### PCA ######
    mean_normalized = (new_df - np.sum(new_df, axis=0) / m) / np.std(new_df, axis=0)
    mean_normalized_without_bra = mean_normalized[
        ['Height (cm)', 'Weight (kg)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)', 'Band Size', 'Cup Size']]

    # SVD
    x = np.array(mean_normalized_without_bra)
    sigma = np.dot(x.T, x)
    u, s, vh = np.linalg.svd(sigma, full_matrices=True)
    u1 = u[:, :2]
    z = np.dot(x, u1)
    x_approx = np.dot(u1, z.T).T
    z1 = z[:, 0]
    z2 = z[:, 1]

    plt.plot(z1, z2, 'ro')
    plt.show()

    u2 = u[:, :3]
    z = np.dot(x, u2)
    x_approx_2 = np.dot(u2, z.T).T
    z1 = z[:, 0]
    z2 = z[:, 1]
    z3 = z[:, 2]

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
    variance = num / denom
    percent = 100 * (1 - variance)
    percent_2 = 100 * (1 - num_2 / denom)
    print("{}% variance retained for k = 2".format(percent))
    print("{}% variance retained for k = 3".format(percent_2))
    # PCA seems to not be the best in this situation since variance retained for k = 2 is around 61% and k = 3 is around 73%

    ###### Clustering ######
    x = pd.DataFrame(data=x, columns=['Height (cm)', 'Weight (kg)', 'Bust (cm)', 'Waist (cm)', 'Hips (cm)', 'Band Size',
                                      'Cup Size'])
    k_error = []
    for k in range(1, x.shape[1] + 1):
        clusters = x.sample(n=k)
        clusters = clusters.reset_index(drop=True)
        error = 0
        while (True):
            c = np.zeros(x.shape[0], dtype=int)
            inner_sum = 0
            for i in range(x.shape[0]):
                c[i] = find_nearest(clusters, x.iloc[i])
                inner_sum += np.linalg.norm(x.iloc[i] - clusters.iloc[c[i] - 1]) ** 2
            for i in range(k):
                clusters.loc[i] = np.mean(x[c == i + 1])
            m = x.shape[0]
            j = 1 / m * inner_sum
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

# p2: distribution of star ratings
# p2: correlation of different features w/ star rating
# p3: try sentiment analysis on the reviews
# p4: how many items each member reviews (so we can normalize by their baseline rating)
