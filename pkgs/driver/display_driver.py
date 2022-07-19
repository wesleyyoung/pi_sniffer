from abc import ABC, abstractmethod


class DisplayDriver(ABC):
    @abstractmethod
    def create_display(self):
        pass

    @abstractmethod
    def get_display(self):
        pass

    @abstractmethod
    def get_button_a(self):
        pass

    @abstractmethod
    def get_button_b(self):
        pass

    @abstractmethod
    def get_button_c(self):
        pass

    @abstractmethod
    def get_button_l(self):
        pass

    @abstractmethod
    def get_button_r(self):
        pass

    @abstractmethod
    def get_button_u(self):
        pass

    @abstractmethod
    def get_button_d(self):
        pass

    @abstractmethod
    def prepare_button(self, button):
        pass

    @abstractmethod
    def clear_display(self):
        pass
