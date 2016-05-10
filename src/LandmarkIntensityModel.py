import numpy as np

from src.LandmarkModel import LandmarkModel

__author__ = "Ivan Sevcik"

class LandmarkIntensityModel(LandmarkModel):
    factor_array = None

    def __init__(self, k, m):
        super(LandmarkIntensityModel, self).__init__(k, m)
        min_factor = 0.5
        max_factor = 1.0
        step = (max_factor - min_factor) / m
        self.factor_array = np.zeros(2 * m + 1)
        for i in range(0, m + 1):
            self.factor_array[m-i] = max_factor - i * step
            self.factor_array[m+i] = max_factor - i * step

    def _find_best_position(self, sampled_profile, landmark_index):
        '''
        Finds best position of landmark by matching model profile to a new sampled profile.
        :param sampled_profile: A sampled profile along landmark normal. Length 2m + 1.
        :param landmark_index: Index of landmark.
        :return: Index of sampled_profile where best match occurred when profiles were center-aligned.
        '''

        sampled_profile *= self.factor_array

        max_intensity = -float('inf')
        max_intensity_idx = 0

        for i, intensity in enumerate(sampled_profile):
            if max_intensity < intensity:
                max_intensity = intensity
                max_intensity_idx = i

        return max_intensity_idx

    def load_from_file(self, name):
        return True

    def save_to_file(self, name):
        pass
