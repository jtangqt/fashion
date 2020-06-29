import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from comments_analyze import process_df


def gradient_descent(X, y, theta, iterations, alpha):
    m = len(X)
    j = []

    for i in range(iterations):
        h = np.dot(X, theta)
        cost = 1 / (2 * m) * np.sum((h - y) ** 2)
        theta = theta - alpha / m * np.dot(X.T, (h - y))
        j.append(cost)
        if not i % 500:
            print("On iteration: {} out of {}".format(i, iterations))
    return theta, j


def plot_cost(j):
    x = np.linspace(0, len(j), len(j))
    plt.plot(x, j)
    plt.show()


def gradient_descent_on_fit(df, iterations, alpha):
    new_df = df.loc[df['Fit'] != "None"]
    X = new_df[["Height (cm)", "Size"]]
    y = new_df[["Fit"]]
    theta = np.zeros((X.shape[1], 1))

    return gradient_descent(X, y, theta, iterations, alpha)


if __name__ == "__main__":
    new_df = process_df('data/comments.csv', 1000)
    # print(new_df.head())

    iterations = 1000
    alpha = 0.0001

    # run gradient descent and plot cost on the j's
    theta, j = gradient_descent_on_fit(new_df, iterations, alpha)
    plot_cost(j)
    print(theta)
