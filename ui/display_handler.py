from multiprocessing import Process, Manager
import time

from pkgs.api.device.disable_echo_gps import disable_echo_gps
from pkgs.api.device.kill_hdmi import kill_hdmi
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

# current view
current_view = status_view

# lock controls
locked = False

# last update time
last_update = 0
last_stats = None

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
    if driver.is_right_pressed():
        # move to the next screen
        current_view = current_view + 1
        current_view = current_view % rotate

    # Left joystick controls screen movement too
    elif driver.is_left_pressed():
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
    return not driver.is_a_pressed() and not driver.is_b_pressed() \
           and not driver.is_up_pressed() and not driver.is_down_pressed() \
           and not driver.is_left_pressed() and not driver.is_right_pressed()


def main_event_loop(settings_service, ap_service, client_service):
    global last_update
    global locked
    global driver
    while True:
        if locked:
            # the user can lock the display in the lock screen. If they have, don't
            # do any other UI processing. We will have to still do the watch dog
            # logic though
            if driver.is_a_pressed() and driver.is_up_pressed():
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

        driver.set_blank_canvas()

        try:
            # which view to draw to the screen
            if current_view == status_view:
                if not do_status_view(driver, runtime_service):
                    # user has requested shutdown
                    break
            elif current_view == overview:
                do_overview(driver)
            elif current_view == antenna:
                do_ant_view(driver)
            elif current_view == system_view:
                do_system_view(driver)
            elif current_view == gps_view:
                do_gps_view(driver)
            elif current_view == client_view:
                do_client_view(driver, ap_service, client_service)
            elif current_view == ap_view:
                do_ap_view(driver, ap_service)
            elif current_view == lock_screen:
                do_lock_screen(driver)
            else:
                print("oh no! Why are we here?")
        except Exception as e:
            print('Error displaying page', e)

        last_update = time.time()
        driver.show()

        time.sleep(0.01)


def main():
    # ensure the echo is disabled on the gps tty. Really annoying this needs to be done.
    disable_echo_gps()

    # kill hdmi. power saving.
    kill_hdmi()

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
            Process(target=refresh_aps, args=(settings_service, ap_service,)),
            Process(target=refresh_clients, args=(settings_service, client_service,)),
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
