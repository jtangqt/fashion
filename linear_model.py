import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from comments_analyze import process_df

def gradientDescent(X, y, theta, iterations, alpha):
    m = len(X)
    j = []

    for i in range(iterations):
        h = np.dot(X, theta)
        cost = 1/(2*m)*np.sum((h-y)**2)
        theta = theta - alpha / m * np.dot(X.T, (h-y))
        j.append(cost)

    return theta, j

def plotCost(j):
    x = np.linspace(0, len(j), len(j))
    plt.plot(x, j)
    plt.show()

if __name__ == "__main__":
    new_df = process_df('data/comments.csv', 1000)

    theta = np.zeros((2, 1))
    # run gradient descent and plot cost on the j's