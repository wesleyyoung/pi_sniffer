import time
import subprocess

from pkgs.command.command_service import CommandService


class WatchdogService:

    def __init__(self):
        # observed some curious behavior from kismet. After many hours it sometimes
        # just stops sending data in the kismet packets. I'm 90% certain it isn't me.
        # who knows. Poor man's solution: watchdog that restarts kismet
        self.watch_dog = time.time()
        # flush output every five minutes just in case of catastrophic error
        self.flush_time = time.time()
        self.current_time = time.time()
        # last update time
        self.last_update = 0
        self.last_stats = None

    ##
    # Every 60 seconds check if kismet is still sending us data. I've observed it
    # sending us empty packets for some reason... If we observe that behavior just
    # restart it.
    #
    # Every 300 seconds tell pi_sniffer to flush output to disk.
    ##
    def do_watchdog(self):
        if (self.get_current_time() - 60) > self.watch_dog:
            self.watch_dog = self.current_time
            overview_stats = CommandService.run(b"o", True)
            if overview_stats is not None:
                stats = overview_stats.split(b",")
                if self.last_stats is None:
                    self.last_stats = stats[5]
                elif self.last_stats == stats[5]:
                    # we are either getting no data or kismet is behaving odd.
                    # knock it over and set it back up
                    self.last_stats = None
                    kismet = subprocess.run(["ps", "-C", "kismet_server"], capture_output=True)
                    if kismet.stdout.find(b"kismet_server") != -1:
                        CommandService.do_kismet_command(b"SHUTDOWN")
                        subprocess.run(["airmon-ng", "stop", "wlan0mon"])
                        subprocess.run(["airmon-ng", "stop", "wlan1mon"])
                        time.sleep(3)
                        subprocess.Popen(["kismet_server", "-f", "/home/pi/kismet.conf", "-n", "--daemonize"])
                else:
                    self.last_stats = stats[5]

        # let's check if we should flush output too
        if (self.get_current_time() - 300) > self.flush_time:
            self.flush_time = self.get_current_time()
            # only send the command if it's running
            pi_sniffer = subprocess.run(["ps", "-C", "pi_sniffer"], capture_output=True)
            if pi_sniffer.stdout.find(b"pi_sniffer") != -1:
                CommandService.run(b"f", False)

    def set_current_time(self, current_time):
        self.current_time = current_time

    def get_current_time(self):
        return self.current_time
