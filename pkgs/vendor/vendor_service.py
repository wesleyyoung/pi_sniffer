import re
from pkgs.mac.mac_vendor_lookup import MacLookup

mac_tool = MacLookup()


class VendorService:
    @staticmethod
    def get_vendor(mac):
        try:
            return mac_tool.lookup(mac)
        except:
            return None

    @staticmethod
    def get_display_name(mac):
        vendor = VendorService.get_vendor(mac)
        return VendorService.create_display_name(mac, vendor)

    @staticmethod
    def create_display_name(mac, vendor):
        if vendor is not None:
            vendor = re.sub(r'\W+', '', vendor)
            vendor_prefix = vendor[0:8]
            while len(vendor_prefix) < 9:
                vendor_prefix += ':'
            mac_suffix = mac[9:]
            return vendor_prefix + mac_suffix
        else:
            return mac
