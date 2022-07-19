from multiprocessing import Process, Manager
import time
import subprocess
from PIL import Image, ImageDraw

from pkgs.driver.adafruit_1_3_bonnet import Adafruit13Bonnet
from pkgs.settings.settings_service import SettingsService
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
# Globals
###

# Display Driver
driver = Adafruit13Bonnet()

# Socket endpoint address
socket_ip = "127.0.0.1"

disp = driver.get_display()

# Input pins
button_A = driver.get_button_a()
button_B = driver.get_button_b()
button_L = driver.get_button_l()
button_R = driver.get_button_r()
button_U = driver.get_button_u()
button_D = driver.get_button_d()
button_C = driver.get_button_c()

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

width = driver.get_display_width()
height = driver.get_display_height()
image = driver.create_image()
draw = driver.create_drawable(image)

# current view
current_view = status_view

# lock controls
locked = False

# last update time
last_update = 0
last_stats = None

# the font all text writing will use
font = driver.get_font()

##
# Services
##
runtime_service = RuntimeService()
watchdog_service = WatchdogService()

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


def refresh_aps(settings_service, ap_service):
    while True:
        try:
            if runtime_service.is_sniffer_running():
                ap_service.refresh_ap_list()
            else:
                pass
        except Exception as e:
            pass

        time.sleep(settings_service.get_data_rate())


def refresh_clients(settings_service, client_service):
    while True:
        try:
            if runtime_service.is_sniffer_running():
                client_service.refresh_clients()
            else:
                pass
        except Exception as e:
            pass

        time.sleep(settings_service.get_data_rate())


def is_no_input_given():
    return button_A.value and button_B.value and button_U.value and button_D.value and button_L.value and button_R.value


def main_event_loop(settings_service, ap_service, client_service):
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
            if (time.time() * 1000) - (last_update * 1000) <= settings_service.get_refresh_rate():
                continue

        # check if the user is changing the view
        check_view()

        # see if we should be refreshing
        watchdog_service.set_current_time(time.time())
        if (watchdog_service.get_current_time() - 6) > last_update:
            watchdog_service.do_watchdog()

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
        driver.draw_blank_canvas()

        time.sleep(0.01)


def main():
    # ensure the echo is disabled on the gps tty. Really annoying this needs to be done.
    subprocess.run(["stty", "-F", "/dev/ttyACM0", "-echo"])

    # kill hdmi. power saving.
    subprocess.run(["/usr/bin/tvservice", "-o"])

    # Clear display. Twice
    driver.clear_display()
    driver.clear_display()

    with Manager() as manager:
        client_service = WifiClientService()
        ap_service = WifiApService()
        ap_service.aps = manager.dict()
        client_service.client_map = manager.dict()
        settings_service = SettingsService()
        settings_service.settings = manager.dict()
        settings_service.set_defaults()
        processes = [
            Process(target=main_event_loop, args=(settings_service, ap_service, client_service)),
            Process(target=refresh_aps, args=(settings_service, ap_service, )),
            Process(target=refresh_clients, args=(settings_service, client_service, )),
        ]

        for proc in processes:
            time.sleep(.3)
            proc.start()

        for proc in processes:
            time.sleep(.3)
            proc.join()

        while True:
            pass


if __name__ == "__main__":
    main()
