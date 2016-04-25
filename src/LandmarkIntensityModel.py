import numpy as np

from src.LandmarkModel import LandmarkModel


class LandmarkIntensityModel(LandmarkModel):
    k = 10

    def __init__(self, data_manager):
        super(LandmarkIntensityModel, self).__init__(data_manager)
        self._train()

    def _train(self):
        self.means_points_model = list()

        radiograph_samples = self._get_samples_across_radiographs(self.k)

        # Compute mean and inverse covariance matrix for every landmark point.
        for i in range(0, radiograph_samples.shape[1]):
            point_samples = radiograph_samples[:, i, :].T
            mean, cov_mat = LandmarkModel._get_mean_and_covariance(point_samples)
            self.means_points_model.append(mean)

    def find_best_position(self, sampled_profile, point_index):
        '''

        :param sampled_profile: Length 2m + 1
        :param model: Length 2k + 1
        :return:
        '''
        model_vec = self.means_points_model[point_index]
        model_length = len(model_vec)
        sampled_profile_length = len(sampled_profile)

        min_value = float("inf")
        min_index = 0

        ssd_arr = np.empty(sampled_profile_length - model_length + 1)
        for i in range(0, sampled_profile_length - model_length + 1):
            sampled_profile_part = sampled_profile[i:i + model_length]
            ssd = LandmarkIntensityModel.sum_of_squared_differences(model_vec, sampled_profile_part)
            ssd_arr[i] = ssd
            if ssd < min_value:
                min_value = ssd
                min_index = i

        return self.k + min_index

    @staticmethod
    def sum_of_squared_differences(vec1, vec2):
        assert isinstance(vec1, np.ndarray)
        assert isinstance(vec2, np.ndarray)
        return np.sum((vec1 - vec2) ** 2)
