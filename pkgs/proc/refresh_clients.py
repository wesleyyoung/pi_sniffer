import time

from pkgs.runtime.runtime_service import RuntimeService
from pkgs.settings.settings_service import SettingsService
from pkgs.wifi_client.wifi_client_service import WifiClientService


def refresh_clients(runtime_service: RuntimeService, settings_service: SettingsService, client_service: WifiClientService):
    while True:
        try:
            if runtime_service.is_sniffer_running():
                client_service.refresh_clients()
            else:
                pass
        except Exception as e:
            pass

        time.sleep(settings_service.get_data_rate())