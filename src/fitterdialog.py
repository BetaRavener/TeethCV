from copy import deepcopy
from time import sleep

import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QColor, QPixmap, QPen, QBrush
from PyQt5.QtWidgets import QDialog, QFileDialog, QGraphicsSceneMouseEvent, QSlider

from gui.fitterdialog import Ui_fitterDialog
from src.ActiveShapeModel import ActiveShapeModel
from src.InitialPoseModel import InitialPoseModel
from src.MultiresFramework import MultiResolutionFramework, ResolutionLevel
from src.datamanager import DataManager
from src.filter import Filter
from src.interactivegraphicsscene import InteractiveGraphicsScene
from src.radiograph import Radiograph
from src.sampler import Sampler
from src.tooth import Tooth
from src.utils import toQImage, StopIterationToken

__author__ = "Ivan Sevcik"

class Animator(QThread):
    tooth_signal = pyqtSignal(Tooth, np.ndarray)
    level_signal = pyqtSignal(int)

    active_shape_model = None
    stop_token = None

    run_config = False
    run_last_level = None

    def __init__(self, asm):
        super(Animator, self).__init__()
        self.active_shape_model = asm
        self.stop_token = StopIterationToken()

    def __del__(self):
        # Notify worker that it's being destroyed so it can stop
        self.stop()

    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.

        if self.run_config:
            self.active_shape_model.run(self.stop_token, self.asm_run_callback)
            return

        while not self.stop_token.stop:
            self.active_shape_model.make_step()
            self.tooth_signal.emit(deepcopy(self.active_shape_model.current_tooth),
                                   deepcopy(self.active_shape_model.current_params))

    def asm_run_callback(self):
        level_change = False
        if self.run_last_level != self.active_shape_model.current_level:
            self.run_last_level = self.active_shape_model.current_level
            self.level_signal.emit(self.run_last_level)
            level_change = True

        self.tooth_signal.emit(deepcopy(self.active_shape_model.current_tooth),
                               deepcopy(self.active_shape_model.current_params))

        if level_change:
            sleep(1)

    def stop(self):
        self.stop_token.stop = True
        self.wait()


class FitterDialog(QDialog, Ui_fitterDialog):
    scene = None
    animator = None
    data_manager = None
    current_scale = 0
    current_sampling_level = 0
    current_phase = None
    active_shape_model = None
    pca = None
    initial_pose_model = None

    slider_resolution = 1000
    _scales = None

    show_sampled_positions = None

    radiograph_image = None

    @property
    def image(self):
        return self.active_shape_model.current_image

    @image.setter
    def image(self, img):
        self.active_shape_model.set_image_to_search(img)

    def __init__(self, data_manager, pca):
        super(FitterDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager
        self.pca = pca
        self.active_shape_model = ActiveShapeModel(self.data_manager, self.pca)
        self.initial_pose_model = InitialPoseModel(self.data_manager)

        self.scene = InteractiveGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.scene.clicked.connect(self._set_position)

        self.image = self.data_manager.radiographs[0].image
        self.radiograph_image = Filter.crop_image(self.data_manager.radiographs[0].image)

        self.openButton.clicked.connect(self._open_radiograph)

        self.zoomSlider.setRange(-10, 10)
        self.zoomSlider.setValue(self.current_scale)
        self.zoomSlider.valueChanged.connect(self.change_scale)

        self.levelSlider.setRange(1, MultiResolutionFramework.levels_count)
        self.levelSlider.setValue(self.current_sampling_level + 1)
        self.levelSlider.valueChanged.connect(self.user_change_level)

        self.stepButton.clicked.connect(self._perform_one_step_asm)
        self.animateButton.clicked.connect(self._animator_entry)

        self._scales = np.empty(self.pca.eigen_values.shape)
        for i, deviation in enumerate(self.pca.get_allowed_deviation()):
            slider = QSlider(Qt.Horizontal, self.paramsScrollAreaContents)
            slider.setRange(-self.slider_resolution, self.slider_resolution)
            # slider.valueChanged.connect(self.slider_moved)
            self.paramsScrollAreaContents.layout().addWidget(slider)
            self._scales[i] = deviation / self.slider_resolution

        self.show_sampled_positions = self.sampledPositionsCheckBox.isChecked()
        self.sampledPositionsCheckBox.stateChanged.connect(self.change_show_positions)

        self._redraw(self.active_shape_model.current_tooth)

    def closeEvent(self, event):
        if self.animator is not None:
            self.animator.stop()

    def _open_radiograph(self):
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory("./data/Radiographs")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Radiograph (*.tif)")
        if file_dialog.exec_() and len(file_dialog.selectedFiles()) == 1:
            if self.animator is not None:
                self.animator.stop()
            radiograph = Radiograph()
            radiograph.path_to_img = file_dialog.selectedFiles()[0]
            self.image = radiograph.image
            self.radiograph_image = Filter.crop_image(radiograph.image)
            self._redraw(self.active_shape_model.current_tooth)

    def change_scale(self, scale):
        self.current_scale = scale
        self.update_scale()

    def user_change_level(self, sampling_level):
        if not self.levelSlider.isEnabled():
            return

        self.current_sampling_level = sampling_level - 1
        self.active_shape_model.change_level(self.current_sampling_level)

        self.update_scale()
        self._redraw(self.active_shape_model.current_tooth)

    def change_show_positions(self):
        self.show_sampled_positions = self.sampledPositionsCheckBox.isChecked()
        self._redraw(self.active_shape_model.current_tooth)

    def model_change_level(self, sampling_level):
        self.current_sampling_level = sampling_level
        self.levelSlider.setValue(self.current_sampling_level + 1)

        self.update_scale()
        self._redraw(self.active_shape_model.current_tooth)

    def update_scale(self):
        real_scale = 1 + self.current_scale * (0.1 if self.current_scale >= 0 else 0.05)
        real_scale *= 2 ** self.current_sampling_level
        self.graphicsView.resetTransform()
        self.graphicsView.scale(real_scale, real_scale)

    def _set_position(self, mouse_event):
        assert isinstance(mouse_event, QGraphicsSceneMouseEvent)
        pos = mouse_event.scenePos()
        self.active_shape_model.set_up((pos.x(), pos.y()), 60 / (
            2 ** self.current_sampling_level))
        self._redraw(self.active_shape_model.current_tooth)

    def _animator_entry(self):
        if self.animator is None:
            self._animation_start()
        else:
            self.animator.stop()

    def _animation_start(self):
        self._disable_ui()

        self.animator = Animator(self.active_shape_model)

        self.animator.run_config = self.fullAsmCheckBox.isChecked()
        if self.animator.run_config:
            tooth_idx = self.startingPoseSpinBox.value()
            pose = self.initial_pose_model.find(self.radiograph_image)[tooth_idx]
            position, rotation, scale = pose
            self.active_shape_model.set_up(position, rotation, scale)

        self.animator.finished.connect(self._animator_end)
        self.animator.tooth_signal.connect(self.update_animation)
        self.animator.level_signal.connect(self.model_change_level)

        self.animator.start()

    def _animator_end(self):
        self.animateButton.setText("Animate")
        self.animator = None
        self.stepButton.setEnabled(True)
        self.fullAsmCheckBox.setEnabled(True)
        self.scene.setEnabled(True)
        self.levelSlider.setEnabled(True)

    def _disable_ui(self):
        self.current_phase = None
        self.animateButton.setText("Stop")
        self.stepButton.setEnabled(False)
        self.fullAsmCheckBox.setEnabled(False)
        self.scene.setEnabled(False)
        self.levelSlider.setEnabled(False)

    def update_animation(self, tooth, params):
        self._set_sliders_from_params(params)
        self._redraw(tooth)

    def _focus_view(self, size):
        rect = QRectF(0, 0, size[0], size[1])
        self.scene.setSceneRect(rect)

    def _redraw(self, tooth, normalize=True):
        self.scene.clear()

        img = self.image.copy()

        if normalize:
            img = (img / img.max()) * 255

        # Draw sampled positions to image
        if self.show_sampled_positions and tooth is not None:
            resolution_level = self.active_shape_model.get_current_level()
            assert isinstance(resolution_level, ResolutionLevel)
            all_sample_positions = []
            Sampler.sample(tooth, img, resolution_level.landmark_model.m, False, all_sample_positions)
            for point_sample_positions in all_sample_positions:
                for x, y in point_sample_positions:
                    img[y, x] = 255

        # Draw image
        qimg = toQImage(img.astype(np.uint8))
        self.scene.addPixmap(QPixmap.fromImage(qimg))

        # Draw initial positions
        init_poses = self.initial_pose_model.find(self.radiograph_image)
        for pose in init_poses:
            position, scale, rotation = InitialPoseModel.downsample_pose(pose, self.current_sampling_level)
            self.scene.addEllipse(position[0] - 2, position[1] - 2, 4, 4,
                                  pen=QPen(QColor.fromRgb(0, 0, 255)), brush=QBrush(QColor.fromRgb(0, 0, 255)))

        # Draw tooth from active shape model
        if tooth is not None:
            tooth.outline_pen = QPen(QColor(255, 0, 0))
            tooth.draw(self.scene, True, True)

        # Set generated scene into the view
        self._focus_view((qimg.width(), qimg.height()))

    def _perform_one_step_asm(self):
        if self.current_phase is None:
            self.current_phase = 0
        else:
            self.current_phase = (self.current_phase + 1) % 2

        self.active_shape_model.make_step(self.current_phase)
        self.update_animation(deepcopy(self.active_shape_model.current_tooth),
                              deepcopy(self.active_shape_model.current_params))

    def _get_all_sliders(self):
        sliders = list()
        for i in range(0, self.paramsScrollAreaContents.layout().count()):
            item = self.paramsScrollAreaContents.layout().itemAt(i).widget()
            if isinstance(item, QSlider):
                sliders.append(item)

        return sliders

    def _set_sliders_from_params(self, params):
        if params is None:
            return

        slider_values = params / self._scales
        self.ignore_sliders = True
        for i, slider in enumerate(self._get_all_sliders()):
            slider.setValue(int(slider_values[i]))
        self.ignore_sliders = False


