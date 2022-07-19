import subprocess
import re


def temp():
    raw_process = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
    return re.search(b"temp=(.*)", raw_process.stdout)