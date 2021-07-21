import re
import subprocess

from pkgs.vendor.vendor_service import VendorService
from pkgs.command.command_service import CommandService
from operator import itemgetter
from multiprocessing import Manager


class WifiClientService:

    def __init__(self):
        with Manager() as manager:
            self.client_map = manager.dict()

    def deauth(self, mac, station_bssid, iface="wlan0mon"):
        subprocess.run(["aireplay-ng", "-0", "1", "-a", station_bssid, "-c", mac, iface])

    def deauth_client(self, client):
        station_bssid = client['station_bssid']
        mac = client['mac']
        if station_bssid is not None:
            self.deauth(mac, station_bssid)

    def deauth_at_index(self, index):
        client = self.get_index(index)
        self.deauth_client(client)

    def get_index(self, index=0):
        return self.get_clients()[index]

    def get(self, mac):
        return self.client_map[mac]

    def get_clients(self):
        try:
            return itemgetter(*list(self.client_map.keys()))(self.client_map)
        except:
            return []

    def get_clients_from_socket(self):
        try:
            return CommandService.run(b"c", True).splitlines()[:-1]
        except:
            return []

    def refresh_clients(self):
        clients = self.get_clients_from_socket()
        for client in clients:
            mac = client.decode("utf-8").lower().strip()
            self.client_map[mac] = self.get_client_info(client)

    def get_client_info(self, client):
        try:
            client = client.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            pass
        data = CommandService.run(b"c" + str.encode(client), True)
        mac = client.lower().strip()
        if data is not None:
            data = data.split(b",")
            return {
                'name': VendorService.get_display_name(mac),
                'mac': mac,
                'rssi': data[0].decode("utf-8"),
                'station_bssid': data[1].decode("utf-8")
            }

    def get_client_station_bssid(self, client):
        data = self.get_client_info(client)
        return data['station_bssid']

    def get_client_rssi(self, client):
        data = self.get_client_info(client)
        return data['rssi']
