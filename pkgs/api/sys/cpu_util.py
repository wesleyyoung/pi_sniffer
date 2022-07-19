import subprocess
import re


def cpu_util():
    raw_process = subprocess.run(["top", "-b", "-n", "1"], capture_output=True)
    return re.search(b"%Cpu\(s\):[ ]+[0-9\.]+[ ]+us,[ ]+[0-9\.]+[ ]+sy,[ ]+[0-9\.]+[ ]+ni,[ ]+([0-9\.]+)[ ]+id",
                     raw_process.stdout)
