import subprocess
import re


def total_mem():
    raw_process = subprocess.run(["vmstat", "-s"], capture_output=True)
    return re.search(b"([0-9]+) K total memory\n", raw_process.stdout)


def mem_free():
    raw_process = subprocess.run(["vmstat", "-s"], capture_output=True)
    return re.search(b"([0-9]+) K free memory\n", raw_process.stdout)