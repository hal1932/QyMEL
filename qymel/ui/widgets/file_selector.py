import os

from ..pyside_module import *


__all__ = ['FileSelector']


class FileSelector(QWidget):

    ACCEPT_OPEN = 'ACCEPT_OPEN'
    ACCEPT_SAVE = 'ACCEPT_SAVE'

    TARGET_FILE = 'TARGET_FILE'
    TARGET_DIRECTORY = 'TARGET_DIRECTORY'

    selection_changed = Signal()

    @property
    def selected_paths(self) -> list[str]:
        text = self.__file_path.text()
        return text.split(os.pathsep) if os.pathsep in text else [text]

    @selected_paths.setter
    def selected_paths(self, value: list[str]) -> None:
        self.__file_path.setText(os.pathsep.join(value))

    @property
    def readonly(self) -> bool:
        return self.__file_path.isReadOnly()

    @readonly.setter
    def readonly(self, value: bool) -> None:
        self.__file_path.setReadOnly(value)

    def __init__(self, parent: QObject|None = None) -> None:
        super(FileSelector, self).__init__(parent)

        self.accept_mode = FileSelector.ACCEPT_OPEN
        self.target = FileSelector.TARGET_FILE
        self.caption = u'Select'
        self.name_filters = [u'All Files (*.*)']
        self.allow_multiple_selection = False
        self.initial_directory = None
        self.use_native_dialog = False

        self.__file_path = QLineEdit()

        button = QPushButton()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        button.setIcon(icon)
        button.setIconSize(QSize(12, 12))
        button.clicked.connect(self.__select_path)

        layout = QHBoxLayout()
        layout.addWidget(self.__file_path)
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def __select_path(self) -> None:
        dialog = QFileDialog(self)

        if self.accept_mode == FileSelector.ACCEPT_OPEN:
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        elif self.accept_mode == FileSelector.ACCEPT_SAVE:
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        else:
            raise RuntimeError('invalid accept_mode: {}'.format(self.accept_mode))

        if self.target == FileSelector.TARGET_FILE:
            if self.accept_mode == FileSelector.ACCEPT_SAVE:
                dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            else:
                if self.allow_multiple_selection:
                    dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
                else:
                    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        elif self.target == FileSelector.TARGET_DIRECTORY:
            dialog.setFileMode(QFileDialog.FileMode.Directory)
            dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        else:
            raise RuntimeError('invalid target: {}'.format(self.target))

        if len(self.selected_paths) > 0:
            last_path = self.selected_paths[0]
            dialog.setDirectory(os.path.dirname(last_path))
            dialog.selectFile(os.path.basename(last_path))
        else:
            if os.path.isdir(self.initial_directory or ''):
                dialog.setDirectory(self.initial_directory)
            else:
                default_directory = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0]
                dialog.setDirectory(default_directory)

        if not self.use_native_dialog:
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        dialog.setNameFilters(self.name_filters)
        dialog.setWindowTitle(self.caption)

        if dialog.exec_():
            print(dialog.selectedFiles())
            self.selected_paths = dialog.selectedFiles()
            self.selection_changed.emit()
