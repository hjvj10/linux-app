import threading
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, GObject
from ...utils import SubclassesMixin
from abc import abstractmethod
import subprocess
from protonvpn_nm_lib.core.subprocess_wrapper import subprocess as _subprocess


class BackgroundProcess(SubclassesMixin):
    """Abstract Widget Factory class."""

    @classmethod
    def factory(cls, threading_backend=None):
        try:
            _version = _subprocess.run(["gio", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
        except ValueError:
            _version = subprocess.run(["gio", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')

        _version = str(_version).strip("\n")
        subclasses_dict = cls._get_subclasses_dict("threading_backend")

        # run_in_thread is supported since 2.36 (https://docs.gtk.org/gio/callback.TaskThreadFunc.html),
        # but the method was only added later in 2.63.2, thus up to this version we should default to python threads
        if (threading_backend is None) or (_version < "2.63.2" and (threading_backend is None or threading_backend != "python")):
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


class CustomThread(threading.Thread):
    """Custom native python thread with callback."""
    def __init__(self, callback=None, *args, **kwargs):
        target = kwargs.pop("target")
        super(CustomThread, self).__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target

    def target_with_callback(self, *args, **kwargs):
        self.method(*args, **kwargs)
        if self.callback is not None:
            self.callback()


class PythonThreading(BackgroundProcess):
    threading_backend = "python"

    def __init__(self):
        self.process = None
        self.set_task_data = None

    def setup(self, target, cancellable=None, callback=None, callback_data=None, *args, **kwargs): # noqa
        self.process = CustomThread(
            target=target, callback=callback, args=args, kwargs=kwargs
        )
        self.process.daemon = True

    def start(self):
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

    def setup(self, target, cancellable=None, callback=None, callback_data=None, *args, **kwargs): # noqa
        self.process = Gio.Task.new(self, cancellable, callback, callback_data)
        self.process.set_task_data(self.__task_data)
        self.__func_to_run_in_thread = target

    def start(self):
        self.process.run_in_thread(self.__func_to_run_in_thread)
