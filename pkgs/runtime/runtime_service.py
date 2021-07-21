import subprocess
import time
from pkgs.command.command_service import CommandService

socket_ip = "127.0.0.1"


class RuntimeService:

    def __init__(self):
        self.running = False

    @staticmethod
    def is_sniffer_running():
        pi_sniffer = subprocess.run(["ps", "-C", "pi_sniffer"], capture_output=True)
        if pi_sniffer.stdout.find(b"pi_sniffer") != -1:
            return True
        else:
            return False

    @staticmethod
    def is_kismet_running():
        kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
        if kismet.stdout.find(b"kismet_server") != -1:
            return True
        else:
            return False

    @staticmethod
    def start_sniffer():
        subprocess.Popen([
            "/home/pi/pi_sniffer/build/pi_sniffer",
            "-c", "/home/pi/pi_sniffer/pi_sniffer.conf",
            "-k",
            socket_ip,
            "-p",
            "3501"
        ])

    @staticmethod
    def start_kismet():
        subprocess.Popen(["kismet_server", "-f", "/home/pi/kismet.conf", "-n", "--daemonize"])
        time.sleep(3)  # give it a second to get established

    def set_running(self, running):
        self.running = running

    def start(self):
        # start kismet and pi sniffer
        if RuntimeService.is_kismet_running() is False:
            RuntimeService.start_kismet()

        if RuntimeService.is_sniffer_running() is False:
            RuntimeService.start_sniffer()

    def stop(self):
        # shutdown kismet and pi sniffer
        self.set_running(False)
        CommandService.run(b"s", False)
        kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
        if kismet.stdout.find(b"kismet_server") != -1:
            CommandService.do_kismet_command(b"SHUTDOWN")
            subprocess.run(["airmon-ng", "stop", "wlan0mon"])
            subprocess.run(["airmon-ng", "stop", "wlan1mon"])

    @staticmethod
    def power_off():
        # attempt a clean shutdown
        CommandService.run(b"s", False)
        time.sleep(5)
        subprocess.run(["shutdown", "-h", "now"])
