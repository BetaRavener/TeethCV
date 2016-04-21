import numpy as np
import math

from src.datamanager import DataManager
from src.sampler import Sampler
from src.tooth import Tooth
from numpy.linalg import inv


class ActiveShapeModel(object):
    data_manager = None
    image = None
    pca = None
    means_points_model = []
    inverse_covariance_points_model = []
    knobs = None

    def __init__(self, _data_manager, image, pca):
        assert isinstance(_data_manager, DataManager)
        self.data_manager = _data_manager
        self.image = image
        self.pca = pca
        self._initialize_model()

    def create_appearance_model(self, derivative=False):
        '''
        Compute mean_points_model and inverse_covariance_points_model for every point in landmark.
        :param derivative:
        :return:
        '''
        radiograph_samples = []
        for radiograph in self.data_manager.radiographs:
            for tooth in radiograph.teeth:
                assert isinstance(tooth, Tooth)
                # Get samples (40, X), where X is number 2*number_of_samples
                sample_matrix = Sampler.sample(tooth, radiograph.image, 4)
                if derivative == True:
                    # TODO maybe absolute values will be necessary
                    sample_matrix = self._compute_derivative(sample_matrix)
                radiograph_samples.append(sample_matrix)
        radiograph_samples = np.array(radiograph_samples)

        # Compute mean and inverse covariance matrix for every landmark point.
        for i in range(0, radiograph_samples.shape[1]):
            point = radiograph_samples[:, i, :]
            mean = np.mean(point, axis=0)
            mean = self._normalize_to_one_vector(mean)
            cov = np.cov(point)
            inv_cov = inv(cov)
            self.means_points_model.append(mean)
            self.inverse_covariance_points_model.append(inv_cov)
        # Means and covariance arrays for points
        assert len(self.means_points_model) == len(self.inverse_covariance_points_model)

    def _initialize_model(self):
        self.knobs = np.zeros(self.pca.eigen_values.shape)


    def _compute_derivative(self, samples):
        '''
        Compute derivation by substracting neighbour points from left to right.
        :param samples:
        :return:
        '''
        return samples[:, 0:-1] - samples[:, 1:]

    def _normalize_to_one_vector(self, vector):

        '''
        Normalize numpy vector.
        @param vector:
        @return:
        '''
        res = []
        magnitude = math.sqrt(sum([x ** 2 for x in vector]))
        vector = [x / magnitude for x in vector]
        return vector
