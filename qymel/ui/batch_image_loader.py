import collections.abc as abc
import typing
import multiprocessing.pool
import threading

from .pyside_module import *


LoadedCallback = abc.Callable[[QImage], QImage]
CompletedCallback = abc.Callable[[QImage], None]
ErrorCallback = abc.Callable[[BaseException], None]

TCallback = typing.TypeVar('TCallback', LoadedCallback, CompletedCallback, ErrorCallback)


class ImageLoadingCallback(object):

    ERROR = 'ERROR'
    LOADED = 'LOADED'
    COMPLETED = 'COMPLETED'


class BatchImageLoader(QObject):

    loaded = Signal(int)
    completed = Signal()

    def __init__(self, parent: QObject|None = None) -> None:
        super(BatchImageLoader, self).__init__(parent)
        self.__file_paths: dict[int, str] = {}
        self.__images: dict[int, QImage|None] = {}
        self.__images_lock = threading.Lock()
        self.__callbacks: dict[str, list[abc.Callable[[QImage], QImage]]] = {}
        self.__pool = multiprocessing.pool.ThreadPool()

    def clear(self) -> None:
        self.__file_paths.clear()
        self.__images.clear()
        self.__callbacks.clear()

    def add_file(self, file_path: str) -> int:
        index = len(self.__file_paths) + 1
        self.__file_paths[index] = file_path
        self.__images[index] = None
        return index

    def add_callback(self, callback_id: str, callback: TCallback) -> None:
        callbacks = self.__callbacks.get(callback_id, [])
        callbacks.append(callback)
        self.__callbacks[callback_id] = callbacks

    def image(self, task_id: int) -> QImage|None:
        return self.__images.get(task_id)

    def load_async(self) -> multiprocessing.pool.AsyncResult:
        loaded_callbacks = self.__callbacks.get(ImageLoadingCallback.LOADED, [])
        completed_callbacks = self.__callbacks.get(ImageLoadingCallback.COMPLETED, [])
        error_callbacks = self.__callbacks.get(ImageLoadingCallback.ERROR, [])

        def _task_callback(_args: tuple[int, str]) -> None:
            _index, _filePath = _args
            self.__load_image(_index, _filePath, loaded_callbacks)

        def _callback(_) -> None:
            for on_completed in completed_callbacks:
                on_completed()
            self.completed.emit()

        def _error_callback(e: BaseException) -> None:
            for callback in error_callbacks:
                callback(e)

        return self.__pool.map_async(
            _task_callback,
            self.__file_paths.items(),
            callback=_callback,
            error_callback=_error_callback
        )

    def __load_image(self, index: int, file_path: str, on_loaded_callbacks: abc.Iterable[LoadedCallback]) -> None:
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
