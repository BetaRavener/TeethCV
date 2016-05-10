from copy import deepcopy

import numpy as np

from src.filter import Filter
from src.sampler import Sampler
from src.tooth import Tooth

__author__ = "Ivan Sevcik"

class LandmarkModel(object):
    radiograph_samples = None
    k = None
    m = None
    normalize = None

    def __init__(self, k=2, m=12, normalize=True):
        self.radiograph_samples = list()
        self.k = k
        self.m = m
        self.normalize = normalize

    def add_training_data(self, teeth, image):
        '''
        Adds another set of training data to model. The teeth must be already aligned in the image.
        :param teeth: List of teeth.
        :param image: Image that will be sampled.
        '''
        for i, tooth in enumerate(teeth):
            # Make a copy so the original in data manager is not modified
            tooth = deepcopy(tooth)
            assert isinstance(tooth, Tooth)
            # Get samples (40, X), where X is number 2*number_of_samples+1
            sample_matrix = Sampler.sample(tooth, image, self.k, self.normalize)
            self.radiograph_samples.append(sample_matrix)
            print "Sampling tooth %d done" % (i+1)

    def finish_training(self):
        '''
        Finishes the training by creating the actual model from previously supplied data.
        '''
        pass

    def update_positions(self, tooth, image):
        '''
        Updates landmark positions of tooth to be in best alignment with the image.
        :param tooth: Tooth with original landmarks.
        :param image: Image that will be sampled for finding new landmark positions. It must be already preprocessed.
        :return: New tooth with updated landmarks.
        '''
        # Sample along normals and find best new position for points by comparing with trained model
        return_positions = []
        new_landmarks = []
        sample_matrix = Sampler.sample(tooth, image, self.m, self.normalize, return_positions)
        for i, sampled_profile in enumerate(sample_matrix):
            position = self._find_best_position(sampled_profile, i)
            new_landmarks.append(return_positions[i][position])

        return Tooth(np.array(new_landmarks))

    def _find_best_position(self, sampled_profile, point_index):
        pass

    @staticmethod
    def _get_mean_and_covariance(data):
        """

        :param data: Data in this format: rows are variables and each columns are observations (one column = one observation of all variables)
                        0, 1, 2, 3, 4,..
                     x1|1| 2| 2| 0| 1|..
                     x2|0| 1| 0| 1| 2|..
                     ..|.|..|..|..|..|..
        :return: mean and covariance matrix for the data
        """
        mean = np.mean(data, axis=1)
        demeaned = data - mean[:, np.newaxis]
        cov = np.dot(demeaned, demeaned.T) / (demeaned.shape[1] - 1)
        return mean, np.matrix(cov)
