import numpy as np
import math
from scipy.spatial.distance import mahalanobis

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

    current_model = None

    # Model parameters
    k = 4
    m = 9
    b = None
    scale = 10
    rotation = 0
    position = (0,0)


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
                sample_matrix = Sampler.sample(tooth, radiograph.image, self.k)
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
        self.b = np.zeros(self.pca.eigen_values.shape)
        self.current_model = Tooth(self.pca.mean.reshape((self.pca.mean.size / 2, 2)))
        self.mean_tooth = Tooth(self.pca.mean.reshape((self.pca.mean.size / 2, 2)))


    def make_step(self):
        return_positions = []
        # Get sample ()
        sample_matrix = Sampler.sample(self.current_model, self.image, self.m, return_positions)
        for i, sampled_profile in enumerate(sample_matrix):
            position = self._find_best_position(sampled_profile, i)
            self.current_model.landmarks[i] = return_positions[i][position]
        self.position, self.scale, self.rotation =  self.current_model.align(self.mean_tooth)
        self.b = self.pca.project(self.current_model.landmarks)
        max_deviations = self.pca.get_allowed_deviation()
        for i in range(0, self.b.shape[0]):
            self.b[i] = min(max(self.b[i], -max_deviations[i]), max_deviations[i])
        # Reconstruct shape
        new_shape = self.pca.reconstruct(self.b)


    def _find_best_position(self, sampled_profile, point_index):
        '''

        :param sampled_profile: Length 2m + 1
        :param model: Length 2k + 1
        :return:
        '''
        model_length = len(self.means_points_model[point_index])
        sampled_profile_length = len(sampled_profile)
        min_value = float("inf")
        min_index = 0
        for i in range(0, sampled_profile_length - model_length + 1):
            sampled_profile_part = sampled_profile[i:i+model_length]
            distance = mahalanobis(sampled_profile_part, self.means_points_model[point_index], self.inverse_covariance_points_model[point_index] )
            if distance < min_value:
                min_value = distance
                min_index = i
        return self.k + min_index



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
