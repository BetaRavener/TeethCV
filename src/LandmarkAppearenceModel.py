import numpy as np
from scipy.spatial.distance import mahalanobis

from src.LandmarkModel import LandmarkModel

# TODO: Outdated. If gonna be used, needs to be updated to comply with new LandmarkModel class.
class LandmarkAppearanceModel(LandmarkModel):
    means_points_model = None
    inverse_covariance_points_model = None

    k = 5

    def __init__(self, data_manager, use_file_cache=False):
        super(LandmarkAppearanceModel, self).__init__(data_manager)
        self._train_model(use_file_cache)

    def _train_model(self, use_file_cache):
        self.means_points_model = list()
        self.inverse_covariance_points_model = list()

        if use_file_cache and self.load_from_file():
            return

        radiograph_samples = self._get_samples_across_radiographs(self.k)

        # Compute mean and inverse covariance matrix for every landmark point.
        for i in range(0, radiograph_samples.shape[1]):
            point_samples = radiograph_samples[:, i, :].T
            mean, cov_mat = LandmarkAppearanceModel._get_mean_and_covariance(point_samples)

            # Assure that the matrix is inversible
            assert not np.isclose(np.linalg.det(cov_mat), 0)
            inv_cov_mat = np.linalg.inv(cov_mat)
            self.means_points_model.append(mean)
            self.inverse_covariance_points_model.append(inv_cov_mat)

        self.save_to_file()

    def find_best_position(self, sampled_profile, point_index):
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
            sampled_profile_part = sampled_profile[i:i + model_length]
            distance = mahalanobis(sampled_profile_part, self.means_points_model[point_index],
                                   self.inverse_covariance_points_model[point_index])
            if distance < min_value:
                min_value = distance
                min_index = i
        return self.k + min_index

    def load_from_file(self):
        try:
            self.means_points_model = np.load("./data/Trained/appearance_model_means.npy")
            self.inverse_covariance_points_model = np.load("./data/Trained/appearance_model_covar.npy")
        except IOError:
            return False
        return True

    def save_to_file(self):
        np.save("./data/Trained/appearance_model_means.npy", self.means_points_model)
        np.save("./data/Trained/appearance_model_covar.npy", self.inverse_covariance_points_model)