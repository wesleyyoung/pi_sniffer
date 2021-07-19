import subprocess
import socket
import re


def create_udp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


socket_ip = "127.0.0.1"
socket_port = 1270
backend_sock = create_udp_socket()


class CommandService:
    ##
    # Issue a command to the pi sniffer UDP interface. Not all commands require
    # responses (e.g. 'S\n' for shutdown does not require a response)
    ##
    @staticmethod
    def run(command, get_response):
        data = None

        pi_sniffer = subprocess.run(["ps", "-C", "pi_sniffer"], capture_output=True)
        if pi_sniffer.stdout.find(b"pi_sniffer") != -1:
            backend_sock.sendto(command + b"\n", (socket_ip, 1270))
            if get_response is True:
                data = backend_sock.recvfrom(65535)[0]

        return data

    ##
    # Issue a generic kismet command (e.g. shutdown) and return
    ##
    @staticmethod
    def do_kismet_command(command):
        s = create_udp_socket()
        s.connect((socket_ip, 2501))
        s.sendall(b"!0 " + command + b"\n")
        s.close()

    ##
    # Grab the current channel list, hop status, and current channel for the
    # provided antenna (uuid defined in kismet.conf. wlan0 == 01 and wlan1 == 02)
    ##
    @staticmethod
    def kismet_ant_info(uuid):
        s = create_udp_socket()
        s.connect((socket_ip, 2501))
        s.sendall(b"!0 ENABLE SOURCE uuid,channellist,hop,channel\n")
        data = b""

        try:
            data = s.recv(1024)
            s.close()
        except:
            pass

        channel_info = re.search(b"SOURCE: " + uuid + b" ([0-9,]+) ([0-9]+) ([0-9]+)", data)
        if channel_info is None:
            return b'', b'', b''
        else:
            # channel list, hop status, current channel
            return channel_info.group(1), channel_info.group(2), channel_info.group(3)

    ##
    # Set the channel of the provided antenna (uuid defined in kismet.conf). If
    # the provided channel == "0" than switch to channel hopping.
    ##
    @staticmethod
    def kismet_set_channel(uuid, channel):
        s = create_udp_socket()
        s.connect((socket_ip, 2501))
        if channel == b"0":
            s.sendall(b"!0 HOPSOURCE " + uuid + b" HOP 3\n")
        else:
            s.sendall(b"!0 HOPSOURCE " + uuid + b" LOCK " + channel + b"\n")
        s.close()
