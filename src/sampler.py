import numpy as np

from src.tooth import Tooth

__author__ = "Ivan Sevcik"

class Sampler(object):
    @staticmethod
    def _find_sample_positions(center_point, normal, sample_count):
        positive_samples = list()
        negative_samples = list()
        center_point_tuple = tuple(center_point.astype(np.int32))

        scale = 0
        last_point_tuple = center_point_tuple
        while len(positive_samples) < sample_count:
            scale += 0.5
            sample_point = tuple(np.floor(center_point + normal * scale).astype(np.int32))
            if sample_point != last_point_tuple:
                positive_samples.append(sample_point)
                last_point_tuple = sample_point

        scale = 0
        last_point_tuple = center_point_tuple
        while len(negative_samples) < sample_count:
            scale -= 0.5
            sample_point = tuple(np.floor(center_point + normal * scale).astype(np.int32))
            if sample_point != last_point_tuple:
                negative_samples.append(sample_point)
                last_point_tuple = sample_point

        negative_samples.reverse()
        negative_samples.append(center_point_tuple)
        return negative_samples + positive_samples

    @staticmethod
    def _sample_image(image, positions):
        samples = list()
        for position in positions:
            if position[0] < 0 or position[1] < 0 or position[0] >= image.shape[1] or position[1] >= image.shape[0]:
                samples.append(0)
            else:
                samples.append(image[position[1], position[0]])

        return np.array(samples)

    @staticmethod
    def sample(tooth, radiograph_image, sample_count, normalize=False, return_positions=None):
        assert isinstance(tooth, Tooth)
        assert isinstance(radiograph_image, np.ndarray)

        result = np.empty((tooth.landmarks.shape[0], 2 * sample_count + 1))

        for i, center_point in enumerate(tooth.landmarks):
            normal = tooth.normals[i]
            positions = Sampler._find_sample_positions(center_point, normal, sample_count)
            samples = Sampler._sample_image(radiograph_image, positions)
            # Normalize samples (according to paper, this is 1 over sum of absolute values of samples)
            samples = samples.astype(np.float64)
            abs_sum = np.sum(np.abs(samples))
            if normalize and not np.isclose(abs_sum, 0):
                samples /= abs_sum
            result[i] = samples
            if return_positions is not None:
                return_positions.append(positions)

        return result
