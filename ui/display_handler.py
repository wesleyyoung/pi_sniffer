from multiprocessing import Process, Manager
import time
import board
import busio
import subprocess
import adafruit_ssd1306
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
from pkgs.wifi_client.wifi_client_service import WifiClientService
from pkgs.wifi_ap.wifi_ap_service import WifiApService
from pkgs.watchdog.watchdog_service import WatchdogService
from pkgs.runtime.runtime_service import RuntimeService
from pkgs.pages.system_view import do_system_view
from pkgs.pages.status_view import do_status_view
from pkgs.pages.overview_view import do_overview
from pkgs.pages.ant_view import do_ant_view
from pkgs.pages.gps_view import do_gps_view
from pkgs.pages.client_view import do_client_view
from pkgs.pages.ap_view import do_ap_view
from pkgs.pages.lock_view import do_lock_screen

###
# This monolithic madness is the entire UI of pi sniffer. It communicates with
# the pi_sniffer engine over UDP and with Kismet over TCP. It issues various
# shell commands in order to interact with the system. It checks to see if the
# UI needs repainting every 0.1ish seconds. An enterprising individual might
# break this thing up.
###

###
# Hooray for globals!
###

# Socket endpoint address
socket_ip = "127.0.0.1"

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create a "display" that represents the OLED screen
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Input pins
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP

# views
status_view = 0
overview = 1
ap_view = 2
client_view = 3
antenna = 4
system_view = 5
gps_view = 6
lock_screen = 7
rotate = 8  # place holder

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

# current view
current_view = status_view

# lock controls
locked = False

# last update time
last_update = 0
last_stats = None

# the font all text writing will use
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 9)

##
# Services
##
runtime_service = RuntimeService()
watchdog_service = WatchdogService()


###
# Globals over. I am appropriately embarrassed.
###

###
# Have the client attempt to rotate to the next screen
###
def check_view():
    global current_view

    # Right joystick controls screen movement
    if not button_R.value:
        # move to the next screen
        current_view = current_view + 1
        current_view = current_view % rotate

    # Left joystick controls screen movement too
    elif not button_L.value:
        if current_view == 0:
            current_view = lock_screen
        else:
            current_view = current_view - 1


def refresh_data(ap_service, client_service):
    while True:
        try:
            if runtime_service.is_sniffer_running():
                ap_service.refresh_ap_list()
                client_service.refresh_clients()
            else:
                pass
        except Exception as e:
            pass
        time.sleep(6)


def is_no_input_given():
    return button_A.value and button_B.value and button_U.value and button_D.value and button_L.value and button_R.value


def main_event_loop(ap_service, client_service):
    global last_update
    global locked
    global width
    global height
    global image
    global draw
    while True:
        if locked:
            # the user can lock the display in the lock screen. If they have, don't
            # do any other UI processing. We will have to still do the watch dog
            # logic though
            if not button_A.value and not button_U.value:
                locked = False
            else:
                watchdog_service.set_current_time(time.time())
                watchdog_service.do_watchdog()
                time.sleep(0.1)
                continue

        # If no input
        if is_no_input_given():
            if (time.time() * 1000) - (last_update * 1000) <= 1500:
                continue

        # check if the user is changing the view
        check_view()

        # see if we should be refreshing
        watchdog_service.set_current_time(time.time())
        if (watchdog_service.get_current_time() - 6) > last_update:
            watchdog_service.do_watchdog()

        # we might draw! Create a blank canvas
        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        try:
            # which view to draw to the screen
            if current_view == status_view:
                if not do_status_view(button_A, button_B, draw, font, width, runtime_service):
                    # user has requested shutdown
                    break
            elif current_view == overview:
                do_overview(draw, width, font, height)
            elif current_view == antenna:
                do_ant_view(button_B, button_U, button_D, draw, width, height, font)
            elif current_view == system_view:
                do_system_view(draw, font, width)
            elif current_view == gps_view:
                do_gps_view(draw, width, font)
            elif current_view == client_view:
                do_client_view(button_A, button_B, button_U, button_D, draw, width, height, font, ap_service,
                               client_service)
            elif current_view == ap_view:
                do_ap_view(button_A, button_U, button_D, draw, width, height, font, ap_service)
            elif current_view == lock_screen:
                do_lock_screen(button_B, draw, width, font)
            else:
                print("oh no! Why are we here?")
        except Exception as e:
            print('Error displaying page', e)

        last_update = time.time()
        disp.image(image)
        disp.show()

        time.sleep(0.01)


def main():
    # ensure the echo is disabled on the gps tty. Really annoying this needs to be done.
    subprocess.run(["stty", "-F", "/dev/ttyACM0", "-echo"])

    # kill hdmi. power saving.
    subprocess.run(["/usr/bin/tvservice", "-o"])

    # Clear display.
    disp.fill(0)
    disp.show()

    disp.fill(0)
    disp.show()

    with Manager() as manager:
        client_service = WifiClientService()
        ap_service = WifiApService()
        ap_service.aps = manager.dict()
        client_service.client_map = manager.dict()
        main_exe = Process(target=main_event_loop, args=(ap_service, client_service))
        data_exe = Process(target=refresh_data, args=(ap_service, client_service))

        main_exe.start()
        data_exe.start()

        main_exe.join()
        data_exe.join()

        while True:
            pass


if __name__ == "__main__":
    main()
