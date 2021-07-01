import threading
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, GObject
from ...utils import SubclassesMixin
from abc import abstractmethod


class BackgroundProcess(SubclassesMixin):
    """Abstract Widget Factory class."""

    @classmethod
    def factory(cls, threading_backend=None):
        subclasses_dict = cls._get_subclasses_dict("threading_backend")
        if threading_backend is None:
            return subclasses_dict["python"]()

        return subclasses_dict[threading_backend]()

    @classmethod
    @abstractmethod
    def setup():
        pass

    @classmethod
    @abstractmethod
    def start():
        pass


class PythonThreading(BackgroundProcess):
    threading_backend = "python"

    def __init__(self):
        self.process = None
        self.set_task_data = None

    def setup(self, target, *args, **kwargs):
        self.process = threading.Thread(
            target=target, args=args, kwargs=kwargs
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
        self.__func_to_run_in_thread = None

    @property
    def task_data(self):
        return self.__task_data

    @task_data.setter
    def task_data(self, newvalue):
        if not isinstance(newvalue, int) or newvalue is None:
            raise TypeError("Only int and None types are accepted")

        self.__task_data = newvalue

    def setup(self, target=None, cancellable=None, callback=None, callback_data=None):
        self.process = Gio.Task.new(self, cancellable, callback, callback_data)
        self.__func_to_run_in_thread = target

    def start(self, func_to_run_in_thread=None):
        if not func_to_run_in_thread and not self.__func_to_run_in_thread:
            raise Exception("Threaded function has not been passed")

        self.process.set_task_data(self.__task_data)

        to_run_in_thread = self.__func_to_run_in_thread
        if func_to_run_in_thread:
            to_run_in_thread = func_to_run_in_thread

        self.process.run_in_thread(to_run_in_thread)
