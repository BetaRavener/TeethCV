from copy import deepcopy

import numpy as np

from src.filter import Filter
from src.sampler import Sampler
from src.tooth import Tooth


class LandmarkModel(object):
    data_manager = None

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def _get_samples_across_radiographs(self, count):
        radiograph_samples = []
        for radiograph in self.data_manager.radiographs:
            # Pre-process the image
            img = radiograph.image
            cropping_region = Filter.get_cropping_region(img)
            img = Filter.crop_image(img)
            img = Filter.process_image(img)

            for tooth in radiograph.teeth:
                # Make a copy so the original in data manager is not modified
                tooth = deepcopy(tooth)
                assert isinstance(tooth, Tooth)
                # Translate landmarks into the cropped region
                tooth.translate(-cropping_region.left_top)
                # Get samples (40, X), where X is number 2*number_of_samples+1
                sample_matrix = Sampler.sample(tooth, img, count, True)
                radiograph_samples.append(sample_matrix)

        return np.array(radiograph_samples)

    def find_best_position(self, sampled_profile, point_index):
        pass

    @staticmethod
    def _get_mean_and_covariance(data):
        """

        :param data: Data in this format: rows are variables and each columns are observations (one column = one observation of all variables)
                        0, 1, 2, 3, 4,..
                     x1|1| 2| 2| 0| 1|..
                     x2|0| 1| 0| 1| 2|..
                     ..|.|..|..|..|..|..
        :return: mean and covariance matrix for the data
        """
        mean = np.mean(data, axis=1)
        demeaned = data - mean[:, np.newaxis]
        cov = np.dot(demeaned, demeaned.T) / (demeaned.shape[1] - 1)
        return mean, np.matrix(cov)
