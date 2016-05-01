import numpy as np


class InitialPoseModel(object):
    def __init__(self):
        pass

    @staticmethod
    def _find_basic_poses(image):
        return [(np.array((251, 405)), 40, 0),
                (np.array((345, 401)), 40, 0),
                (np.array((470, 393)), 40, 0),
                (np.array((561, 378)), 40, 0)
                ]

    @staticmethod
    def _downsample_pose(pose):
        translation, scale, rotation = pose
        return translation / 2, scale / 2, rotation

    @staticmethod
    def find(image, level=0):
        '''
        Finds initial poses at given level
        :param image:
        :param level:
        :return:
        '''

        basic_poses = InitialPoseModel._find_basic_poses(image)
        for i in range(0, level):
            basic_poses = [InitialPoseModel._downsample_pose(x) for x in basic_poses]

        return basic_poses
