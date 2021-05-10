from .abstract_widget_factory import WidgetFactory
from abc import abstractmethod


class AbstractButtonFactory(WidgetFactory):
    """Abstract Button Factory class."""
    abstract_buton_factory = "abstract_buton_factory"

    @classmethod
    def factory(cls, widget):
        try:
            return cls.button(widget)
        except (KeyError, NotImplementedError):
            pass

        try:
            return cls.link(widget)
        except (KeyError, NotImplementedError):
            pass

        raise NotImplementedError("Provided button is not implemented")

    @classmethod
    def button(cls, widget):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "buttonfactory" == subclass.__name__.lower():
                return subclass.factory(widget)

        raise NotImplementedError("Button not implemented")

    @classmethod
    def link(cls, widget):
        subclasses = cls._get_subclasses_with("concrete_factory")
        for subclass in subclasses:
            if "linkbuttonfactory" == subclass.__name__.lower():
                return subclass.factory(widget)

        raise NotImplementedError("Link button not implemented")

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
