from copy import deepcopy

import numpy as np
from scipy.spatial.distance import mahalanobis

from src.LandmarkAppearenceModel import LandmarkAppearanceModel
from src.LandmarkIntensityModel import LandmarkIntensityModel
from src.datamanager import DataManager
from src.sampler import Sampler
from src.tooth import Tooth
from src.utils import to_landmarks_format


class ActiveShapeModel(object):
    data_manager = None
    pca = None
    landmark_model = None

    image = None
    mean_tooth = None
    current_tooth = None
    current_params = None

    # Model parameters
    m = 30

    def __init__(self, _data_manager, pca):
        assert isinstance(_data_manager, DataManager)
        self.data_manager = _data_manager
        self.pca = pca
        self.landmark_model = LandmarkIntensityModel(self.data_manager)

    def set_up(self, translation=(0, 0), scale=1, rotation=0):
        self.mean_tooth = Tooth(to_landmarks_format(self.pca.mean))
        self.current_tooth = deepcopy(self.mean_tooth)
        self.current_tooth.transform(translation, scale, rotation)

    def make_step(self):
        return_positions = []
        # 1. Sample along normals and find best new position for points by comparing with model
        sample_matrix = Sampler.sample(self.current_tooth, self.image, self.m, True, return_positions)
        for i, sampled_profile in enumerate(sample_matrix):
            position = self.landmark_model.find_best_position(sampled_profile, i)
            self.current_tooth.landmarks[i] = return_positions[i][position]
        self.current_tooth._calculate_centroid()

        # 2. Find new translation, scale, rotation and eigen values
        translation, scale, rotation = self.current_tooth.align(self.mean_tooth)
        b = self.pca.project(self.current_tooth.landmarks.flatten())

        # 3. Limit the eigen values to allowed range
        max_deviations = self.pca.get_allowed_deviation()
        for i in range(0, b.shape[0]):
            b[i] = min(max(b[i], -max_deviations[i]), max_deviations[i])


        # 3b. Limit pose values
        scale = min(max(scale, 20), 60)

        # 4. Reconstruct modified shape
        new_shape = self.pca.reconstruct(b)
        new_tooth = Tooth(to_landmarks_format(new_shape))
        new_tooth.transform(translation, scale, rotation)

        self.current_params = b
        self.current_tooth = new_tooth

    def _get_difference(self, previous_tooth):
        return self.current_tooth.sum_of_squared_distances(previous_tooth)

    def run(self):
        difference = float('inf')
        while True:
            previous_tooth = self.current_tooth
            self.make_step()
            new_difference = self._get_difference(previous_tooth)

            # Test convergence. If new difference is larger than previous, stop algorithm
            if new_difference > difference:
                self.current_tooth = previous_tooth
                break

            difference = new_difference


