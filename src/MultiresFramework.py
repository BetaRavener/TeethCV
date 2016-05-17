from copy import deepcopy

import cv2
import numpy as np

from src.LandmarkIntensityModel import LandmarkIntensityModel
from src.config import Config
from src.datamanager import DataManager
from src.filter import Filter

__author__ = "Ivan Sevcik"


class ResolutionLevel(object):
    image = None
    default_image = None
    landmark_model = None

    def __init__(self, model_params):
        k, m = model_params
        self.landmark_model = LandmarkIntensityModel(k, m)

    def update_tooth_landmarks(self, tooth):
        '''
        Convenience method for updating tooth landmarks by using landmark_model and image
        :param tooth: Tooth for which to update landmarks.
        :return: New tooth with updated landmarks
        '''
        return self.landmark_model.update_positions(tooth, self.image)


class MultiResolutionFramework(object):
    levels_count = 2
    data_manager = None
    resolution_levels = None
    crop_translation = None  # Crop translation for currently processed image

    # Presets: median kernel size, bilateral kernel size, bilateral color delta
    _filter_presets = [(5, 17, 6), (3, 15, 6), (0, 7, 6)]
    # Params: k and m parameter
    _model_params = [(5, 14), (5, 14), (2, 5)]

    def __init__(self, data_manager):
        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager

        self.resolution_levels = list()
        for i in range(0, self.levels_count):
            self.resolution_levels.append(ResolutionLevel(MultiResolutionFramework._model_params[i]))

    def train(self):
        if Config.use_file_cache:
            success = True
            for i, level in enumerate(self.resolution_levels):
                success = success and level.landmark_model.load_from_file(str(i))

            if success:
                return

        # Iterate all radiographs one by one to save memory
        for r, radiograph in enumerate(self.data_manager.radiographs):
            image = radiograph.image
            teeth = self.datamanager.get_all_teeth_from_radiograph(radiograph, True)

            # Crop image to region of interest and translate all teeth into cropped region
            crop_translation = -Filter.get_cropping_region(image).left_top
            image = Filter.crop_image(image)
            for tooth in teeth:
                tooth.translate(crop_translation)

            for i in range(0, self.levels_count):
                resolution_level = self.resolution_levels[i]
                assert isinstance(resolution_level, ResolutionLevel)

                # Downsample the image if needed and update teeth parameters
                if i > 0:
                    image, teeth = MultiResolutionFramework.downsample(image, teeth)

                # Create copy of the image to not modify the original one
                filtered_image = image.copy()
                assert isinstance(filtered_image, np.ndarray)

                # Filter the image
                median_kernel, bilateral_kernel, bilateral_color = MultiResolutionFramework.get_filter_presets(i)
                filtered_image = Filter.process_image(filtered_image, median_kernel, bilateral_kernel, bilateral_color)

                # Add new data to the training set for given resolution
                resolution_level.landmark_model.add_training_data(teeth, filtered_image)
                print "#Training level %d done" % (i + 1)
            print "###Training radiograph %d done" % (r + 1)

        # Finish training at all levels
        for i, resolution_level in enumerate(self.resolution_levels):
            resolution_level.landmark_model.finish_training()
            resolution_level.landmark_model.save_to_file(str(i))

    def get_level(self, level_idx):
        if level_idx >= self.levels_count:
            return None

        return self.resolution_levels[level_idx]

    def set_radiograph_image(self, radiograph_image):
        '''
        Processes image and saves it's subsampled version into appropriate resolution levels
        :param image: Image to process. Should be original radiograph image without processing.
        '''
        self.crop_translation = -Filter.get_cropping_region(radiograph_image).left_top
        image = Filter.crop_image(radiograph_image)
        for i in range(0, self.levels_count):
            if i > 0:
                image = MultiResolutionFramework.downsample_image(image)

            median_kernel, bilateral_kernel, bilateral_color = MultiResolutionFramework.get_filter_presets(i)
            filtered_image = Filter.process_image(image.copy(), median_kernel, bilateral_kernel, bilateral_color)
            self.resolution_levels[i].image = filtered_image
            self.resolution_levels[i].default_image = image.copy()

    @staticmethod
    def get_filter_presets(level_idx):
        return MultiResolutionFramework._filter_presets[level_idx]

    @staticmethod
    def downsample_image(image):
        # pyrDown means down-sampling, but it is actually going up in pyramid
        return cv2.pyrDown(image)

    @staticmethod
    def downsample(image, teeth):
        image = MultiResolutionFramework.downsample_image(image)
        # Make copy of the teeth so original is not changed in place
        teeth = deepcopy(teeth)
        for tooth in teeth:
            tooth.downsample_transform()
        return image, teeth
