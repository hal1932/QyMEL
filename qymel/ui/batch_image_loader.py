# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import multiprocessing.pool
import threading

from .pyside_module import *


class ImageLoadingCallback(object):

    ERROR = 'ERROR'
    LOADED = 'LOADED'
    COMPLETED = 'COMPLETED'


class BatchImageLoader(QObject):

    loaded = Signal(int)
    completed = Signal()

    def __init__(self, parent=None):
        # type: (QObject) -> NoReturn
        super(BatchImageLoader, self).__init__(parent)
        self.__file_paths = {}  # type: Dict[int, str]
        self.__images = {}  # type: Dict[int, Optional[QImage]]
        self.__images_lock = threading.Lock()
        self.__callbacks = {}  # type: Dict[str, List[Callable[[QImage], QImage]]]
        self.__pool = multiprocessing.pool.ThreadPool()

    def clear(self):
        # type: () -> NoReturn
        self.__file_paths.clear()
        self.__images.clear()
        self.__callbacks.clear()

    def add_file(self, file_path):
        # type: (str) -> int
        index = len(self.__file_paths) + 1
        self.__file_paths[index] = file_path
        self.__images[index] = None
        return index

    def add_callback(self, callback_id, callback):
        # type: (str, Callable[[QImage], QImage]) -> None
        callbacks = self.__callbacks.get(callback_id, [])
        callbacks.append(callback)
        self.__callbacks[callback_id] = callbacks

    def image(self, task_id):
        # type: (int) -> Optional[QImage]
        return self.__images.get(task_id)

    def load_async(self):
        # type: () -> multiprocessing.pool.AsyncResult
        error_callbacks = self.__callbacks.get(ImageLoadingCallback.ERROR, [])
        loaded_callbacks = self.__callbacks.get(ImageLoadingCallback.LOADED, [])
        completed_callbacks = self.__callbacks.get(ImageLoadingCallback.COMPLETED, [])

        def _task_callback(_args):
            # type: (Tuple[int, str]) -> NoReturn
            _index, _filePath = _args
            self.__load_image(_index, _filePath, loaded_callbacks)

        def _callback(_):
            for on_completed in completed_callbacks:
                on_completed()
            self.completed.emit()

        # def _error_callback(e):
        #     for callback in error_callbacks:
        #         callback(e)

        return self.__pool.map_async(
            _task_callback,
            self.__file_paths.items(),
            callback=_callback,
            # errorCallback=_error_callback
        )

    def __load_image(self, index, file_path, on_loaded_callbacks):
        # type: (int, str, List[Callable[[QImage], QImage]]) -> None
        image = QImage(file_path)
        with self.__images_lock:
            self.__images[index] = image

        new_image = image
        for on_loaded in on_loaded_callbacks:
            new_image = on_loaded(new_image)

        if new_image != image:
            with self.__images_lock:
                self.__images[index] = new_image

        self.loaded.emit(index)
