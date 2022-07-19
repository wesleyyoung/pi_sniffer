import subprocess
import re


def disk_usage():
    raw_process = subprocess.run(["df"], capture_output=True)
    return re.search(b"/dev/root[ ]+[A-Z0-9\.]+[ ]+[A-Z0-9\.]+[ ]+[A-Z0-9\.]+[ ]+([0-9]+)% /", raw_process.stdout)