import cv2
import numpy as np

from src.datamanager import DataManager
from src.filter import Filter

__author__ = "Ivan Sevcik"

class InitialPoseModel(object):
    data_manager = None
    crop_sides_size = 160
    crop_upper_jaw_top_size = 160
    crop_lower_jaw_size = 160
    top_jaw_line = None
    lower_jaw_line = None
    max_angle = 10
    close_lines_threshold = 40

    def __init__(self, data_manager):
        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager

    @staticmethod
    def _find_basic_poses(image):
        return [(np.array((251, 405)), 50, 0),
                (np.array((345, 401)), 50, 0.1),
                (np.array((470, 393)), 50, 0.1),
                (np.array((561, 378)), 50, 0.2),
                (np.array((291, 605)), 40, 0),
                (np.array((375, 601)), 40, 0),
                (np.array((460, 593)), 40, 0),
                (np.array((541, 578)), 40, 0),
                ]

    @staticmethod
    def downsample_pose(pose, count=1):
        translation, scale, rotation = pose
        return translation / (2**count), scale / (2**count), rotation

    def find(self, image):
        '''
        Finds initial poses
        :param image:
        :param level:
        :return:
        '''

        #basic_poses = InitialPoseModel._find_basic_poses(image)
        basic_poses = self._find_poses(image)

        return [basic_poses[i] for i in self.data_manager.selector]

    def _find_poses(self, image):
        self.top_jaw_line, self.lower_jaw_line = self._find_jaw_separation_line(image)

        upper_jaw_image = self.crop_top_jaw(image, self.top_jaw_line)
        lower_jaw_image = self.crop_lower_jaw(image, self.lower_jaw_line)

        # Filter the image
        upper_jaw_image = Filter.process_image(upper_jaw_image, median_kernel=5, bilateral_kernel=17, bilateral_color=6)
        lower_jaw_image = Filter.process_image(lower_jaw_image, median_kernel=5, bilateral_kernel=17, bilateral_color=6)

        upper_jaw_image = self._convert_to_binary_image(upper_jaw_image)
        lower_jaw_image = self._convert_to_binary_image(lower_jaw_image)

        upper_lines = self._find_hough_lines(upper_jaw_image)
        lower_lines = self._find_hough_lines(lower_jaw_image)

        # Filter out lines
        upper_lines = self._filter_lines(upper_lines, upper_jaw_image.shape)
        lower_lines = self._filter_lines(lower_lines, lower_jaw_image.shape)

        # Compute starting points
        rho0, theta0 = upper_lines[0]
        rho1, theta1 = upper_lines[1]
        rho2, theta2 = upper_lines[2]
        position0 = np.array((rho0-35+self.crop_sides_size, 50+(self.top_jaw_line - self.crop_upper_jaw_top_size)))
        position1 = np.array((rho0+(rho1-rho0)/2 + self.crop_sides_size, 80+(self.top_jaw_line - self.crop_upper_jaw_top_size)))
        position2 = np.array((rho1+(rho2-rho1)/2 + self.crop_sides_size, 80+(self.top_jaw_line - self.crop_upper_jaw_top_size)))
        position3 = np.array((rho2+35+self.crop_sides_size, 50+(self.top_jaw_line - self.crop_upper_jaw_top_size)))
        rho0, theta0 = lower_lines[0]
        rho1, theta1 = lower_lines[1]
        rho2, theta2 = lower_lines[2]
        position4 = np.array((rho0-40+self.crop_sides_size, 90+self.lower_jaw_line))
        position5 = np.array((rho0+(rho1-rho0)/2+self.crop_sides_size, 100+self.lower_jaw_line))
        position6 = np.array((rho1+(rho2-rho1)/2+self.crop_sides_size, 100+self.lower_jaw_line))
        position7 = np.array((rho2+40+self.crop_sides_size, 90+self.lower_jaw_line))

        return [(position0, 50, -0.1),
                (position1, 50, 0.1),
                (position2, 50, 0.1),
                (position3, 50, 0.2),
                (position4, 40, 0),
                (position5, 40, -0.1),
                (position6, 40, -0.1),
                (position7, 40, 0.2)
                ]

    def _find_jaw_separation_line(self, image):
        y_histogram = cv2.reduce(image, 1, cv2.cv.CV_REDUCE_SUM, dtype=cv2.CV_32S)
        min_y = np.argmin(y_histogram)
        return self._get_peak_range(y_histogram, min_y)

    def crop_top_jaw(self, image, y_line):
        return image[y_line-self.crop_upper_jaw_top_size:y_line, self.crop_sides_size:image.shape[1]-self.crop_sides_size]

    def crop_lower_jaw(self, image, y_line):
        return  image[y_line: y_line+self.crop_lower_jaw_size, self.crop_sides_size:image.shape[1]-self.crop_sides_size]

    def _get_peak_range(self, histogram, min_index):
        threshold = 5000
        minimum_value = histogram[min_index]
        max_range_index = min_index
        for i in range(min_index, min_index+200):
            if (i > histogram.shape[0]):
                break
            if (histogram[i] > minimum_value + threshold):
                break
            max_range_index = i
        min_range_index = min_index
        for i in reversed(range(min_index-200, min_index)):
            if (i < 0):
                break
            if (histogram[i] > minimum_value + threshold):
                break
            min_range_index = i
        return (min_range_index, max_range_index)

    def _convert_to_binary_image(self, image):
        image = np.array(image, dtype=np.uint8)
        return cv2.threshold(image, 8, 255, cv2.THRESH_BINARY)[1]

    def _find_hough_lines(self, image):
        #self.lines = cv2.HoughLinesP(self.image, 1, np.pi/90, 5, None, 80, 40)
        lines = cv2.HoughLines(image, 1, 20*np.pi/180, 30, 0,0)
        return lines

    def _filter_lines(self, lines, image_shape):
        mask = []
        # Filter only vertical lines
        for rho,theta in lines[0]:
                if (theta >= np.pi/180*0 and theta <= np.pi/180*self.max_angle) or (theta >= np.pi/180*(180-self.max_angle) and theta <= np.pi/180*180):
                    mask.append(True)
                else:
                    mask.append(False)
        mask = np.array(mask)
        lines = lines[0][mask]
        lines = sorted(lines, key=lambda item: item[0], reverse=True)

        # Delete lines close together
        mask = []
        previous = 0
        for rho,theta in lines:
            if (rho < previous+self.close_lines_threshold and rho > previous-self.close_lines_threshold) \
                    or (rho < self.close_lines_threshold):
                mask.append(False)
            else:
                mask.append(True)
                previous = rho
        mask = np.array(mask)
        lines = np.array(lines)
        lines = lines[mask]

        # Filter only 3 lines - Go from the middle to the sides and add/remove lines
        middle = image_shape[1] / 2
        min_idx = 0
        min_dist = float('Inf')
        for i, line_par in enumerate(lines):
            rho, theta = line_par
            if np.abs(rho-middle) < min_dist:
                min_dist = np.abs(rho-middle)
                min_idx = i
        lines = lines[min_idx-1:min_idx+2]

        # Return sorted from left to right tooth
        lines = sorted(lines, key=lambda item: item[0])
        return np.array(lines)

