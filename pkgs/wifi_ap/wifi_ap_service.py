from pkgs.command.command_service import CommandService


class WifiApService:
    ap_list = []

    def __init__(self):
        self.ap_list = []

    def get(self, index):
        return self.ap_list[index]

    def get_ap_list(self):
        return self.ap_list

    def get_ap_list_from_socket(self):
        access_points = CommandService.run(b"l", True)
        if access_points is not None:
            ap_list = access_points.splitlines()
            return ap_list[:len(ap_list) - 1]
        return []

    def refresh_ap_list(self):
        self.ap_list = self.get_ap_list_from_socket()

    def get_ap_info(self, ap):
        try:
            data = CommandService.run(b"r" + ap[1], True)
            bssid = ap[1].decode("utf-8")
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
                    "bssid": bssid,
                    "client_count": client_count
                }
            return {}
        except:
            return {}

    def get_ap_info_at_index(self, index=0):
        return self.get_ap_info(self.get(index))
