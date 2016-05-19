import cv2
import numpy as np

from src.datamanager import DataManager
from src.filter import Filter

__author__ = "Jakub Macina, Ivan Sevcik"


class InitialPoseModel(object):
    data_manager = None
    crop_sides_size = 160
    crop_upper_jaw_top_size = 160
    crop_lower_jaw_size = 160
    top_jaw_line = None
    lower_jaw_line = None
    max_angle = 25
    side_lines_threshold = 100

    def __init__(self, data_manager):
        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager

    @staticmethod
    def downsample_pose(pose, count=1):
        translation, scale, rotation = pose
        return translation / (2**count), scale / (2**count), rotation

    def find(self, image):
        '''
        Finds initial poses.
        :param image:
        :param level:
        :return:
        '''
        basic_poses = self._find_poses(image)
        return [basic_poses[i] for i in self.data_manager.selector]

    def _find_poses(self, image):
        self.top_jaw_line, self.lower_jaw_line = self._find_jaw_separation_line(self._crop_image_sides(image))

        upper_jaw_image = self.crop_upper_jaw(image, self.top_jaw_line)
        lower_jaw_image = self.crop_lower_jaw(image, self.lower_jaw_line)

        # Filter the image
        upper_jaw_image = Filter.process_image(upper_jaw_image, median_kernel=5, bilateral_kernel=17, bilateral_color=6)
        lower_jaw_image = Filter.process_image(lower_jaw_image, median_kernel=5, bilateral_kernel=17, bilateral_color=6)

        upper_jaw_image = self._convert_to_binary_image(upper_jaw_image)
        lower_jaw_image = self._convert_to_binary_image(lower_jaw_image)

        # Find the lines in the image
        upper_lines = self._find_hough_lines(upper_jaw_image, threshold=15)
        lower_lines = self._find_hough_lines(lower_jaw_image, threshold=15)

        # Filter out lines
        upper_lines = self._filter_lines(upper_lines, upper_jaw_image.shape, line_offset=6, max_line_gap=90)
        lower_lines = self._filter_lines(lower_lines, lower_jaw_image.shape, line_offset=2, max_line_gap=60)

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
        position5 = np.array((rho0+(rho1-rho0)/2+self.crop_sides_size, 90+self.lower_jaw_line))
        position6 = np.array((rho1+(rho2-rho1)/2+self.crop_sides_size, 90+self.lower_jaw_line))
        position7 = np.array((rho2+40+self.crop_sides_size, 90+self.lower_jaw_line))

        return [(position0, 48, 0.05),
                (position1, 55, 0.2),
                (position2, 55, 0.2),
                (position3, 48, 0.3),
                (position4, 40, 0),
                (position5, 38, -0.05),
                (position6, 38, -0.10),
                (position7, 40, -0.15)
                ]

    def _find_jaw_separation_line(self, image):
        '''
        Finds y coordinate of lines that separates upper and lower jaws.
        :param image:
        :return:
        '''
        y_histogram = cv2.reduce(image, 1, cv2.cv.CV_REDUCE_SUM, dtype=cv2.CV_32S)
        return self._get_valley_range(y_histogram)

    def _crop_image_sides(self, image):
        '''
        Crop image on from left and right side.
        :param image:
        :return:
        '''
        return image[:, self.crop_sides_size:image.shape[1]-self.crop_sides_size]

    def crop_upper_jaw(self, image, y_line):
        '''
        Crop image to upper jaw.
        :param image:
        :param y_line:
        :return:
        '''
        return image[y_line-self.crop_upper_jaw_top_size:y_line, self.crop_sides_size:image.shape[1]-self.crop_sides_size]

    def crop_lower_jaw(self, image, y_line):
        '''
        Crop image to lower jaw.
        :param image:
        :param y_line:
        :return:
        '''
        return  image[y_line: y_line+self.crop_lower_jaw_size, self.crop_sides_size:image.shape[1]-self.crop_sides_size]

    def _get_valley_range(self, histogram):
        '''
        Find range of valley in histogram by going to the sides from minimum until threshold is reached,
        used for seperating jaws.
        :param histogram: Sum of image rows.
        :return:
        '''
        threshold = 5000
        min_index = np.argmin(histogram)
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
        '''
        Converting image to the binary.
        :param image:
        :return:
        '''
        image = np.array(image, dtype=np.uint8)
        return cv2.threshold(image, 8, 255, cv2.THRESH_BINARY)[1]
        #return cv2.Canny(image, 25, 30)

    def _find_hough_lines(self, image, threshold=20):
        #self.lines = cv2.HoughLinesP(self.image, 1, np.pi/90, 5, None, 80, 40)
        lines = cv2.HoughLines(image, 1, 20*np.pi/180, threshold, 0,0)
        return lines

    def _filter_lines(self, lines, image_shape, line_offset=5, max_line_gap=60):
        '''
        Filter our the lines in the image - close lines and not vertical lines.
        :param lines:
        :param image_shape: Shape of the image.
        :param line_offset: Offset of line to the left.
        :param max_line_gap: Minimal threshold between lines, only one line within this threshold is retained.
        :return:
        '''
        mask = []
        # Filter only vertical lines
        for rho,theta in lines[0]:
                if (theta >= np.pi/180*0 and theta <= np.pi/180*self.max_angle) \
                        or (theta >= np.pi/180*(180-self.max_angle) and theta <= np.pi/180*180):
                    mask.append(True)
                else:
                    mask.append(False)
        mask = np.array(mask)
        lines = lines[0][mask]
        lines = sorted(lines, key=lambda item: item[0], reverse=True)

        #2 Delete lines close together, prefer vertical lines
        indices = []
        previous_rho = 0
        previous_ind = 0
        previous_theta = 0
        for i, line_par in enumerate(lines):
            rho,theta = line_par
            if (rho < self.side_lines_threshold) or (rho > image_shape[1]-self.side_lines_threshold):
                continue
            elif (rho < previous_rho+max_line_gap and rho > previous_rho-max_line_gap):
                if theta < previous_theta:
                    previous_ind = i
                    previous_theta = theta
            else:
                indices.append(previous_ind)
                previous_rho = rho
                previous_theta = theta
                previous_ind = i
        indices.pop(0)
        indices.append(previous_ind)
        lines = np.array(lines)
        lines = lines[indices]

        # Move lines more to the left to be in between teeth
        for i, line_par in enumerate(lines):
            rho, theta = line_par
            lines[i] = (rho-line_offset, theta)


        # Filter only 3 lines - Go from the middle to the sides
        middle = image_shape[1] / 2
        min_idx = 0
        min_dist = float('Inf')
        for i, line_par in enumerate(lines):
            rho, theta = line_par
            if np.abs(rho-middle) < min_dist:
                min_dist = np.abs(rho-middle)
                min_idx = i
        new_lines = lines[min_idx-1:min_idx+2]

        # Add lines if less than 3
        if new_lines.shape[0] != 3:
            rho, theta = lines[min_idx]
            lines = [(rho+max_line_gap, 0), (rho, theta), (rho-max_line_gap, 0)]
        else:
            lines = new_lines


        # Return sorted from left to right tooth
        lines = sorted(lines, key=lambda item: item[0])
        return np.array(lines)

