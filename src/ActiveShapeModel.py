from copy import deepcopy

import cv2
import numpy as np

from src.MultiresFramework import MultiResolutionFramework
from src.datamanager import DataManager
from src.tooth import Tooth
from src.utils import to_landmarks_format, StopIterationToken

__author__ = "Ivan Sevcik"


class ActiveShapeModel(object):
    data_manager = None
    pca = None
    multi_resolution_framework = None

    mean_tooth = None
    current_tooth = None
    current_params = None
    current_level = 0
    max_steps_per_level = 100

    @property
    def current_image(self):
        return self.multi_resolution_framework.get_level(self.current_level).image

    def __init__(self, _data_manager, pca):
        assert isinstance(_data_manager, DataManager)
        self.data_manager = _data_manager
        self.pca = pca
        self.multi_resolution_framework = MultiResolutionFramework(self.data_manager)
        self.multi_resolution_framework.train()

    def set_image_to_search(self, image):
        self.multi_resolution_framework.set_radiograph_image(image)

    def set_up(self, translation=(0, 0), scale=1, rotation=0):
        self.mean_tooth = Tooth(to_landmarks_format(self.pca.mean))
        self.current_tooth = deepcopy(self.mean_tooth)
        self.current_tooth.transform(translation, scale, rotation)
        self.current_params = np.zeros(self.pca.eigen_values.shape)

    def make_step(self, phase=None):
        if phase is None or phase == 0:
            # 1. Sample along normals and find best new position for points by comparing with model
            resolution_level = self.multi_resolution_framework.get_level(self.current_level)
            new_tooth = resolution_level.update_tooth_landmarks(self.current_tooth)
        else:
            new_tooth = deepcopy(self.current_tooth)

        if phase is None or phase == 1:
            # 2. Find new translation, scale, rotation and eigen values
            translation, scale, rotation = new_tooth.align(self.mean_tooth)
            b = self.pca.project(new_tooth.landmarks.flatten())

            # 3. Limit the eigen values to allowed range
            max_deviations = self.pca.get_allowed_deviation()
            for i in range(0, b.shape[0]):
                b[i] = min(max(b[i], -max_deviations[i]), max_deviations[i])

            # TODO: Maybe do it statistically?
            # 3b. Limit pose values
            scale = min(max(scale, 5), 80 / (2 ** self.current_level))

            # 4. Reconstruct modified shape
            new_shape = self.pca.reconstruct(b)
            new_tooth = Tooth(to_landmarks_format(new_shape))
            new_tooth.transform(translation, scale, rotation)

            self.current_params = b

        self.current_tooth = new_tooth

    def _get_difference(self, previous_tooth):
        return self.current_tooth.sum_of_squared_distances(previous_tooth)

    def run(self, stop_token=None, step_callback=None):
        next_level = MultiResolutionFramework.levels_count - 1
        self.current_level = 0

        while next_level >= 0:
            self.change_level(next_level)
            # Show initial state
            if step_callback is not None:
                    step_callback()

            steps_left = ActiveShapeModel.max_steps_per_level
            while steps_left > 0:
                if isinstance(stop_token, StopIterationToken) and stop_token.stop:
                    return

                previous_tooth = self.current_tooth
                self.make_step()
                difference = self._get_difference(previous_tooth)

                if step_callback is not None:
                    step_callback()

                # Test convergence. If new difference is larger than previous, stop algorithm
                if difference < 1:
                    self.current_tooth = previous_tooth
                    break

                steps_left -= 1

            next_level -= 1

        # At last, perform inverse crop translation
        tooth = deepcopy(self.current_tooth)
        assert isinstance(tooth, Tooth)
        tooth.translate(-self.multi_resolution_framework.crop_translation)
        return tooth

    def change_level(self, level):
        difference = level - self.current_level
        if difference == 0:
            return

        self.current_level = level

        if self.current_tooth is None:
            return

        assert isinstance(self.current_tooth, Tooth)
        if difference < 0:
            for i in range(0, -difference):
                self.current_tooth.upsample_transform()
        else:
            for i in range(0, difference):
                self.current_tooth.downsample_transform()

    def get_current_level(self):
        return self.multi_resolution_framework.get_level(self.current_level)

    def get_current_tooth_positioned(self):
        tooth = deepcopy(self.current_tooth)
        assert isinstance(tooth, Tooth)
        tooth.translate(-self.multi_resolution_framework.crop_translation)
        return tooth
