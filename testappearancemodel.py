import numpy as np
import sys

from src.LandmarkAppearenceModel import LandmarkAppearanceModel
from src.datamanager import DataManager

import matplotlib

from src.pca import PCA

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


def cov(a, b):

    if len(a) != len(b):
        return

    a_mean = np.mean(a)
    b_mean = np.mean(b)

    sum = 0

    for i in range(0, len(a)):
        sum += ((a[i] - a_mean) * (b[i] - b_mean))

    return sum/(len(a)-1)

data_manager = DataManager()
model = LandmarkAppearanceModel(data_manager)
samples = model._get_samples_across_radiographs()
one_point_samples = samples[:, 0, :].T
print "Data rank: %d" % (np.linalg.matrix_rank(one_point_samples))

mean = np.mean(one_point_samples, axis=1)
demeaned = (one_point_samples - mean[:, np.newaxis])

cov_matrix = np.cov(one_point_samples)

np.savetxt("cov.txt", cov_matrix, '%.2e')
print "Matrix rank: %d\nMatrix det: %f" % (np.linalg.matrix_rank(cov_matrix), np.linalg.det(cov_matrix))

tol = 1e-5
Q, R = np.linalg.qr(cov_matrix)
independent = np.abs(R.diagonal()) > tol

n = one_point_samples.shape[0]

plt.ion()
f, ax = plt.subplots(n, n)
for i, x in enumerate(demeaned):
    for j, y in enumerate(demeaned):
        if i >= n or j >= n:
            continue

        graph = ax[i, j]
        plt.setp(graph.get_xticklabels(), visible=False)
        plt.setp(graph.get_yticklabels(), visible=False)
        graph.scatter(x, y)
        graph.set_xlim([x.min(), x.max()])
        graph.set_ylim([y.min(), y.max()])

plt.waitforbuttonpress()