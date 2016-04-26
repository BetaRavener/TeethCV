from copy import deepcopy

import numpy as np

from src.MultiresFramework import MultiResolutionFramework
from src.datamanager import DataManager
from src.filter import Filter
from src.tooth import Tooth
from src.utils import to_landmarks_format


class ActiveShapeModel(object):
    data_manager = None
    pca = None
    landmark_model = None
    multi_resolution_framework = None

    mean_tooth = None
    current_tooth = None
    current_params = None
    current_level = 0

    @property
    def image(self):
        return self.multi_resolution_framework.get_level(self.current_level).image

    @image.setter
    def image(self, img):
        self.multi_resolution_framework.set_radiograph_image(img)

    def __init__(self, _data_manager, pca):
        assert isinstance(_data_manager, DataManager)
        self.data_manager = _data_manager
        self.pca = pca
        self.multi_resolution_framework = MultiResolutionFramework(self.data_manager)
        self.multi_resolution_framework.train()
        # self.landmark_model = LandmarkIntensityModel()
        # self.landmark_model.old_training(self.data_manager)

    def set_up(self, translation=(0, 0), scale=1, rotation=0):
        self.mean_tooth = Tooth(to_landmarks_format(self.pca.mean))
        self.current_tooth = deepcopy(self.mean_tooth)
        self.current_tooth.transform(translation, scale, rotation)

    def make_step(self):
        # 1. Sample along normals and find best new position for points by comparing with model
        resolution_level = self.multi_resolution_framework.get_level(self.current_level)
        tooth = resolution_level.update_tooth_landmarks(self.current_tooth)

        self.current_tooth = tooth
        self.current_params = np.zeros(self.pca.eigen_values.size)

        # 2. Find new translation, scale, rotation and eigen values
        translation, scale, rotation = tooth.align(self.mean_tooth)
        b = self.pca.project(tooth.landmarks.flatten())

        # 3. Limit the eigen values to allowed range
        max_deviations = self.pca.get_allowed_deviation()
        for i in range(0, b.shape[0]):
            b[i] = min(max(b[i], -max_deviations[i]), max_deviations[i])

        # 3b. Limit pose values
        scale = min(max(scale, 5), 60)

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

    def change_level(self, level):
        self.current_level = level


