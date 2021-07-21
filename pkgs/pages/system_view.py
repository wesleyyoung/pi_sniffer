import subprocess
import re


def do_system_view(draw, font, width):
    draw.rectangle((0, 0, width, 10), outline=1, fill=1)
    draw.text(((width / 2) - 36, 0), "System Status", fill=0)

    cpu = subprocess.run(["top", "-b", "-n", "1"], capture_output=True)
    result = re.search(b"%Cpu\(s\):[ ]+[0-9\.]+[ ]+us,[ ]+[0-9\.]+[ ]+sy,[ ]+[0-9\.]+[ ]+ni,[ ]+([0-9\.]+)[ ]+id",
                       cpu.stdout)
    if result is None:
        draw.text((0, 10), "CPU: Unknown%", font=font, fill=1)
    else:
        value = 100 - int(float(result.group(1)))
        draw.text((0, 10), "CPU: " + str(value) + "%", font=font, fill=1)

    mem = subprocess.run(["vmstat", "-s"], capture_output=True)
    total_mem = re.search(b"([0-9]+) K total memory\n", mem.stdout)
    total_free = re.search(b"([0-9]+) K free memory\n", mem.stdout)
    if total_mem is None or total_free is None:
        draw.text((0, 20), "Memory: Unknown%", font=font, fill=1)
    else:
        value = 100 - ((float(total_free.group(1)) / float(total_mem.group(1))) * 100)
        draw.text((0, 20), "Memory: " + str(int(value)) + "%", font=font, fill=1)

    disk = subprocess.run(["df"], capture_output=True)
    disk_usage = re.search(b"/dev/root[ ]+[A-Z0-9\.]+[ ]+[A-Z0-9\.]+[ ]+[A-Z0-9\.]+[ ]+([0-9]+)% /", disk.stdout)
    if disk_usage is None:
        draw.text((0, 30), "Disk: Unknown%", font=font, fill=1)
    else:
        draw.text((0, 30), "Disk: " + disk_usage.group(1).decode("utf-8") + "%", font=font, fill=1)

    temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
    temp_C = re.search(b"temp=(.*)", temp.stdout)
    if temp_C is None:
        draw.text((0, 40), "Temp: Unknown", font=font, fill=1)
    else:
        draw.text((0, 40), "Temp: " + temp_C.group(1).decode("utf-8"), font=font, fill=1)
