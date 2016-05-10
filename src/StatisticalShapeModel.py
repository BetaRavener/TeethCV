from copy import deepcopy

import numpy as np

from src.pca import PCA
from src.tooth import Tooth

__autor__ = "Ivan Sevcik, Jakub Macina"


class StatisticalShapeModel(object):
    @staticmethod
    def create(data_manager, components_limit=0):
        '''
        Creates statistical model by aligning models and performing PCA
        :param data_manager: data manager providing training data
        :param components_limit: Limit how much PCA components should be found (0 == all)
        :return: resulting PCA
        '''
        teeth = data_manager.get_all_teeth(True)
        mean_shape = deepcopy(teeth[0])
        assert isinstance(mean_shape, Tooth)
        mean_shape.move_to_origin()
        mean_shape.normalize_shape()

        error = float("inf")
        while error > 0.05:
            meanAcum = np.zeros(mean_shape.landmarks.shape)
            for i in range(0, len(teeth)):
                teeth[i].align(mean_shape)
                meanAcum += teeth[i].landmarks

            new_mean_shape = Tooth(meanAcum / len(teeth))
            new_mean_shape.align(mean_shape)
            error = new_mean_shape.sum_of_squared_distances(mean_shape)

            mean_shape = new_mean_shape

        # Realign all teeth with final mean shape
        for i in range(0, len(teeth)):
            teeth[i].align(mean_shape)

        data = np.zeros((len(teeth), teeth[0].landmarks.size))
        for i, tooth in enumerate(teeth):
            data[i, :] = tooth.landmarks.flatten()

        pca = PCA()
        pca.train(deepcopy(data), components_limit)
        return pca
