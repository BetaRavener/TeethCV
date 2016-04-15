from copy import deepcopy

from src.radiograph import Radiograph


class DataManager:
    number_of_radiographs = 14
    radiographs = None

    def __init__(self):
        self.radiographs = list()

        for i in range(0, self.number_of_radiographs):
            radiograph = Radiograph()
            radiograph.load(i, True)
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
            teeth.extend(deepcopy(r.teeth) if make_copy else r.teeth)

        return teeth

    def count_all_teeth(self):
        return len(self.get_all_teeth())

    def get_tooth(self, radiographIdx, toothIdx, make_copy=False):
        tooth = self.radiographs[radiographIdx].teeth[toothIdx]
        return deepcopy(tooth) if make_copy else tooth

    def get_tooth_from_all(self, total_tooth_idx, make_copy=False):
        tooth = self.get_all_teeth()[total_tooth_idx]
        return deepcopy(tooth) if make_copy else tooth
