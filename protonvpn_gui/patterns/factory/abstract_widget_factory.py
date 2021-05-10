from abc import ABCMeta, abstractmethod, abstractclassmethod
from ...utils import SubclassesMixin


class WidgetFactory(SubclassesMixin, metaclass=ABCMeta):
    """Abstract Widget Factory class."""

    @classmethod
    def button(cls, widget):
        subclasses = cls._get_subclasses_with("abstract_buton_factory")
        for subclass in subclasses:
            if "abstractbuttonfactory" == subclass.__name__.lower():
                return subclass.factory(widget)

    @classmethod
    def grid(cls, widget):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "gridfactory" == subclass.__name__.lower():
                return subclass.factory(widget)

        raise NotImplementedError("Grid not implemented")

    @classmethod
    def revealer(cls, widget):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "revealerfactory" == subclass.__name__.lower():
                return subclass.factory(widget)

        raise NotImplementedError("Revealer not implemented")

    @classmethod
    def image(cls, widget, extra_arg=None):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "imagefactory" == subclass.__name__.lower():
                return subclass.factory(widget, extra_arg)

        raise NotImplementedError("Revealer not implemented")

    @classmethod
    def label(cls, widget, label_text=None):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "labelfactory" == subclass.__name__.lower():
                return subclass.factory(widget, label_text)

        raise NotImplementedError("Revealer not implemented")

    @classmethod
    def textview(cls, widget, text=""):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "textviewfactory" == subclass.__name__.lower():
                return subclass.factory(widget, text)

        raise NotImplementedError("Revealer not implemented")

    @abstractclassmethod
    def factory():
        """Factory method to produce products."""

    @property
    @abstractmethod
    def widget(self):
        """Get widget object."""
        pass

    @property
    @abstractmethod
    def context():
        pass

    @property
    @abstractmethod
    def show():
        """Get widget visibility."""
        pass

    @show.setter
    @abstractmethod
    def show():
        """Set widget visibiltiy."""
        pass

    @abstractmethod
    def add_class():
        """Add CSS class."""
        pass

    @abstractmethod
    def remove_class():
        """Remove CSS class."""
        pass

    @abstractmethod
    def has_class():
        """Check if widget has CSS class."""
        pass

    @abstractmethod
    def remove_all_classes():
        """Remove all CSS classes."""
        pass

    @abstractmethod
    def replace_all_by():
        """Replace all CSS classes with a specific one."""
        pass

    @abstractmethod
    def replace_old_class_with_new_class():
        """Replace specified CSS class(es) with specificied class(es)."""
        pass
