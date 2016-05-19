from copy import deepcopy

from src.radiograph import Radiograph

__author__ = "Ivan Sevcik"

class DataManager:
    number_of_radiographs = 14
    radiographs = None
    left_out_radiograph = None
    selector = None

    def __init__(self, leave_one_out=None):
        self.radiographs = list()
        self.selector = range(0, 8)

        for i in range(0, self.number_of_radiographs):
            radiograph = Radiograph()
            radiograph.load(i, True)

            if leave_one_out is not None and i == leave_one_out:
                self.left_out_radiograph = radiograph
                continue

            self.radiographs.append(radiograph)

    def get_all_teeth(self, make_copy=False):
        """
        Retrieves all teeth instances across all radiographs
        :param make_copy: If True, the instances will be deep-copied
        :return: All teeth instances
        """
        teeth = list()
        for r in self.radiographs:
            assert isinstance(r, Radiograph)
            teeth_from_one = [r._teeth[i] for i in self.selector]
            teeth.extend(deepcopy(teeth_from_one) if make_copy else teeth_from_one)

        return teeth

    def count_all_teeth(self):
        '''
        Count all teeth available.
        :return: teeth count
        '''
        return len(self.get_all_teeth())

    def get_tooth(self, radiograph_idx, tooth_idx, make_copy=False):
        '''
        Get tooth from radiograph.
        :param radiograph_idx: radiograph index
        :param tooth_idx: tooth index
        :param make_copy: Boolean whether to make a deep copy on return
        :return: instance of the tooth
        '''
        tooth = [self.radiographs[radiograph_idx]._teeth[i] for i in self.selector][tooth_idx]
        return deepcopy(tooth) if make_copy else tooth

    def get_tooth_from_all(self, total_tooth_idx, make_copy=False):
        '''
        Get tooth with index from all radiographs.
        :param total_tooth_idx: tooth index
        :param make_copy: Boolean whether to make a deep copy on return
        :return: teeth instances
        '''
        tooth = self.get_all_teeth()[total_tooth_idx]
        return deepcopy(tooth) if make_copy else tooth

    def get_all_teeth_from_radiograph(self, radiograph, make_copy=False):
        '''
        Get all incisor teeth from radiograph.
        :param radiograph: instance of radiograph
        :param make_copy: Boolean whether to make a deep copy on return
        :return: teeth instances
        '''
        teeth = [radiograph._teeth[i] for i in self.selector]
        return deepcopy(teeth) if make_copy else teeth

    def select_all_teeth(self):
        '''
        Set the selector filter to all 8 incisor teeth.
        '''
        self.selector = range(0, 8)

    def select_upper_jaw(self):
        '''
        Set the selector filter to all upper incisor teeth.
        '''
        self.selector = range(0, 4)

    def select_lower_jaw(self):
        '''
        Set the selector filter to all lower incosor teeth.
        :return:
        '''
        self.selector = range(4, 8)
