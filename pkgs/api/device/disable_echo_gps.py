import subprocess


def disable_echo_gps():
    subprocess.run(["stty", "-F", "/dev/ttyACM0", "-echo"])