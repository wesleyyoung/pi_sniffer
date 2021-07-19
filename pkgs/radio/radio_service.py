import subprocess

from pkgs.command.command_service import CommandService


class RadioService:
    def __init__(self):
        self.foo = ""

    @staticmethod
    def is_antenna_running(iface):
        ant = subprocess.run(["ifconfig", iface], capture_output=True)
        return ant.stdout.find(b"RUNNING,PROMISC") is not -1

    @staticmethod
    def set_channel(uid, channel):
        CommandService.kismet_set_channel(uid, channel)

    @staticmethod
    def antenna_info(uid):
        return CommandService.kismet_ant_info(uid)

    @staticmethod
    def cycle_channel(uid, mod):
        (channellist, hopping, channel) = RadioService.antenna_info(uid)
        channels = channellist.split(b",")
        if len(channels) > 0:
            if hopping != b"0":
                RadioService.set_channel(uid, channels[0])
            else:
                current = channels.index(channel)
                current = current + mod
                if current >= len(channels):
                    RadioService.set_channel(uid, b"0")
                else:
                    RadioService.set_channel(uid, channels[current])

    @staticmethod
    def cycle_channel_up(uid):
        RadioService.cycle_channel(uid, 1)

    @staticmethod
    def cycle_channel_down(uid):
        RadioService.cycle_channel(uid, -1)

    @staticmethod
    def get_uid(iface):
        # Hardcode these values for now
        if iface == "wlan0mon":
            return b"00000000-0000-0000-0000-000000000001"
        elif iface == "wlan1mon":
            return b"00000000-0000-0000-0000-000000000002"
        else:
            return None
