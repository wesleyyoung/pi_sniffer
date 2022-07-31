from multiprocessing import Process, Manager
import time

from pkgs.api.device.disable_echo_gps import disable_echo_gps
from pkgs.api.device.kill_hdmi import kill_hdmi
from pkgs.driver.adafruit_1_3_bonnet import Adafruit13Bonnet
from pkgs.proc.refresh_aps import refresh_aps
from pkgs.proc.refresh_clients import refresh_clients
from pkgs.proc.ui import ui_event_loop
from pkgs.settings.settings_service import SettingsService
from pkgs.wifi_client.wifi_client_service import WifiClientService
from pkgs.wifi_ap.wifi_ap_service import WifiApService
from pkgs.watchdog.watchdog_service import WatchdogService
from pkgs.runtime.runtime_service import RuntimeService


def main():
    # ensure the echo is disabled on the gps tty. Really annoying this needs to be done.
    disable_echo_gps()

    # kill hdmi. power saving.
    kill_hdmi()

    # Display Driver
    display_driver = Adafruit13Bonnet()

    # Clear display. Twice
    display_driver.clear_display()
    display_driver.clear_display()

    with Manager() as manager:
        ##
        # Services
        ##
        runtime_service = RuntimeService()
        watchdog_service = WatchdogService()
        client_service = WifiClientService()
        ap_service = WifiApService()
        ap_service.aps = manager.dict()
        client_service.client_map = manager.dict()
        settings_service = SettingsService()

        settings_service.settings = manager.dict()
        settings_service.set_defaults()

        processes = [
            Process(target=ui_event_loop, args=(watchdog_service, runtime_service, settings_service,
                                                display_driver, ap_service, client_service)),
            Process(target=refresh_aps, args=(runtime_service, settings_service, ap_service,)),
            Process(target=refresh_clients, args=(runtime_service, settings_service, client_service,)),
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
