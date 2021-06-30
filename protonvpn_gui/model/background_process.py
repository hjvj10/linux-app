import threading
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, GObject
from ..utils import SubclassesMixin
from abc import abstractmethod


class BackgroundProcess(SubclassesMixin):
    """Abstract Widget Factory class."""

    @classmethod
    def get(cls, threading_backend=None):
        subclasses_dict = cls._get_subclasses_dict("threading_backend")
        if threading_backend is None:
            return subclasses_dict["python"]()

        return subclasses_dict[threading_backend]()

    @classmethod
    @abstractmethod
    def start():
        pass


class PythonThreading(BackgroundProcess):
    threading_backend = "python"

    def __init__(self):
        self.process = None
        self.set_task_data = None

    def setup(self, target_method, *args, **kwargs):
        self.process = threading.Thread(
            target=target_method, args=args, kwargs=kwargs
        )
        self.process.daemon = True

    def start(self, *args):
        self.process.start()


class GTaskThreading(BackgroundProcess, GObject.GObject):
    threading_backend = "gtask"

    def __init__(self):
        GObject.Object.__init__(self)
        self.process = None
        self.__task_data = None

    @property
    def task_data(self):
        return self.__task_data

    @task_data.setter
    def task_data(self, newvalue):
        if self.process and (isinstance(newvalue, int) or newvalue is None):
            self.process.set_task_data(newvalue)

    def setup(self, cancellable=None, callback=None, callback_data=None):
        self.process = Gio.Task.new(self, cancellable, callback, callback_data)

    def start(self, func_to_run_in_thread):
        self.process.run_in_thread(func_to_run_in_thread)
