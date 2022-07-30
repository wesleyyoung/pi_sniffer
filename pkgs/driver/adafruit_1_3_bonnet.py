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
        self.image = self.create_image()
        self.drawable = self.create_drawable(self.image)
        self.button_A = self.register_button(DigitalInOut(board.D5))
        self.button_B = self.register_button(DigitalInOut(board.D6))
        self.button_C = self.register_button(DigitalInOut(board.D4))
        self.button_U = self.register_button(DigitalInOut(board.D17))
        self.button_D = self.register_button(DigitalInOut(board.D22))
        self.button_L = self.register_button(DigitalInOut(board.D27))
        self.button_R = self.register_button(DigitalInOut(board.D23))
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 9)

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

    def get_drawable(self):
        return self.drawable

    def get_font(self):
        return self.font

    def get_image(self):
        return self.image

    def create_image(self):
        width = self.get_display_width()
        height = self.get_display_height()
        return Image.new('1', (width, height))

    def create_drawable(self, image):
        return ImageDraw.Draw(image)

    def draw_image(self, image):
        self.display.image(image)
        self.display.show()

    def show(self):
        self.draw_image(self.image)
        self.display.show()

    def set_blank_canvas(self):
        width = self.get_display_width()
        height = self.get_display_height()
        self.image = Image.new('1', (width, height))
        self.drawable = ImageDraw.Draw(self.image)
        self.drawable.rectangle((0, 0, width, height), outline=0, fill=0)

    def draw_blank_canvas(self):
        width = self.get_display_width()
        height = self.get_display_height()
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        self.draw_image(image)

    def draw_text(self, x, y, text, fill=1):
        self.drawable.text((x, y), text, font=self.font, fill=fill)

    def draw_rect(self, xy, outline=1, fill=1):
        self.drawable.rectangle(xy, outline=outline, fill=fill)

    def draw_line(self, xy, fill=1):
        self.drawable.line(xy, fill=fill)

    def get_button_a(self):
        return self.button_A

    def get_button_b(self):
        return self.button_B

    def get_button_c(self):
        return self.button_C

    def get_button_l(self):
        return self.button_L

    def get_button_r(self):
        return self.button_R

    def get_button_u(self):
        return self.button_U

    def get_button_d(self):
        return self.button_D

    def is_btn_pressed(self, button):
        return not button.value

    def is_a_pressed(self):
        return self.is_btn_pressed(self.button_A)

    def is_b_pressed(self):
        return self.is_btn_pressed(self.button_B)

    def is_c_pressed(self):
        return self.is_btn_pressed(self.button_C)

    def is_up_pressed(self):
        return self.is_btn_pressed(self.button_U)

    def is_down_pressed(self):
        return self.is_btn_pressed(self.button_D)

    def is_left_pressed(self):
        return self.is_btn_pressed(self.button_L)

    def is_right_pressed(self):
        return self.is_btn_pressed(self.button_R)

    def register_button(self, button):
        button.direction = Direction.INPUT
        button.pull = Pull.UP
        return button
