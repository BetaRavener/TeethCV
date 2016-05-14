from threading import Thread

import numpy as np
import sys
from PyQt5.QtGui import QPixmap, QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QApplication

from src.ActiveShapeModel import ActiveShapeModel
from src.InitialPoseModel import InitialPoseModel
from src.StatisticalShapeModel import StatisticalShapeModel
from src.datamanager import DataManager
from src.simplescenewindow import SimpleSceneWindow
from src.tooth import Tooth
from src.utils import toQImage

__author__ = "Ivan Sevcik"


def process_jaw(data_manager):
    '''
    Performs learning from data and search by ASM for jaw currently selected in data manager
    :param data_manager: Data manager supplying training data and images
    :return: A set of teeth that were found in image
    '''
    pca = StatisticalShapeModel.create(data_manager)
    pca.threshold(0.9)
    asm = ActiveShapeModel(data_manager, pca)

    reference_radiograph = data_manager.left_out_radiograph
    reference_image = reference_radiograph.image

    # Set image for ASM and it will perform all the filtering
    asm.set_image_to_search(reference_image)

    # Find initial poses in the filtered image at level 0
    first_resolution_level = asm.multi_resolution_framework.get_level(0)
    first_resolution_image = first_resolution_level.image
    initial_pose_model = InitialPoseModel(data_manager)
    initial_poses = initial_pose_model.find(first_resolution_image)

    # Prepare list for gathering results
    results = []

    # For each initial pose perform asm
    for i, (position, scale, rotation) in enumerate(initial_poses):
        print "Performing search #%d." % i
        asm.set_up(position, scale, rotation)
        result = asm.run()

        # Save the result to list
        results.append(result)

    print "All searching done."
    return results


def measure_errors(data_manager, search_results):
    '''
    Compares the reference teeth with those found by algorithm
    :param data_manager: Data manager supplying reference data
    :param search_results: Teeth that were found by search
    :return: Average and maximum error for each tooth
    '''
    reference_radiograph = data_manager.left_out_radiograph
    reference_teeth = data_manager.get_all_teeth_from_radiograph(reference_radiograph, True)

    errors = []
    for i in range(0, len(search_results)):
        error_tuple = reference_teeth[i].measure_error(search_results[i])
        errors.append(error_tuple)

    return errors


def print_errors(errors):
    # Print header
    print "Tooth # | Avg error | Max error"
    print "-" * 31
    for i in range(0, len(errors)):
        avg_error, max_error = errors[i]
        print "{0: >7} | {1: >9.6} | {2: >9.6}".format(i, avg_error, max_error)


def visualize_data(window, data_manager, search_results):
    # Scene where everything will be drawn
    scene = QGraphicsScene()

    reference_radiograph = data_manager.left_out_radiograph
    reference_image = reference_radiograph.image
    reference_teeth = data_manager.get_all_teeth_from_radiograph(reference_radiograph)

    # Draw reference image first
    qimg = toQImage(reference_image.astype(np.uint8))
    scene.addPixmap(QPixmap.fromImage(qimg))

    for tooth in reference_teeth:
        assert isinstance(tooth, Tooth)
        tooth.outline_pen = QPen(QColor.fromRgb(0, 0, 255))
        tooth.draw(scene)

    if search_results is not None:
        for tooth in search_results:
            assert isinstance(tooth, Tooth)
            tooth.draw(scene)

    window.set_scene(scene)


def export_data(data_manager, search_results):
    assert isinstance(data_manager, DataManager)
    reference_radiograph = data_manager.left_out_radiograph
    reference_image = reference_radiograph.image

    for i, tooth in enumerate(search_results):
        assert isinstance(tooth, Tooth)
        real_tooth_idx = data_manager.selector[i] + 1
        tooth.export_landmarks("loo-%d" % real_tooth_idx)
        tooth.export_segmentation("loo-%d" % real_tooth_idx, reference_image.shape)

# Create main app
myApp = QApplication(sys.argv)
window = SimpleSceneWindow()

leave_out = int(input("Enter radiograph to leave out (1-14): ")) - 1
if leave_out > 14 or leave_out < 0:
    print 'Invalid selection'
    exit()

export_flag = (raw_input("Should the result be exported? (n/y): ") == "y")

data_manager = DataManager(leave_out)
#visualize_data(window, data_manager, None)
#window.show()
#myApp.exec_()

print "Processing upper jaw."
data_manager.select_upper_jaw()
upper_jaw_teeth = process_jaw(data_manager)

print "Results upper jaw."
errors = measure_errors(data_manager, upper_jaw_teeth)
print_errors(errors)
print ""
visualize_data(window, data_manager, upper_jaw_teeth)
window.show()
myApp.exec_()
if export_flag:
    export_data(data_manager, upper_jaw_teeth)

print "Processing lower jaw."
data_manager.select_lower_jaw()
lower_jaw_teeth = process_jaw(data_manager)

print "Results lower jaw."
errors = measure_errors(data_manager, lower_jaw_teeth)
print_errors(errors)
print ""
visualize_data(window, data_manager, lower_jaw_teeth)
window.show()
myApp.exec_()
if export_flag:
    export_data(data_manager, lower_jaw_teeth)