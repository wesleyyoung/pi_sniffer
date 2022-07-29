import subprocess


def kill_hdmi():
    subprocess.run(["/usr/bin/tvservice", "-o"])