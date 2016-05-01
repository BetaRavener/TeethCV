import numpy as np

from src.LandmarkModel import LandmarkModel


class LandmarkIntensityModel(LandmarkModel):
    means_points_model = None

    def __init__(self):
        super(LandmarkIntensityModel, self).__init__()
        self.means_points_model = list()

    def finish_training(self):
        radiograph_samples_arr = np.array(self.radiograph_samples)

        # Compute mean and inverse covariance matrix for every landmark point.
        for i in range(0, radiograph_samples_arr.shape[1]):
            point_samples = radiograph_samples_arr[:, i, :].T
            mean, cov_mat = LandmarkModel._get_mean_and_covariance(point_samples)
            self.means_points_model.append(mean)

    def _find_best_position(self, sampled_profile, landmark_index):
        '''
        Finds best position of landmark by matching model profile to a new sampled profile.
        :param sampled_profile: A sampled profile along landmark normal. Length 2m + 1.
        :param landmark_index: Index of landmark.
        :return: Index of sampled_profile where best match occurred when profiles were center-aligned.
        '''
        model_vec = self.means_points_model[landmark_index]
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

    def load_from_file(self, name):
        try:
            self.means_points_model = np.load("./data/Trained/lim_%s.npy" % name)
        except IOError:
            return False
        return True

    def save_to_file(self, name):
        np.save("./data/Trained/lim_%s.npy" % name, self.means_points_model)
