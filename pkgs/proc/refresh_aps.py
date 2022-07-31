import time

from pkgs.runtime.runtime_service import RuntimeService
from pkgs.settings.settings_service import SettingsService
from pkgs.wifi_ap.wifi_ap_service import WifiApService


def refresh_aps(runtime_service: RuntimeService, settings_service: SettingsService, ap_service: WifiApService):
    while True:
        try:
            if runtime_service.is_sniffer_running():
                ap_service.refresh_ap_list()
            else:
                pass
        except Exception as e:
            pass

        time.sleep(settings_service.get_data_rate())