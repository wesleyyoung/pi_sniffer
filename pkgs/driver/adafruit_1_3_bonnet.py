from abc import ABC
import board
from digitalio import DigitalInOut, Direction, Pull
import adafruit_ssd1306
import busio
from pkgs.driver.display_driver import DisplayDriver
from PIL import Image, ImageDraw, ImageFont


i2c = busio.I2C(board.SCL, board.SDA)


class Adafruit13Bonnet(DisplayDriver, ABC):
    def __init__(self):
        self.display = self.create_display()

    def get_font(self):
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 9)

    def clear_display(self):
        self.display.fill(0)
        self.display.show()

    def get_display_width(self):
        return self.display.width

    def get_display_height(self):
        return self.display.height

    def create_display(self):
        # Create a "display" that represents the OLED screen
        return adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    def get_display(self):
        return self.display

    def create_image(self):
        width = self.get_display_width()
        height = self.get_display_height()
        return Image.new('1', (width, height))

    def create_drawable(self, image):
        return ImageDraw.Draw(image)

    def draw_image(self, image):
        self.display.image(image)
        self.display.show()

    def draw_blank_canvas(self):
        width = self.get_display_width()
        height = self.get_display_height()
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        self.draw_image(image)

    def get_button_a(self):
        return self.prepare_button(DigitalInOut(board.D5))

    def get_button_b(self):
        return self.prepare_button(DigitalInOut(board.D6))

    def get_button_c(self):
        return self.prepare_button(DigitalInOut(board.D4))

    def get_button_l(self):
        return self.prepare_button(DigitalInOut(board.D27))

    def get_button_r(self):
        return self.prepare_button(DigitalInOut(board.D23))

    def get_button_u(self):
        return self.prepare_button(DigitalInOut(board.D17))

    def get_button_d(self):
        return self.prepare_button(DigitalInOut(board.D22))

    def prepare_button(self, button):
        button.direction = Direction.INPUT
        button.pull = Pull.UP
        return button
