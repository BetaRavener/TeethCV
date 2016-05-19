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
        """
        Returns image currently used by active shape model.
        :return: Currently used image from resolution framework.
        """
        return self.multi_resolution_framework.get_level(self.current_level).image

    def __init__(self, _data_manager, pca):
        assert isinstance(_data_manager, DataManager)
        self.data_manager = _data_manager
        self.pca = pca
        self.multi_resolution_framework = MultiResolutionFramework(self.data_manager)
        self.multi_resolution_framework.train()

    def set_image_to_search(self, image):
        """
        Sets image on which the active shape model search will be performed.
        :param image: Image to search.
        """
        self.multi_resolution_framework.set_radiograph_image(image)

    def set_up(self, translation=(0, 0), scale=1, rotation=0):
        """
        Sets up the initial shpae before performing search. The search always start from the mean shape and eigenvalues
        all 0, but translation, scale and rotation of this shape can be controlled.
        :param translation: Translation of the initial shape.
        :param scale: Scale of the initial shape.
        :param rotation: Rotation of the initial shape.
        """
        self.mean_tooth = Tooth(to_landmarks_format(self.pca.mean))
        self.current_tooth = deepcopy(self.mean_tooth)
        self.current_tooth.transform(translation, scale, rotation)
        self.current_params = np.zeros(self.pca.eigen_values.shape)

    def make_step(self, phase=None):
        """
        Performs one step of the active shape model search algorithm, which updates landmarks, projects obtained model
        on the PCA, limits returned eigenvalues and reconstructs the shape again. Current propoerties of this ASM
        instance are updated accordingly.
        :param phase: If None, whole algorithm is performed. If 0, only landmarks will be updated. If 1, everything
                      except landmark updates will be perfomed.
        """
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

            # 3b. Limit pose values
            scale = min(max(scale, 5), 80 / (2 ** self.current_level))

            # 4. Reconstruct modified shape
            new_shape = self.pca.reconstruct(b)
            new_tooth = Tooth(to_landmarks_format(new_shape))
            new_tooth.transform(translation, scale, rotation)

            self.current_params = b

        self.current_tooth = new_tooth

    def _get_difference(self, previous_tooth):
        """
        Computes the change of current_tooth shape that occurred from previous_tooth using sum of squared distances.
        :param previous_tooth: Previous tooth to which's shape the current one should be compared
        :return: Sum of squared distances between landmark points of the two teeth.
        """
        return self.current_tooth.sum_of_squared_distances(previous_tooth)

    def run(self, stop_token=None, step_callback=None):
        """
        Performs complete Active Shape Model search in multiple resolution levels.
        :param stop_token: A token that can be used to interrupt the algorithm.
        :param step_callback: A callback function that can be used to report after a step of algorithm has been done.
        :return: Final tooth that is positioned into original radiograph image (see: set_image_to_search)
        """
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

        # At last, position the tooth into original radiograph
        return self.get_current_tooth_positioned()

    def change_level(self, level):
        """
        Changes the resolution level at which the search takes place.
        :param level: An index of level, where 0 is base image and increasing numbers halve resolution each time.
        """
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
        """
        Returns current level at which the search is performed.
        :return: Current level.
        """
        return self.multi_resolution_framework.get_level(self.current_level)

    def get_current_tooth_positioned(self):
        """
        Positions current tooth into original radiograph image (see: set_image_to_search)
        :return: Positioned tooth.
        """
        tooth = deepcopy(self.current_tooth)
        assert isinstance(tooth, Tooth)
        tooth.translate(-self.multi_resolution_framework.crop_translation)
        return tooth
