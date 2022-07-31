import time

from pkgs.display.is_no_input_given import is_no_input_given
from pkgs.driver.display_driver import DisplayDriver
from pkgs.runtime.runtime_service import RuntimeService
from pkgs.settings.settings_service import SettingsService
from pkgs.watchdog.watchdog_service import WatchdogService
from pkgs.wifi_client.wifi_client_service import WifiClientService
from pkgs.wifi_ap.wifi_ap_service import WifiApService
from pkgs.pages.system_view import do_system_view
from pkgs.pages.status_view import do_status_view
from pkgs.pages.overview_view import do_overview
from pkgs.pages.ant_view import do_ant_view
from pkgs.pages.gps_view import do_gps_view
from pkgs.pages.client_view import do_client_view
from pkgs.pages.ap_view import do_ap_view
from pkgs.pages.lock_view import do_lock_screen

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


def check_view_update_request(display_driver: DisplayDriver):
    global current_view

    # Right joystick controls screen movement
    if display_driver.is_right_pressed():
        # move to the next screen
        current_view = current_view + 1
        current_view = current_view % rotate

    # Left joystick controls screen movement too
    elif display_driver.is_left_pressed():
        if current_view == 0:
            current_view = lock_screen
        else:
            current_view = current_view - 1


def ui_event_loop(watchdog_service: WatchdogService, runtime_service: RuntimeService,
                  settings_service: SettingsService, display_driver: DisplayDriver,
                  ap_service: WifiApService, client_service: WifiClientService):
    global last_update
    global locked
    while True:
        if locked:
            # the user can lock the display in the lock screen. If they have, don't
            # do any other UI processing. We will have to still do the watch dog
            # logic though
            if display_driver.is_a_pressed() and display_driver.is_up_pressed():
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
        check_view_update_request()

        # see if we should be refreshing
        watchdog_service.set_current_time(time.time())
        if (watchdog_service.get_current_time() - 6) > last_update:
            watchdog_service.do_watchdog()

        display_driver.set_blank_canvas()

        try:
            # which view to draw to the screen
            if current_view == status_view:
                if not do_status_view(display_driver, runtime_service):
                    # user has requested shutdown
                    break
            elif current_view == overview:
                do_overview(display_driver)
            elif current_view == antenna:
                do_ant_view(display_driver)
            elif current_view == system_view:
                do_system_view(display_driver)
            elif current_view == gps_view:
                do_gps_view(display_driver)
            elif current_view == client_view:
                do_client_view(display_driver, ap_service, client_service)
            elif current_view == ap_view:
                do_ap_view(display_driver, ap_service)
            elif current_view == lock_screen:
                do_lock_screen(display_driver)
            else:
                print("oh no! Why are we here?")
        except Exception as e:
            print('Error displaying page', e)

        last_update = time.time()
        display_driver.show()

        time.sleep(0.01)
