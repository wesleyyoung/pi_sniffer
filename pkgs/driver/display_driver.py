from abc import ABC, abstractmethod


class DisplayDriver(ABC):
    @abstractmethod
    def get_font(self):
        pass

    @abstractmethod
    def create_display(self):
        pass

    @abstractmethod
    def get_display(self):
        pass

    @abstractmethod
    def get_display_width(self):
        pass

    @abstractmethod
    def get_display_height(self):
        pass

    @abstractmethod
    def draw_blank_canvas(self):
        pass

    @abstractmethod
    def create_image(self):
        pass

    @abstractmethod
    def create_drawable(self, image):
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
    def register_button(self, button):
        pass

    @abstractmethod
    def clear_display(self):
        pass
