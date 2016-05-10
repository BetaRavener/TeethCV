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
        return len(self.get_all_teeth())

    def get_tooth(self, radiograph_idx, tooth_idx, make_copy=False):
        tooth = [self.radiographs[radiograph_idx]._teeth[i] for i in self.selector][tooth_idx]
        return deepcopy(tooth) if make_copy else tooth

    def get_tooth_from_all(self, total_tooth_idx, make_copy=False):
        tooth = self.get_all_teeth()[total_tooth_idx]
        return deepcopy(tooth) if make_copy else tooth

    def get_all_teeth_from_radiograph(self, radiograph, make_copy=False):
        teeth = [radiograph._teeth[i] for i in self.selector]
        return deepcopy(teeth) if make_copy else teeth

    def select_all_teeth(self):
        self.selector = range(0, 8)

    def select_upper_jaw(self):
        self.selector = range(0, 4)

    def select_lower_jaw(self):
        self.selector = range(4, 8)
