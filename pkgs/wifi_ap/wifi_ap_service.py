from multiprocessing import Manager
from pkgs.command.command_service import CommandService
from operator import itemgetter


class WifiApService:

    def __init__(self):
        with Manager() as manager:
            self.aps = manager.dict()

    def get(self, bssid):
        return self.aps[bssid]

    def get_ap_list(self):
        try:
            return itemgetter(*list(self.aps.keys()))(self.aps)
        except:
            return []

    def get_index(self, index):
        return self.get_ap_list()[index]

    def get_ap_list_from_socket(self):
        access_points = CommandService.run(b"l", True)
        if access_points is not None:
            ap_list = access_points.splitlines()
            return ap_list[:len(ap_list) - 1]
        return []

    async def get_ap_list_from_socket_async(self):
        access_points = await CommandService.run_async(b"l", True)
        if access_points is not None:
            ap_list = access_points.splitlines()
            return ap_list[:len(ap_list) - 1]
        return []

    def refresh_ap_list(self):
        aps = self.get_ap_list_from_socket()
        for ap in aps:
            info = ap.decode('utf-8').split(',')
            bssid = info[1].lower().strip()
            ap = {
                'bssid': bssid,
                'ssid': info[0]
            }
            
            ap = self.get_ap_info(ap)
            self.aps[bssid] = ap

    async def refresh_ap_list_async(self):
        aps = await self.get_ap_list_from_socket_async()
        for ap in aps:
            info = ap.decode('utf-8').split(',')
            bssid = info[1].lower().strip()
            ap = {
                'bssid': bssid,
                'ssid': info[0]
            }
            ap = self.get_ap_info(ap)
            self.aps[bssid] = ap

    def get_ap_by_bssid(self, bssid):
        bssid = str(bssid).lower().strip()
        try:
            return self.get(bssid)
        except Exception as e:
            return None

    def get_ap_info(self, ap):
        try:
            data = CommandService.run(b"r" + str.encode(ap['bssid']), True)
            if data is not None:
                split_info = data.split(b",")
                channel = split_info[0].decode("utf-8")
                security = split_info[1].decode("utf-8")
                rssi = split_info[2].decode("utf-8")
                client_count = split_info[3].decode("utf-8")
                return {
                    "channel": channel,
                    "security": security,
                    "rssi": rssi,
                    "bssid": ap['bssid'],
                    "ssid": ap['ssid'],
                    "client_count": client_count
                }
            return {}
        except Exception as e:
            return {}

    def get_ap_info_at_index(self, index=0):
        return self.get_ap_info(self.get_index(index))
