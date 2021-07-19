import re
import subprocess

from pkgs.mac.mac_vendor_lookup import MacLookup
from pkgs.command.command_service import CommandService


class WifiClientService:
    clients = []
    mac_tool = MacLookup()

    def __init__(self):
        self.clients = []

    def deauth(self, mac, station_bssid, iface="wlan0mon"):
        subprocess.run(["aireplay-ng", "-0", "1", "-a", station_bssid, "-c", mac, iface])

    def deauth_client(self, client):
        station_bssid = self.get_client_station_bssid(client)
        mac = client.decode("utf-8")
        if station_bssid is not None:
            self.deauth(mac, station_bssid)

    def deauth_at_index(self, index):
        client = self.get(index)
        self.deauth_client(client)

    def get(self, index=0):
        return self.clients[index]

    def get_clients(self):
        return self.clients

    def get_clients_from_socket(self):
        clients_raw = CommandService.run(b"c", True)
        if clients_raw is not None:
            clients = clients_raw.splitlines()
            return clients[:len(clients) - 1]
        else:
            return []

    def refresh_clients(self):
        self.clients = self.get_clients_from_socket()

    def get_client_info(self, client):
        data = CommandService.run(b"c" + client, True)
        return_array = []
        if data is not None:
            for datum in data.split(b","):
                return_array.append(datum.decode("utf-8"))

        return return_array

    def get_client_station_bssid(self, client):
        data = self.get_client_info(client)
        return data[1]

    def get_client_rssi(self, client):
        data = self.get_client_info(client)
        return data[0]

    def get_client_vendor(self, mac):
        try:
            return self.mac_tool.lookup(mac)
        except:
            return None

    def get_client_display_name(self, mac):
        vendor = self.get_client_vendor(mac)
        if vendor is not None:
            vendor = re.sub(r'\W+', '', vendor)
            vendor_prefix = vendor[0:8]
            while len(vendor_prefix) < 9:
                vendor_prefix += ':'
            mac_suffix = mac[9:]
            return vendor_prefix + mac_suffix
        else:
            return mac
