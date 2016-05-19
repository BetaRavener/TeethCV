import numpy as np

from src.tooth import Tooth

__author__ = "Ivan Sevcik"

class Sampler(object):
    @staticmethod
    def _find_sample_positions(center_point, normal, sample_count):
        """
        Finds sampling position for a given central point and normal.
        :param center_point: Point around which to sample.
        :param normal: A normal along which to sample.
        :param sample_count: Number of pixels that should be sampled at each side of 'center_point'
        :return: (2*sample_count+1) sampling positions going from the most negative normal position to the most positive
                 normal position.
        """
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
        """
        Samples image at specified positions.
        :param image: Image to sample.
        :param positions: Positions at which to sample.
        :return: A numpy array of sampled pixel values.
        """
        samples = list()
        for position in positions:
            if position[0] < 0 or position[1] < 0 or position[0] >= image.shape[1] or position[1] >= image.shape[0]:
                samples.append(0)
            else:
                samples.append(image[position[1], position[0]])

        return np.array(samples)

    @staticmethod
    def sample(tooth, radiograph_image, sample_count, normalize=False, return_positions=None):
        """
        Samples the 'radiograph' image along normals of each landmark point creating 'tooth' shape.
        :param tooth: Tooth along which's landmark points should be sampled.
        :param radiograph_image: A radiograph image to sample.
        :param sample_count: Specifies how many pixels on each side of the point should be sampled/
        :param normalize: If true, the pixel values of the sampled vector are normalized into range <0, 1>
        :param return_positions: If list is passed as this argument, it will be filled by positions at which the pixels
                                 were sampled from the image.
        :return: A numpy array of sampled pixel values.
        """
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
