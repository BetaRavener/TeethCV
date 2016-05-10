import numpy as np

from src.datamanager import DataManager

__author__ = "Ivan Sevcik"

class InitialPoseModel(object):
    data_manager = None

    def __init__(self, data_manager):
        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager

    @staticmethod
    def _find_basic_poses(image):
        return [(np.array((251, 405)), 40, 0),
                (np.array((345, 401)), 40, 0),
                (np.array((470, 393)), 40, 0),
                (np.array((561, 678)), 40, 0),
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
        Finds initial poses at given level
        :param image:
        :param level:
        :return:
        '''

        basic_poses = InitialPoseModel._find_basic_poses(image)

        return [basic_poses[i] for i in self.data_manager.selector]
