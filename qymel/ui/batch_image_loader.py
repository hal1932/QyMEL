# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import multiprocessing.pool
import threading

# from .pyside_module import *
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
except ImportError:
    from PySide.QtGui import *
    from PySide.QtCore import *

from .dispatcher import *


class ImageLoadItem(object):

    def __init__(self, index, file_path, image):
        # type: (int, str, Optional[QImage]) -> NoReturn
        self.index = index
        self.file_path = file_path
        self.image = image


class ImageLoadingCallback(object):

    ERROR = 'error'
    LOADED = 'loaded'
    COMPLETED = 'completed'


class BatchImageLoader(QObject):
    """
    loader = BatchImageLoader()
    task_id1 = loader.add_file_path('test1.png')
    task_id2 = loader.add_file_path('test2.png')
    loader.add_callback(ImageLoadingCallback.LOADED, lambda img: img.scaled(100, 100))
    if wait:
        loader.load()
        image1 = loader.image(task_id1)
        image2 = loader.image(task_id2)
    if async:
        def load_complete():
            image1 = loader.image(task_id1)
            image2 = loader.image(task_id2)
        loader.completed.connect(load_complete)
        loader.load_async()
    """

    loaded = Signal(int)
    completed = Signal()

    def __init__(self, parent=None):
        # type: (QObject) -> NoReturn
        super(BatchImageLoader, self).__init__(parent)
        self.__file_paths = {}  # type: Dict[int, str]
        self.__images = {}  # type: Dict[int, Optional[QImage]]
        self.__callbacks = {}  # type: Dict[str, List[Callable[[QImage], QImage]]]
        self.__pool = multiprocessing.pool.ThreadPool()

    def add_file_path(self, file_path):
        # type: (str) -> int
        index = len(self.__file_paths) + 1
        self.__file_paths[index] = file_path
        self.__images[index] = None
        return index

    def add_callback(self, callback_id, callback):
        # type: (str, Callable[[QPixmap], QPixmap]) -> None
        callbacks = self.__callbacks.get(callback_id, [])
        callbacks.append(callback)
        self.__callbacks[callback_id] = callbacks

    def image(self, task_id):
        # type: (int) -> Optional[QImage]
        return self.__images.get(task_id)

    def load(self):
        error_callbacks = self.__callbacks.get(ImageLoadingCallback.ERROR, [])
        loaded_callbacks = self.__callbacks.get(ImageLoadingCallback.LOADED, [])
        completed_callbacks = self.__callbacks.get(ImageLoadingCallback.COMPLETED, [])

        def _task_callback(_item):
            _index, _file_path = _item
            try:
                self.__load_image(_index, _file_path, loaded_callbacks)
            except Exception as e:
                for callback in error_callbacks:
                    Dispatcher.begin_invoke(callback, e)

        self.__pool.map(_task_callback, self.__file_paths.items())

        for on_completed in completed_callbacks:
            on_completed()
        self.completed.emit()

    def load_async(self):
        error_callbacks = self.__callbacks.get(ImageLoadingCallback.ERROR, [])
        loaded_callbacks = self.__callbacks.get(ImageLoadingCallback.LOADED, [])
        completed_callbacks = self.__callbacks.get(ImageLoadingCallback.COMPLETED, [])

        def _task_callback(_args):
            # type: (Tuple[int, str]) -> NoReturn
            _index, _file_path = _args
            self.__load_image(_index, _file_path, loaded_callbacks)

        def _callback(_):
            for on_completed in completed_callbacks:
                on_completed()
            self.completed.emit()

        def _error_callback(e):
            for callback in error_callbacks:
                callback(e)

        self.__pool.map_async(_task_callback, self.__file_paths.items(), callback=_callback, error_callback=_error_callback)

    def __load_image(self, index, file_path, on_loaded_callbacks):
        # type: (int, str, List[Callable[[QImage], QImage]]) -> None
        image = QImage(file_path)
        for on_loaded in on_loaded_callbacks:
            image = on_loaded(image)
        self.__images[index] = image
        self.loaded.emit(index)
        raise RuntimeError()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv or [])

    widget = QWidget()
    layout = QHBoxLayout()
    widget.setLayout(layout)
    widget.show()

    loader = BatchImageLoader()
    task_ids = [
        loader.add_file_path('C:/tmp/test111.png'),
        loader.add_file_path('C:/tmp/test22.png'),
    ]
    loader.add_callback(ImageLoadingCallback.LOADED, lambda img: img.scaled(100, 100))
    loader.add_callback(ImageLoadingCallback.ERROR, lambda e: QMessageBox.critical(None, 'error', str(e)))

    load_async = False

    if load_async:
        def loaded(task_id):
            image = loader.image(task_id)
            label = QLabel()
            label.setPixmap(QPixmap(image))
            layout.addWidget(label)

        def load_complete():
            QMessageBox.information(None, 'complete!!', '')

        loader.loaded.connect(loaded)
        loader.completed.connect(load_complete)
        loader.load_async()
    else:
        loader.load()
        for task_id in task_ids:
            image = loader.image(task_id)
            print(image)
            label = QLabel()
            label.setPixmap(QPixmap(image))
            layout.addWidget(label)

    sys.exit(app.exec_())
