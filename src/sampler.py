import cv2
import numpy as np

from src.tooth import Tooth


class Sampler(object):
    @staticmethod
    def _find_sample_positions(center_point, normal, sample_count):
        positive_samples = list()
        negative_samples = list()
        center_point_tuple = tuple(center_point)

        scale = 0
        while len(positive_samples) < sample_count:
            scale += 0.5
            sample_point = tuple(np.floor(center_point + normal * scale))
            if sample_point not in positive_samples and sample_point != center_point_tuple:
                positive_samples.append(sample_point)

        scale = 0
        while len(negative_samples) < sample_count:
            scale -= 0.5
            sample_point = tuple(np.floor(center_point + normal * scale))
            if sample_point not in negative_samples and sample_point != center_point_tuple:
                negative_samples.append(sample_point)

        negative_samples.reverse()
        negative_samples.append(center_point_tuple)
        return negative_samples + positive_samples

    @staticmethod
    def _sample_image(image, positions):
        samples = list()
        for position in positions:
            if position[0] < 0 or position[1] < 0 or position[0] > image.shape[1] or position[1] > image.shape[0]:
                samples.append(0)
            else:
                samples.append(image[position[1], position[0]])

        return samples

    @staticmethod
    def sample(tooth, radiograph_image, sample_count):
        assert isinstance(tooth, Tooth)
        assert isinstance(radiograph_image, np.ndarray)

        result = np.empty((tooth.landmarks.shape[0], 2 * sample_count + 1))

        for i, center_point in enumerate(tooth.landmarks):
            normal = tooth.normals[i]
            positions = Sampler._find_sample_positions(center_point, normal, sample_count)
            result[i] = Sampler._sample_image(radiograph_image, positions)

        return result
